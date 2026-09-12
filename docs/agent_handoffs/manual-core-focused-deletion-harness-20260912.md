# Core Focused deletion-aware harness handoff

## Reproducer

Current UI synchronization head `postmerge/ui@9e9227dc722d7d771ae4ce4e45a75983330fed97` triggered Core Focused run `34699977166`, which failed although UI Focused was green.

The Core workflow diffed base `146fb7280dbfe30f2bec129aec8ee77f015ce040` against the candidate and selected paths that had been deleted from the candidate, including `src/athena/knowledge/orphan_knowledge.py` and `tests/unit/test_orphan_knowledge.py`. Ruff then failed with `E902 No such file or directory`; focused pytest failed with `file or directory not found`.

The diagnostic Ruff-remediation path also failed because it created `.focused-evidence/` and then required `git status --porcelain` to be completely empty, so its own intentionally untracked evidence made the candidate look dirty.

## Repair

- Every changed-file selector now uses `git diff --name-only --diff-filter=ACMRT` so deleted paths are excluded while added, copied, modified, renamed and type-changed candidate paths remain covered.
- Ruff selection, focused pytest selection and Ruff-remediation selection use the same deletion-aware filter.
- Diagnostic remediation checks tracked cleanliness with `git status --porcelain --untracked-files=no` before and after remediation, so intentionally untracked `.focused-evidence/` does not mask real tracked mutations.
- Enforcement remains fail-closed: both changed-file Ruff and changed focused tests must succeed.
- No lint rule, assertion, test requirement or product guard is weakened.

Contract coverage: `tests/unit/test_core_focused_workflow_contract.py` locks all three selectors, both tracked-cleanliness checks and final dual enforcement.

## Coordination

This candidate is stacked on `manual/develop-release-readiness-ruff-20260912@22f7b640cccad1a65ccc6a32e46778b47e2a697e` only to avoid the known Develop release-readiness Ruff baseline failure while verifying the workflow fix. Its delta beyond that parent is limited to the Core Focused workflow, its workflow-contract test and this handoff.

UI owns no workflow repair and should not work around the E902 failure in product code. Spec/Core should not recreate deleted files merely to satisfy the old selector. Errors should record this as a CI-harness defect distinct from product/runtime failures.

After the parent Develop Ruff fix integrates, recreate or retarget this exact bounded delta onto current Develop and require fresh exact-head evidence before integration.
