from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_spec.py"
RepositoryReader = Callable[..., str]


@pytest.fixture(scope="module")
def repository_reader() -> RepositoryReader:
    namespace = runpy.run_path(str(SCRIPT))
    reader = namespace["read_text"]
    assert callable(reader)
    return reader


def _make_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable on this host: {exc}")


def test_repository_reader_accepts_real_target_inside_root(
    tmp_path: Path,
    repository_reader: RepositoryReader,
) -> None:
    root = tmp_path / "repo"
    document = root / "docs" / "safe.md"
    document.parent.mkdir(parents=True)
    document.write_text("# Safe\n", encoding="utf-8")

    assert repository_reader(document, root=root) == "# Safe\n"


def test_repository_reader_refuses_external_symlink_before_reading(
    tmp_path: Path,
    repository_reader: RepositoryReader,
) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_text("host-only sentinel", encoding="utf-8")
    external_link = docs / "external.md"
    _make_symlink(external_link, outside)

    with pytest.raises(ValueError, match="outside root"):
        repository_reader(external_link, root=root)
