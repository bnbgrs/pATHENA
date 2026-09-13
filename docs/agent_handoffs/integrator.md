# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `d7a5bcf6d836c47588b907d666b5541386ca0678`.
- Exact parent canonical Quality `34737035739 = FAILURE`: controller isolation itself is green (`6 passed`), the remaining canonical suite reaches completion with `1 failed, 5029 passed, 17 skipped`; the sole failure is the stale workflow-contract assertion expecting the pre-isolation one-process pytest command.
- Worker heads checked: Errors `2a777c98dd10d22cefc487e0f76d0552415efdf5`; Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d`; Backend `7063801bcefc7153f4ef5de4b3d82669861b4208`; UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb`.

## Iteration 1 — exact Develop regression closed

`tests/unit/test_quality_workflow_contract.py` now guards the actual fail-closed canonical structure: the mandatory desktop-controller module runs in its own interpreter, every remaining test runs exactly once with only that module ignored in the second invocation, both PIPESTATUS values are captured, and either nonzero status fails the canonical pytest step. This updates the contract to the already-integrated native Qt isolation without Skip/XFail, retry, test removal, or gate weakening.

## Iteration 2 — bounded Knowledge model disclosure integrated

Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d` has exact Core Focused `34737394852 = SUCCESS` and canonical `34737394871 = SUCCESS`. Its effective product delta against current Develop is only `src/athena/api/knowledge_model_disclosure.py` plus `tests/unit/test_knowledge_model_disclosure.py`.

The slice exposes recorded model/run provenance for a Knowledge revision without fabricating model participation. User-authored revisions reject supplied model provenance; primary-model revisions require a matching succeeded `ProcessingRun` and `ModelSignature`; mismatched or partial provenance fails closed.

## Blocked candidates

- Backend `7063801b...`: Storage Focused `34738082478 = FAILURE`; hold all Storage mutation. `ERR-0049` remains current until paired foreign WAL+SHM replacement is rejected while legitimate rotation/race behavior remains green.
- UI `2f003f7d...`: newer UI-owned work exists, but no broad branch promotion; re-qualify bounded UI slices only after exact Develop quality completes.
- Historical `ERROR_LEDGER.md` is not authoritative over newer exact-SHA evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail. `main` and `bnbgrs/ATHENA` remain read-only.

## Visual truth

Eleven-screen parity remains fail-closed: no `MATCH` without opened original reference plus real exact-SHA render.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
