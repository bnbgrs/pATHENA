# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this repair: `146fb7280dbfe30f2bec129aec8ee77f015ce040`.
- Exact parent canonical Quality: `34697870543 = FAILURE`; failure is isolated to canonical Ruff. Specification validation, mypy, full pytest, Windows path safety/release guards, Linux storage regressions and local install smoke all passed on the same SHA.
- Worker heads checked: Errors `e33839260e5582e972aa6e311c9631afbe08fe24`; Spec/Core `a35a67f1afe2789d8a568fa3484ef5fe29f46de9`; Backend `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`; UI `9e9227dc722d7d771ae4ce4e45a75983330fed97`.

## Develop repair

No worker feature slice is promoted in this run. The previous Integrator-owned release-readiness slice left Ruff-formatting drift at the import/module-constant boundary in `src/athena/release_readiness.py` and `tests/unit/test_release_readiness.py`. The current Backend lineage independently carries an equivalent `fix(release): normalize readiness import blocks` correction. This repair applies only that formatting normalization to Develop; product behavior, assertions and release guards are unchanged.

The repair is deliberately bounded to the two release-readiness Python files plus this handoff and the Alpha/Beta progress register. It does not modify Storage, Recovery, Security, runtime topology, packaging, migrations, worker scheduling or UI.

## Worker qualification

- Errors exact `e33839260e5582e972aa6e311c9631afbe08fe24` identifies `ERR-0041` as a Spec/Core Ruff import-order blocker on an older Spec/Core SHA; Errors does not own the Core file.
- Spec/Core exact `a35a67f1afe2789d8a568fa3484ef5fe29f46de9` contains an owner-side Ruff correction and is not promoted while Develop itself requires repair/reverification.
- Backend exact `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8` contains the equivalent release-readiness formatting normalization; Backend Focused Candidate `34700396671 = SUCCESS`, while its canonical Quality was still in progress at qualification time. No Backend product slice is promoted.
- UI exact `9e9227dc722d7d771ae4ce4e45a75983330fed97` is a synchronization head; no UI product slice is promoted in this repair run.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` is maintained without invented completion percentages.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` still has all eleven slots at `IMPLEMENTED_PENDING_VISUAL_REVIEW`; `MATCH` requires an opened original reference plus a real render from the exact implementation SHA.
- `docs/ui/VISUAL_GAP_LEDGER.md` likewise asserts no screenshot-level `MATCH` without exact render evidence.
- Worker candidate evidence superseded by later commits is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop repair SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
