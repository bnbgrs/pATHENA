# pATHENA Feature Integrator Handoff

## Current source of truth

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop baseline reviewed before mutation: `363d6ca497b12cf9f04d9c9392d945960eade3d3`.
- Worker heads reviewed: errors `9fb49a3195a6f8bf3ccbac60de39301cc01ffe6c`; spec-core `3b6b26015777e2c940e27900a3bdbf11236f180a`; backend `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`; UI `e7cbdb70a3f061b6160eb10de8c3aaa8925b73f0`.
- Exact Develop baseline had no associated queued/in-progress canonical Quality when mutation eligibility was checked.
- Core exact head `3b6b26015777e2c940e27900a3bdbf11236f180a` passed canonical Quality `34306400739`, but its product tree is already present on Develop; its only net diff from Develop is `spec-core.md`.
- Backend exact head `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` failed canonical Quality `34303936995`; no Backend slice was integrated.
- UI synchronized head `e7cbdb70a3f061b6160eb10de8c3aaa8925b73f0` has canonical Quality `34307975430` in progress; it was not consumed.

## Progress this run — Settings provider identity on model-list failure

No current worker supplied a new READY product slice. The current `ALPHA_BETA_PROGRESS.md` still records `UI-GAP-0020` as implemented with exact-green worker evidence but outstanding on shared Develop. That bounded deferred slice was independently re-reviewed against current Develop and integrated as the single progress action for this run.

Exact source evidence: UI product `64b9956601f2ec21ee3624d27323221dc2aba10c` plus focused regression `7b4569dd55c93cb19b5dfe2d53ea0c2ccc34fe71` passed canonical Quality `33942660590` at exact head `9ca1cb04031d618bd6d34d2df4a46d331d110a82`. The product changes only `src/athena/desktop/pathena_settings_runtime.py`. When a provider identity is still present but model freshness becomes unavailable, Settings now renders that provider as `last known`/idle with unavailable freshness instead of incorrectly replacing known identity with `Model provider · unavailable`. A genuinely absent provider still fails closed as unavailable/error. The model error/detail remains error-state and unavailable freshness.

The worker focused test file contains an existing `pytest.importorskip("PySide6")`; it was reviewed for assertions but deliberately not imported, preserving the Integrator no-Skip/XFail rule. No production Security, Storage, Recovery, Network, scheduler/worker, packaging, migration or Windows-runtime semantics changed.

## Quality / promotion state

- The integrated product blob is byte-identical to the exact-green UI candidate blob `afa98f0334bb1fffa9d63b4016ca97d7e86213df` verified by Quality `33942660590`.
- Exact-current Develop canonical Quality is still required before any Beta/release-ready or promotion-ready claim.
- Historical Windows/runtime signatures remain release guards only unless reproduced on an exact current SHA.

## Next integration order

1. Re-check exact-current Develop CI before any further mutation; if a canonical gate is queued/in-progress, keep Develop frozen until completion.
2. Consume UI `34307975430` only if it completes green on exact `e7cbdb70a3f061b6160eb10de8c3aaa8925b73f0` without superseding commits.
3. Keep Backend v41/schema/WAL work conservative while exact Backend Quality remains red.
4. Reconcile the `ALPHA_BETA_PROGRESS.md` row for the now-integrated provider-identity slice only when this can be done without superseding a running Develop gate.
5. Preserve explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv; Desktop/Worker two-EXE split; one Desktop with bounded workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock ownership cluster; and duplicate-column/Core-startup/storage-bootstrap signatures.

## Rules retained

No main mutation or promotion; no force push/history rewrite/auto-merge; no Skip/XFail addition; no weaker assertions; no Security/Storage/Recovery/Windows/validator relaxation; no fake success or fabricated provenance.