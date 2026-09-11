from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_spec.py"


@pytest.fixture(scope="module")
def resolve_repository_link() -> Callable[..., Path | None]:
    namespace = runpy.run_path(str(SCRIPT))
    resolver = namespace["resolve_repository_link"]
    assert callable(resolver)
    return resolver


def test_in_repository_relative_link_is_allowed(
    tmp_path: Path,
    resolve_repository_link: Callable[..., Path | None],
) -> None:
    root = tmp_path / "repo"
    source = root / "docs" / "INDEX.md"
    target = root / "README.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Index\n", encoding="utf-8")
    target.write_text("# Root\n", encoding="utf-8")

    resolved = resolve_repository_link(source, "../README.md", root=root)

    assert resolved == target.resolve()


def test_existing_parent_traversal_outside_repository_is_rejected(
    tmp_path: Path,
    resolve_repository_link: Callable[..., Path | None],
) -> None:
    root = tmp_path / "repo"
    source = root / "docs" / "INDEX.md"
    outside = tmp_path / "outside.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Index\n", encoding="utf-8")
    outside.write_text("# Outside\n", encoding="utf-8")

    resolved = resolve_repository_link(source, "../../outside.md", root=root)

    assert resolved is None


def test_symlink_to_existing_file_outside_repository_is_rejected(
    tmp_path: Path,
    resolve_repository_link: Callable[..., Path | None],
) -> None:
    root = tmp_path / "repo"
    source = root / "docs" / "INDEX.md"
    outside = tmp_path / "outside.md"
    link = root / "docs" / "external.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Index\n", encoding="utf-8")
    outside.write_text("# Outside\n", encoding="utf-8")
    try:
        link.symlink_to(outside)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable on this host: {exc}")

    resolved = resolve_repository_link(source, "external.md", root=root)

    assert resolved is None


def test_missing_in_repository_target_remains_a_local_destination(
    tmp_path: Path,
    resolve_repository_link: Callable[..., Path | None],
) -> None:
    root = tmp_path / "repo"
    source = root / "docs" / "INDEX.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Index\n", encoding="utf-8")

    resolved = resolve_repository_link(source, "missing.md", root=root)

    assert resolved == (source.parent / "missing.md").resolve()
    assert not resolved.exists()
