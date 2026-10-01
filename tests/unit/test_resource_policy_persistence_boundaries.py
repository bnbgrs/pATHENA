from __future__ import annotations

from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.resources.manager import ResourceMode


def _started_app(tmp_path: Path, name: str) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / name))
    app.start(run_startup_maintenance=False)
    return app


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ram_headroom_bytes", 0.5),
        ("disk_headroom_bytes", 0.5),
        ("updated_at_us", 0.5),
    ],
)
def test_policy_rejects_fractional_values_in_integer_fields(
    tmp_path: Path,
    field: str,
    value: float,
) -> None:
    app = _started_app(tmp_path, f"fractional-{field}")
    try:
        with app.database.write_transaction() as connection:
            connection.execute(
                f"UPDATE resource_policy SET {field} = ? WHERE singleton_id = 1",
                (value,),
            )

        with pytest.raises(RuntimeError, match=field):
            app.resources.policy()
    finally:
        app.stop()


def test_policy_rejects_text_actor_blob_even_at_valid_length(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path, "actor-storage-type")
    connection = app.database.connection
    try:
        actor_id = app.chat.ensure_local_user()
        app.resources.set_mode(ResourceMode.QUIET)
        assert app.resources.policy().updated_by_actor_id == actor_id

        connection.execute("PRAGMA foreign_keys = OFF")
        try:
            with app.database.write_transaction() as transaction:
                transaction.execute(
                    """
                    UPDATE resource_policy
                    SET updated_by_actor_id = ?
                    WHERE singleton_id = 1
                    """,
                    ("x" * 16,),
                )
        finally:
            connection.execute("PRAGMA foreign_keys = ON")

        with pytest.raises(RuntimeError, match="updated_by_actor_id"):
            app.resources.policy()
    finally:
        app.stop()


def test_policy_preserves_valid_persisted_values(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path, "valid-policy")
    try:
        actor_id = app.chat.ensure_local_user()
        policy = app.resources.set_mode(ResourceMode.PERFORMANCE)

        assert policy.mode is ResourceMode.PERFORMANCE
        assert policy.ram_headroom_bytes >= 0
        assert policy.disk_headroom_bytes >= 0
        assert 0.0 <= policy.gpu_background_threshold <= 1.0
        assert policy.updated_at_us >= 0
        assert policy.updated_by_actor_id == actor_id
    finally:
        app.stop()
