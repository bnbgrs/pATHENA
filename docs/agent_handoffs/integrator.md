# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `8a8f7e716075e6248214b15563a0e282aba7723c`.
- Exact canonical Quality on that parent: `34800785441 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — project Knowledge membership planning

Current Spec/Core `2c1aef57d1ffd5ab53283a05843c912c9e3e93ad` is exact-qualified: Core Focused `34802608287 = SUCCESS` and canonical Quality `34802608283 = SUCCESS` on the same worker SHA. Against current Develop the effective product delta is bounded to `src/athena/knowledge/project_membership.py` plus `tests/unit/test_knowledge_project_membership.py`; the worker's historical commit lineage is not promoted.

The new planner validates canonical Knowledge snapshots, requires `PROJECT_KNOWLEDGE` targets, preserves multiple distinct project memberships in first-seen order, collapses duplicate targets, reuses the established `belongs_to_project` relation definition, and fails closed if registry semantics silently fall back or drift. It does not persist relations, synthesize IDs, create provenance, or bypass repository/storage ownership.

Focused tests cover multi-project membership, duplicate collapse, non-project rejection, empty input, wrong collection type, and relation-registry fallback rejection. No Security, Storage, Recovery, packaging, Windows, visual, test-strength, or Skip/XFail guard is relaxed.

## Current worker truth at integration time

- Errors: `80ffef405415a9dfde9bff8b1f54764224652ef7`.
- Spec/Core: `2c1aef57d1ffd5ab53283a05843c912c9e3e93ad` — bounded project-membership planner selected.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`.
- UI: `5922cdca385ad622b9e97f4e17b32edb00c847b8` — remains UI/Visual-owned and unpromoted here.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real rendered exact-SHA state.
- The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
