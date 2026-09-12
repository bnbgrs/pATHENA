# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `b8afe9661387c4a1a3d65f539c39ca772f37329c`.
- Exact parent canonical Quality: `34710920451 = SUCCESS`.
- Worker heads checked: Errors `3e3915d5cb0c3964661db1fcef100f98664915c1`; Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; Backend `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`; UI `460e35e74d8c529a5880356bf30b9099d80e39de`.

## Worker qualification

- Spec/Core exact `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`: NOT READY. Core Focused remains red on one Ruff I001 while six focused behavior tests pass.
- Backend exact `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`: NOT READY. Backend Focused is green but Storage Focused is red on the sidecar identity-continuity guard; Storage/Recovery promotion remains conservative.
- UI exact `460e35e74d8c529a5880356bf30b9099d80e39de`: UI Focused Candidate is green; canonical Quality is still active at qualification time, so no UI slice is promoted yet.
- Errors current handoff reports `ERR-0042`, `ERR-0043`, and `ERR-0044`; its baselines are older than current Develop and are treated as diagnostic evidence, not sole current truth.

## Cross-cutting integration

This integration adds a regression test for the Core Focused candidate workflow repair already present on Develop. The test locks the exact non-deletion diff selection and tracked-worktree remediation invariants so `ERR-0044` cannot silently regress:

- all three Core Python diff selections must use `--diff-filter=ACMR`;
- the former deletion-inclusive selector is forbidden;
- remediation cleanliness must ignore untracked evidence only, while tracked mutations remain visible;
- immutable reset and exact candidate restoration remain required.

No Product, Storage, Recovery, Security, UI, packaging, runtime-topology, Skip/XFail, assertion, or canonical-gate semantics are relaxed.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to current Develop and is not the sole authority for current OPEN state.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` is maintained without invented completion percentages.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed; no screenshot `MATCH` is inferred without opened original reference plus a real exact-SHA render.
- Worker candidate evidence superseded by later commits is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
