from __future__ import annotations

from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.external.gateway import ExternalAuthorizationError


def _app(tmp_path: Path) -> AthenaApplication:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path / "runtime")
    )
    app.start()
    return app


def test_authorization_reader_rejects_text_actor_identity_even_at_valid_length(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    try:
        authorization = app.external_access.authorize_explicit(
            purpose="persisted identity boundary",
            allowed_hosts=("example.com",),
        )
        connection = app.database.connection
        assert int(connection.execute("PRAGMA foreign_keys").fetchone()[0]) == 1

        connection.execute("PRAGMA foreign_keys = OFF")
        try:
            with app.database.write_transaction() as transaction:
                transaction.execute(
                    """
                    UPDATE external_access_authorizations
                    SET actor_id = ?
                    WHERE authorization_id = ?
                    """,
                    ("x" * 16, authorization.authorization_id.bytes),
                )
        finally:
            connection.execute("PRAGMA foreign_keys = ON")

        with pytest.raises(
            ExternalAuthorizationError,
            match="actor_id",
        ):
            app.external_access.get_authorization(
                authorization.authorization_id
            )
    finally:
        app.stop()


def test_authorization_reader_rejects_noncanonical_persisted_host_scope(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    try:
        authorization = app.external_access.authorize_explicit(
            purpose="persisted host boundary",
            allowed_hosts=("example.com",),
        )

        with app.database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE external_access_authorizations
                SET allowed_hosts_json = ?
                WHERE authorization_id = ?
                """,
                ('["EXAMPLE.com"]', authorization.authorization_id.bytes),
            )

        with pytest.raises(
            ExternalAuthorizationError,
            match="non-canonical",
        ):
            app.external_access.get_authorization(
                authorization.authorization_id
            )
    finally:
        app.stop()


def test_authorization_reader_preserves_valid_record(tmp_path: Path) -> None:
    app = _app(tmp_path)
    try:
        authorization = app.external_access.authorize_explicit(
            purpose=" valid persisted record ",
            allowed_hosts=("EXAMPLE.com.", "openai.com"),
            privacy_route="tor_preferred",
            ttl_seconds=60,
        )

        loaded = app.external_access.get_authorization(
            authorization.authorization_id
        )

        assert loaded == authorization
        assert loaded.purpose == "valid persisted record"
        assert loaded.allowed_hosts_json == '["example.com","openai.com"]'
    finally:
        app.stop()
