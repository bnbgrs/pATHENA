from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PR_ONLY_FOCUSED = (
    ".github/workflows/backend-focused-candidate.yml",
    ".github/workflows/core-focused-candidate.yml",
    ".github/workflows/storage-focused-candidate.yml",
    ".github/workflows/ui-focused-candidate.yml",
)
_MIXED_EVENT_WORKFLOWS = (
    ".github/workflows/ui-snapshot.yml",
    ".github/workflows/windows-runtime-boundary.yml",
)


def _concurrency_block(relative_path: str) -> str:
    lines = (_REPO_ROOT / relative_path).read_text(encoding="utf-8").splitlines()
    start = lines.index("concurrency:")
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if line and not line.startswith((" ", "\t")):
            break
        block.append(line)
    return "\n".join(block)


@pytest.mark.parametrize("relative_path", _PR_ONLY_FOCUSED)
def test_pr_only_focused_workflows_cancel_superseded_heads(
    relative_path: str,
) -> None:
    block = _concurrency_block(relative_path)

    assert "github.event.pull_request.number" in block
    assert "cancel-in-progress: true" in block
    assert "head.sha" not in block
    assert "github.run_id" not in block


@pytest.mark.parametrize("relative_path", _MIXED_EVENT_WORKFLOWS)
def test_mixed_workflows_cancel_only_superseded_pull_request_heads(
    relative_path: str,
) -> None:
    block = _concurrency_block(relative_path)

    assert "github.event.pull_request.number" in block
    assert "github.event_name == 'pull_request'" in block
    assert "github.run_id" not in block
    assert "pull_request.head.sha" not in block
