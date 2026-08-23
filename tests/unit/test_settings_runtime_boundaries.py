from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from athena.config.settings import AthenaSettings, ConfigurationError


@pytest.mark.parametrize(
    "kwargs",
    [
        {"log_level": 20},
        {"local_root": "/tmp/athena"},
        {"archive_root": "/tmp/archive"},
        {"backup_root": 1},
        {"projection_root": True},
        {"lm_studio_base_url": 1234},
    ],
)
def test_settings_reject_wrong_runtime_types(kwargs: dict[str, Any]) -> None:
    defaults: dict[str, Any] = {"local_root": Path("/tmp/athena")}
    defaults.update(kwargs)

    with pytest.raises(ConfigurationError):
        AthenaSettings(**defaults)


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:notaport",
        "http://127.0.0.1:99999",
        "http://[::1]:0",
    ],
)
def test_settings_reject_invalid_lm_studio_ports(url: str) -> None:
    with pytest.raises(ConfigurationError):
        AthenaSettings(
            local_root=Path("/tmp/athena"),
            lm_studio_base_url=url,
        )


def test_settings_accept_local_ipv6_with_valid_port() -> None:
    settings = AthenaSettings(
        local_root=Path("/tmp/athena"),
        lm_studio_base_url="http://[::1]:1234/",
    )

    assert settings.lm_studio_base_url == "http://[::1]:1234"


def test_settings_normalize_log_level_without_changing_path_identity() -> None:
    root = Path("/tmp/athena")
    settings = AthenaSettings(local_root=root, log_level=" debug ")

    assert settings.log_level == "DEBUG"
    assert settings.local_root == root
