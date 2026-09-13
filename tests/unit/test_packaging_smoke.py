from importlib import metadata

import pytest

from athena.packaging_smoke import check_distribution_metadata, main, run_packaging_smoke


def test_packaging_smoke_reports_required_distribution_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(metadata, "version", lambda name: "6.12.2" if name == "pypdf" else "")

    report = run_packaging_smoke()

    assert report.ready is True
    assert report.checks[0].distribution == "pypdf"
    assert report.checks[0].status == "PASS"
    assert report.checks[0].detail == "pypdf 6.12.2"


def test_packaging_smoke_fails_closed_when_pypdf_metadata_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing(name: str) -> str:
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(metadata, "version", missing)

    report = run_packaging_smoke()

    assert report.ready is False
    assert report.checks[0].status == "FAIL"
    assert report.checks[0].detail == "pypdf distribution metadata is unavailable"


def test_packaging_smoke_cli_returns_failure_for_missing_metadata(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def missing(name: str) -> str:
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(metadata, "version", missing)

    assert main(("--json",)) == 2
    output = capsys.readouterr().out
    assert '"ready": false' in output
    assert '"distribution": "pypdf"' in output


def test_packaging_smoke_rejects_noncanonical_distribution_name() -> None:
    with pytest.raises(ValueError, match="canonical trimmed text"):
        check_distribution_metadata(" pypdf")
