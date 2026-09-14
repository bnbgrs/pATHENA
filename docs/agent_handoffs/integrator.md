# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`.
- Authoritative exact canonical Quality on that parent: `34785279278 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — integrate bounded Knowledge merge/split identity planning

Spec/Core candidate `52b4e322041547e9039a0f3026f6747583605914` is exact-verified by Core Focused `34789228532 = SUCCESS` and canonical Quality `34789228473 = SUCCESS`. Against the current Develop parent, the effective worker delta is bounded to `src/athena/knowledge/merge_split_policy.py`, `tests/unit/test_knowledge_merge_split_policy.py`, and worker handoff documentation. Only the product/test files are promoted; worker history is not merged.

The planner is persistence-neutral and makes identity consequences explicit before an atomic repository write. A merge may retain either existing canonical ID or create a new result ID while explicitly listing superseded IDs. A split requires at least two unique new UUID identities, rejects reuse of the source identity, and records the source as superseded. Runtime type validation is fail-closed.

No test, guard, Security, Storage, Recovery, packaging, runtime, or visual invariant is relaxed. After this integration, the resulting exact Develop SHA must pass canonical Quality before any further Develop mutation.

## Current worker truth at integration time

- Errors: `e8247f46fd2bc685fae10d5bfbd2efceb5a19904`.
- Spec/Core: `52b4e322041547e9039a0f3026f6747583605914` — bounded merge/split slice exact green and promoted here.
- Backend: `e4e1244e8482ac7d78e557ded5f91252cccc0347` — tree-equivalent to the pre-integration Develop parent; no product delta.
- UI: `05d640fd13212f8671bff0f0ca49a673df4f10c1` — current visual run `34793863216 = FAILURE`; not READY.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` is historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real rendered exact-SHA state.
- The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
