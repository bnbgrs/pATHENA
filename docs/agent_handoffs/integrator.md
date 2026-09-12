# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`
- Develop parent before this integration: `4dbefe2167b28bffab2c6b69b7a8df4b43770a6f`
- Parent canonical Quality: `34674406807` = `SUCCESS`
- Promoted worker candidate: `postmerge/spec-core` exact SHA `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`
- Exact Core Focused Candidate: `34672548118` = `SUCCESS`
- Exact canonical Quality on candidate: `34672548120` = `SUCCESS`

## Integrated bounded slice

The integration takes only the self-contained stale-Knowledge maintenance policy and its direct focused tests from the verified Spec/Core candidate:

- `src/athena/knowledge/stale_policy.py`
- `tests/unit/test_stale_knowledge_policy.py`

The candidate is one commit-lineage step behind current Develop because Develop subsequently integrated a disjoint UI Help slice. Exact comparison against current Develop shows only these two Core files differ, so no UI, Backend, Storage, Recovery, Security, CI, visual-ledger, or worker-history mutation is imported.

The policy emits a deterministic maintenance signal when a Knowledge validity window has ended or when a fully specified source-age threshold is exceeded. Missing maintenance evidence remains current-or-unknown rather than inventing staleness. The policy does not mutate Knowledge, Claims, provenance, epistemic truth/status, persistence, or retrieval behavior. Invalid timestamp/duration inputs and incomplete source-age pairs fail closed.

## Current evidence rules

- Current Error handoff keeps `ERR-0035 / BE-052` OPEN/P1/Backend-owned and reports a Backend candidate that removed startup DB/WAL/SHM identity protection and its adversarial regression test. That Backend lineage is not integration-ready and was not touched here.
- `docs/agent_logs/ERROR_LEDGER.md` remains historical evidence rather than sole authority for current OPEN state.
- Root `ALPHA_BETA_PROGRESS.md` remains absent on the current Develop baseline.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed; no visual `MATCH` is asserted without the original reference and a real exact-SHA render.
- Backend/Storage/Recovery candidates remain conservative and require their own exact-head evidence before promotion.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, or history rewrite is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.