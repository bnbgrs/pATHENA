from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WINDOWS_COMMON = REPO_ROOT / "scripts" / "windows_common.ps1"


def test_windows_settings_file_is_parsed_as_data_not_executed() -> None:
    source = WINDOWS_COMMON.read_text(encoding="utf-8")

    assert ". $settingsPath" not in source
    assert "ConvertFrom-PathenaSettingsLiteral" in source
    assert "Unsupported pATHENA Windows setting" in source
    assert "Duplicate pATHENA Windows setting" in source
    assert "'$env:ATHENA_LOCAL_ROOT' = 'ATHENA_LOCAL_ROOT'" in source
    assert "'$env:ATHENA_LMSTUDIO_BASE_URL' = 'ATHENA_LMSTUDIO_BASE_URL'" in source


def test_windows_settings_writer_marks_file_as_data_only() -> None:
    source = WINDOWS_COMMON.read_text(encoding="utf-8")

    assert "Data-only file: windows_common.ps1 parses this strictly and never executes it." in source
