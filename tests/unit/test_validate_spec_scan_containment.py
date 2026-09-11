from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_spec.py"
ScanCollector = Callable[..., tuple[list[Path], list[Path], list[str]]]


@pytest.fixture(scope="module")
def collect_repository_scan_files() -> ScanCollector:
    namespace = runpy.run_path(str(SCRIPT))
    collector = namespace["collect_repository_scan_files"]
    assert callable(collector)
    return collector


def _make_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable on this host: {exc}")


def test_regular_repository_markdown_is_collected(
    tmp_path: Path,
    collect_repository_scan_files: ScanCollector,
) -> None:
    root = tmp_path / "repo"
    document = root / "docs" / "safe.md"
    document.parent.mkdir(parents=True)
    document.write_text("# Safe\n", encoding="utf-8")

    all_files, markdown_files, unsafe_inputs = collect_repository_scan_files(root=root)

    assert document in all_files
    assert document in markdown_files
    assert unsafe_inputs == []


def test_external_markdown_symlink_is_reported_and_never_collected(
    tmp_path: Path,
    collect_repository_scan_files: ScanCollector,
) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    safe = docs / "safe.md"
    safe.write_text("# Safe\n", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("# External host content\n", encoding="utf-8")
    external_link = docs / "external.md"
    _make_symlink(external_link, outside)

    all_files, markdown_files, unsafe_inputs = collect_repository_scan_files(root=root)

    assert safe in all_files
    assert safe in markdown_files
    assert external_link not in all_files
    assert external_link not in markdown_files
    assert unsafe_inputs == ["docs/external.md"]


def test_missing_external_symlink_target_still_fails_closed(
    tmp_path: Path,
    collect_repository_scan_files: ScanCollector,
) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    external_link = docs / "missing-external.md"
    _make_symlink(external_link, tmp_path / "not-created.md")

    all_files, markdown_files, unsafe_inputs = collect_repository_scan_files(root=root)

    assert external_link not in all_files
    assert external_link not in markdown_files
    assert unsafe_inputs == ["docs/missing-external.md"]


def test_in_repository_symlink_target_is_allowed_without_escape(
    tmp_path: Path,
    collect_repository_scan_files: ScanCollector,
) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    target = docs / "target.md"
    target.write_text("# Target\n", encoding="utf-8")
    alias = docs / "alias.md"
    _make_symlink(alias, target)

    all_files, markdown_files, unsafe_inputs = collect_repository_scan_files(root=root)

    assert target in all_files
    assert alias in all_files
    assert target in markdown_files
    assert alias in markdown_files
    assert unsafe_inputs == []


def test_ignored_scan_root_does_not_turn_external_symlink_into_evidence(
    tmp_path: Path,
    collect_repository_scan_files: ScanCollector,
) -> None:
    root = tmp_path / "repo"
    ignored = root / ".venv"
    ignored.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    external_link = ignored / "external.md"
    _make_symlink(external_link, outside)

    all_files, markdown_files, unsafe_inputs = collect_repository_scan_files(root=root)

    assert external_link not in all_files
    assert external_link not in markdown_files
    assert unsafe_inputs == []
