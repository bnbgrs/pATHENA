# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `db159a068a5de1ca8cd302a5ea436f3f07889d9f`.
- Exact parent canonical Quality: `34700628139 = SUCCESS`.
- Worker heads checked: Errors `9c634dccc829b1a822288afc99ab0339d77efbb1`; Spec/Core `1f61104959dc6a7d7fcff6051fb013f5f6894706`; Backend `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`; UI `4898bceb9a5af98e1a044eb656714ce03be5e2a4`.

## Worker qualification

- Spec/Core exact `1f61104959dc6a7d7fcff6051fb013f5f6894706`: Core Focused Candidate `34701843776 = SUCCESS`; canonical Quality `34701843759 = SUCCESS`. The bounded product delta is `src/athena/knowledge/provenance_explanation.py` plus `tests/unit/test_provenance_explanation.py`. READY.
- Errors current head is documentation/evidence reclassification only; no Error-owned product mutation is imported.
- Backend current head is a release-readiness formatting repair lineage rather than a higher-priority new Backend prerequisite; no Backend product mutation is imported.
- UI current head is synchronized with current Develop before workspace hierarchy work; its handoff remains non-integrator-ready for the pending UI candidate. No UI product mutation is imported.

## Integrated bounded slice

Integrated truthful, transport-neutral Knowledge provenance explanations. The policy projects only provenance already recorded on the canonical Knowledge revision, sorts inputs by their recorded ordinal, retains entity/revision/role identity, and exposes the recorded actor and timestamp. Source-free user Knowledge is represented explicitly as having no recorded provenance inputs instead of fabricating a source.

The boundary rejects non-tuple inputs, wrong input element types, provenance inputs belonging to another provenance record, and duplicate ordinals. The slice is read-only projection logic and does not mutate Knowledge, Storage, Recovery, Security, runtime topology, packaging, migrations, scheduling or UI.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` is maintained without invented completion percentages.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains fail-closed; no screenshot `MATCH` is inferred without opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` likewise asserts no screenshot-level `MATCH` without exact render evidence.
- Worker candidate evidence superseded by later commits is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
