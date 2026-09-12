# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `8d34591f08ab1f1a42dbb032963769968aefab2e`.
- Parent canonical Quality: `34689663093 = SUCCESS`.
- Worker heads checked: Errors `983a57ca2005ad231a8896fc24e77cfd48b971a7`; Spec/Core `008345141aac276f9723b536a70497e2dec74b20`; Backend `e4aacf8004e08fddacb41cebe687453a759444cf`; UI `2e39818797e9c13ab20ac929f5377ae9888181df`.

## Worker qualification

- Spec/Core: exact Core Focused Candidate `34688220222 = SUCCESS` and exact canonical Quality `34688220225 = SUCCESS`. The bounded current commit changes only `src/athena/knowledge/user_override_policy.py` and `tests/unit/test_user_override_policy.py`; current Develop retained the same pre-slice versions of both files, so the slice is compatible and READY.
- Backend: current exact head `e4aacf8004e08fddacb41cebe687453a759444cf` has Backend Focused `34691379970 = SUCCESS`, while canonical `34691380019` is still running. `ERR-0040` remains Backend-owned until exact-head canonical evidence closes it.
- UI: current head `2e39818797e9c13ab20ac929f5377ae9888181df` is a synchronization merge onto current Develop before further palette work; no bounded new UI product slice is promoted from that head in this integration.
- Errors: current handoff identifies `ERR-0040 = OPEN / P1` on the Backend scheduled-materialization lineage; no parallel Error-owned product mutation is taken.

## Integrated bounded slice

Integrated the Spec/Core user-correction conflict policy. Explicit `EvidenceRole.CONTRADICTS` evidence remains visible after a user correction, duplicate contradiction revisions deduplicate deterministically, non-contradictory evidence does not fabricate conflicts, and the policy never authorizes deletion of contrary source evidence. Malformed runtime evidence fails closed. Existing user-override behavior remains intact.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` is maintained without invented completion percentages.
- Historical signatures are not reopened without current exact-SHA reproduction.
- The eleven-screen visual state remains fail-closed; `MATCH` requires an opened original reference and a real exact-SHA render.
- Worker candidate evidence superseded by later commits is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
