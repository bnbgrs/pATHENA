from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_spec.py"


@pytest.fixture(scope="module")
def validator_namespace() -> dict[str, object]:
    return runpy.run_path(str(SCRIPT))


@pytest.fixture(scope="module")
def resolve_repository_link(
    validator_namespace: dict[str, object],
) -> Callable[..., Path | None]:
    resolver = validator_namespace["resolve_repository_link"]
    assert callable(resolver)
    return resolver


@pytest.fixture(scope="module")
def included_in_repository_scan(
    validator_namespace: dict[str, object],
) -> Callable[..., bool]:
    predicate = validator_namespace["included_in_repository_scan"]
    assert callable(predicate)
    return predicate


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


def test_repository_scan_rejects_lexically_external_path(
    tmp_path: Path,
    included_in_repository_scan: Callable[..., bool],
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")

    assert not included_in_repository_scan(outside, root=root)


def test_repository_scan_rejects_symlink_resolving_outside_root(
    tmp_path: Path,
    included_in_repository_scan: Callable[..., bool],
) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    link = docs / "external.md"
    try:
        link.symlink_to(outside)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable on this host: {exc}")

    assert not included_in_repository_scan(link, root=root)


def test_repository_scan_allows_symlink_resolving_inside_root(
    tmp_path: Path,
    included_in_repository_scan: Callable[..., bool],
) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    target = docs / "target.md"
    target.write_text("# Target\n", encoding="utf-8")
    link = docs / "alias.md"
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable on this host: {exc}")

    assert included_in_repository_scan(link, root=root)
