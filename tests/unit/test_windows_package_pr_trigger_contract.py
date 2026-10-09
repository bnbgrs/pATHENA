"""Native Windows package PR-trigger coverage for release-critical runtime paths."""

from __future__ import annotations

import re
from fnmatch import fnmatchcase
from pathlib import Path

_WORKFLOW = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "workflows"
    / "windows-package.yml"
)
_CRITICAL_PATHS = (
    "src/athena/api/runtime.py",
    "src/athena/chat/direct.py",
    "src/athena/chat/unified.py",
    "src/athena/chat/context_continuity.py",
    "src/athena/core/application.py",
    "src/athena/desktop/pathena_window.py",
    "src/athena/desktop/window.py",
    "src/athena/model/adapters/lm_studio.py",
    "src/athena/model/registry.py",
    "src/athena/retrieval/context_package.py",
    "src/athena/storage/bootstrap.py",
    "src/athena/storage/migration_coordinator.py",
    "tests/unit/test_chat_context_continuity.py",
    "tests/unit/test_direct_chat_context_budget.py",
    "tests/unit/test_issue_244_model_selection.py",
    "tests/unit/test_migration_coordinator.py",
    "tests/unit/test_windows_package_pr_trigger_contract.py",
)


def _pr_path_patterns(workflow: str) -> tuple[str, ...]:
    assert "\n  pull_request:\n" in workflow
    pull_request = workflow.split("\n  pull_request:\n", 1)[1]
    pull_request = pull_request.split("\npermissions:\n", 1)[0]
    assert "      - develop/pathena-next\n" in pull_request
    assert "    paths:\n" in pull_request
    return tuple(re.findall(r'^\s+- "([^"]+)"\s*$', pull_request, re.MULTILINE))


def test_native_windows_package_runs_for_release_critical_pr_paths() -> None:
    patterns = _pr_path_patterns(_WORKFLOW.read_text(encoding="utf-8"))
    assert patterns
    missing = [
        path for path in _CRITICAL_PATHS
        if not any(fnmatchcase(path, pattern) for pattern in patterns)
    ]
    assert not missing, f"Windows package PR filter omits critical paths: {missing}"


def test_native_windows_package_uses_exact_pr_head() -> None:
    workflow = _WORKFLOW.read_text(encoding="utf-8")
    assert "github.event.pull_request.head.sha" in workflow
    assert "ref: ${{ env.REQUESTED_REF }}" in workflow
    assert "Prove checked-out identity" in workflow
