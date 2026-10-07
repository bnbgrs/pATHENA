from __future__ import annotations

import tomllib
from pathlib import Path

from athena.version import __version__

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_release_version_is_consistent_across_source_project_and_lock() -> None:
    project = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads((_REPO_ROOT / "uv.lock").read_text(encoding="utf-8"))

    local_packages = [
        package
        for package in lock["package"]
        if package.get("name") == "athena-local"
        and package.get("source") == {"editable": "."}
    ]

    assert __version__ == "0.1.0"
    assert project["project"]["version"] == __version__
    assert len(local_packages) == 1
    assert local_packages[0]["version"] == __version__
