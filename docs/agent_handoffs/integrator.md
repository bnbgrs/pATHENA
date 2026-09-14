# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `e818ade900545e788c72cbd24bb6761880470148`.
- Authoritative exact canonical Quality on that parent: `34794066456 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — application-facing Knowledge merge/split planning

The previously integrated persistence-neutral Knowledge merge/split planner is now reachable through `KnowledgeService` without inventing merge persistence. `plan_merge` requires both source Knowledge identities to exist before delegating to the fail-closed planner; `plan_split` requires the source identity to exist before validating proposed child IDs. Both methods are read-only and return explicit identity/supersession plans for a later authorized atomic semantic write.

Focused regression coverage verifies existing-source enforcement, missing-source rejection, retained/superseded IDs, and that planning creates no Knowledge revisions. No repository schema, storage transaction, provenance write, Security/Storage/Recovery behavior, visual contract, or release guard is relaxed.

## Current worker truth at integration time

- Errors: `e90c89d4759d7c6ad1be09edf43c992c46159d92` — documentation/requalification only; no bounded product fix to promote.
- Spec/Core: `52b4e322041547e9039a0f3026f6747583605914` — merge/split planner already promoted; no new product delta selected.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d` — tree-equivalent to current Develop parent after history-preserving sync; no product delta.
- UI: `9c03ce6bb2c4cb9913cf0dafcaa2336fdb6dd82c` — Visual `34794418240 = FAILURE` only at final visual verdict; not READY and no baseline is auto-accepted.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` is historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real rendered exact-SHA state.
- The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.