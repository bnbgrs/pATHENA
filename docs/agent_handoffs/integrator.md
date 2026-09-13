# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `b4cba3d5cba31213e789cb2cbbc91f651e465e71`.
- Exact parent canonical Quality: `34731514082 = SUCCESS`.
- Worker heads checked: Errors `fe507864e1f02c418d1120e68bbc4b23a39244ec`; Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `ff9988a4b8db84593552a26266213d5ec871ef62`; UI `704ccd243ba2edb4f71e27d402d83b91724c0b30`.

## Iteration — bounded schedule-startup integration

Backend owner lineage `a709c229d6994c159490c2c1eaf3f2549f12cf56` had exact Backend Focused `34730587835 = SUCCESS`, Storage Focused `34730587918 = SUCCESS`, and canonical Quality `34730587873 = SUCCESS`. Its schedule-startup slice is separable from the unresolved paired-sidecar Storage mutation.

Integrated only:
- `src/athena/jobs/schedule_startup.py`
- `tests/unit/test_schedule_startup.py`

The slice requires an active caller transaction, reconciles durable missing occurrences before writes, applies the configured missed-run policy before materialization, uses deterministic occurrence identities, creates nothing for disabled schedules, and fails before partial inserts on a foreign identity collision.

The current Backend sync head `ff9988a4...` is not broadly promotable: Backend Focused and Storage Focused are green, but canonical `34733130192 = FAILURE`; additionally Error handoff `ERR-0049` keeps the separate `database.py` complete-sidecar-rotation mutation blocked pending paired foreign WAL+SHM replacement rejection coverage. No `database.py` change is included here.

## Worker qualification

- Spec/Core `78d51621...`: previously integrated bounded Knowledge history/reason-truth delta; no new product delta selected.
- Backend `ff9988a4...`: broad promotion blocked; bounded schedule-startup slice integrated from its exact-green owner lineage. Storage rotation remains excluded.
- UI `704ccd24...`: current sync head before further visual evidence; no broad UI promotion.
- Errors `fe507864...`: current handoff owns `ERR-0049` paired-sidecar guard gap and supersedes historical ledger state where newer exact evidence differs.

## Evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical (baseline `7be496d2...`) and is not sole authority where newer exact-SHA evidence exists.
- Eleven-screen parity remains fail-closed: no `MATCH` without opened original reference plus real exact-SHA render.
- Superseded or cancelled Worker CI is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures. `main` and `bnbgrs/ATHENA` remain read-only.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation. If green, consume the next Backend successor for `ERR-0049` only if paired foreign WAL+SHM replacement is explicitly rejected while the legitimate process-separated race remains green.
