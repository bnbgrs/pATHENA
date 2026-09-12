# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`
- Develop parent before this integration: `bfee081ff63e849b5d024299f0a7b9286dc737e7`
- Parent canonical Quality: `34671556177` = `SUCCESS`
- Promoted worker candidate: `postmerge/ui` exact SHA `dce6d463b17474ec2da702a14b7a4365123df45d`
- Exact UI Focused Candidate: `34671153433` = `SUCCESS`
- Exact canonical Quality on candidate: `34671153472` = `SUCCESS`

## Integrated bounded slice

The integration takes only the self-contained UI Help/accessibility product slice and its direct focused tests from the verified candidate:

- `src/athena/desktop/pathena_capability_help.py`
- `src/athena/desktop/pathena_navigation_context_accessibility.py`
- `tests/unit/test_pathena_capability_help_shell.py`
- `tests/unit/test_pathena_navigation_context_accessibility.py`

Worker handoff text, visual ledgers, and snapshot-renderer evidence are deliberately not promoted with this product slice. Current Develop documentation remains the source of truth for visual status.

The slice keeps Help inside the existing workspace shell, derives its capability hierarchy from live capability data, preserves the primary navigation/router invariant, exposes deterministic focus targets for Help options, and keeps contextual inspector/accessibility behavior UI-owned. No Core, Backend, Storage, Recovery, Security, packaging, runtime, or release-guard behavior is changed.

The candidate also had an unrelated Core Focused result caused by the historical broad Core test trigger. Current Develop already contains the narrowed Core trigger. That unrelated cross-trigger result is not used as evidence for this bounded UI promotion; the exact UI Focused Candidate and exact canonical Quality are both green.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical evidence and is not authoritative by itself for current OPEN state.
- Root `ALPHA_BETA_PROGRESS.md` is absent on the current Develop baseline.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: all eleven reference slots stay pending real visual review. No `MATCH` is claimed without an original reference plus a real exact-SHA render.
- Backend/Storage/Recovery candidates remain conservative and require their own exact-head evidence before promotion.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures.

## Promotion state

`PROMOTION_READY=NO`

Develop must not be mutated again while canonical Quality for the integration commit is queued or in progress. `main` and `bnbgrs/ATHENA` remain read-only.