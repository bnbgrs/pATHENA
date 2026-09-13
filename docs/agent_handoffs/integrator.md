# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop head before this integration: `ba6bc224cc152c144d13ca21730dad6620610abe`.
- Exact canonical Quality `34781654173 = SUCCESS` on that head.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — strengthen Core candidate exact qualification

Current Spec/Core `93358a1c7a310a2da4279fb51b1e99a1bde505ab` has Core Focused `34783221743 = SUCCESS` but canonical Quality `34783221804 = FAILURE` solely because mypy rejects a candidate-owned tuple inference in `merge_split_policy.py`; full pytest and all persistent release-guard lanes passed. The product root cause remains Core-owned and is not parallel-patched here.

The cross-cutting integration fix strengthens `.github/workflows/core-focused-candidate.yml`: exact changed Core Python files now run mypy in addition to Ruff before a focused candidate can be considered green. Mypy evidence is retained in `.focused-evidence/mypy.txt`, and the final focused outcome requires Ruff, mypy and focused pytest all to succeed. `tests/unit/test_core_focused_candidate_workflow.py` locks this contract without weakening any existing selector, test, security, storage, recovery or release guard.

This closes the qualification blind spot that allowed a candidate-specific typing regression to present as focused-green while canonical Quality was red. It does not change Core product semantics and does not claim the current Merge/Split candidate READY.

## Current worker truth at integration time

- Errors: `db47bc9d89633034d2897367caee86b96f945fd8`.
- Spec/Core: `93358a1c7a310a2da4279fb51b1e99a1bde505ab`.
- Backend: `dda2dd74c0989f7ec453e8a2b7d8122f85a9251c`; tree-synchronized with Develop before this integration.
- UI: `de4efa5d3814948d47d83484c4a27ac0c2daf64c`; visual review remains fail-closed.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` is historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real rendered exact-SHA state.
- The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
