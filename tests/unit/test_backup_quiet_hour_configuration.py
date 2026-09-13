import pytest

from athena.config.settings import AthenaSettings, ConfigurationError
from athena.core.application import AthenaApplication


def test_backup_quiet_hour_defaults_to_three_utc(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(tmp_path))
    monkeypatch.delenv("ATHENA_BACKUP_QUIET_HOUR_UTC", raising=False)

    settings = AthenaSettings.from_environment()

    assert settings.backup_quiet_hour_utc == 3


def test_backup_quiet_hour_reads_environment(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(tmp_path))
    monkeypatch.setenv("ATHENA_BACKUP_QUIET_HOUR_UTC", "17")

    settings = AthenaSettings.from_environment()

    assert settings.backup_quiet_hour_utc == 17


@pytest.mark.parametrize("value", ["-1", "24", "3.5", "not-an-hour"])
def test_backup_quiet_hour_rejects_invalid_environment(
    tmp_path,
    monkeypatch,
    value,
) -> None:
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(tmp_path))
    monkeypatch.setenv("ATHENA_BACKUP_QUIET_HOUR_UTC", value)

    with pytest.raises(ConfigurationError, match="integer between 0 and 23"):
        AthenaSettings.from_environment()


@pytest.mark.parametrize("value", [-1, 24, True, False, 3.5])
def test_backup_quiet_hour_rejects_invalid_direct_values(tmp_path, value) -> None:
    with pytest.raises(ConfigurationError, match="integer between 0 and 23"):
        AthenaSettings(
            local_root=tmp_path,
            backup_quiet_hour_utc=value,
        )


def test_application_wires_backup_quiet_hour_into_worker(tmp_path) -> None:
    settings = AthenaSettings(
        local_root=tmp_path,
        backup_quiet_hour_utc=19,
    )

    application = AthenaApplication(settings=settings)

    assert application.backup_worker.quiet_hour_utc == 19
