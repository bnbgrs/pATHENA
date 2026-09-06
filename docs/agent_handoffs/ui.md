# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@8236500a5ae0ae58e7dce5bb3cf0771eb534670d`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `ab9e79f7a5fd6e96808b22d65e427eb0e9a3fcf9`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0035 — Research detail reader keyboard focus

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `f9d0a01de648ea806bfd725c3b35a68fc9eb425d` adds only `QPlainTextEdit#researchDetails:focus` to the canonical accent-border focus block.
- Focused regression `4183addc10689496101c2b4d6ae7d45fcb4cf3d1` verifies selector and canonical accent token.
- Exact UI documentation head `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4` passed ATHENA Quality Gate `34019891561 = success`.

## UI-GAP-0036 — Jobs detail reader keyboard focus

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `PathenaJobsExperience._configure_tab_order()` explicitly puts the read-only Jobs details reader between the durable-job list and Refresh. `_configure_accessibility()` exposes it as `Durable job details`. The specialized `QPlainTextEdit#jobDetails` rule has no focus state, and the canonical object-specific reader focus block previously covered Help, Library and Research but not Jobs.
- Product `605c63992e112a168ddeda403b561740d524c018` adds only `QPlainTextEdit#jobDetails:focus` to the established canonical accent-border block.
- Focused regression `8ae0f51e0637e75d7619e7fb9c4fe65679c6f626` locks the selector and canonical accent token.
- Durable job content, filtering, action enablement/transitions, scheduler behavior, read-only semantics and backend/storage/security/runtime ownership are unchanged.

## Develop synchronization

Develop-only Personal-Memory changes were synchronized exactly before the UI mutation: `src/athena/memory/repository.py`, `tests/unit/test_personal_memory_context_priority.py`, and `docs/agent_handoffs/integrator.md`. The UI worker did not author or reinterpret those semantics.

## Integrator handoff

- UI-GAP-0035 is READY: product `f9d0a01de648ea806bfd725c3b35a68fc9eb425d`, focused regression `4183addc10689496101c2b4d6ae7d45fcb4cf3d1`, exact verified head `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4`, Quality `34019891561 = success`.
- UI-GAP-0036 is NOT READY until canonical Quality succeeds on an exact candidate containing product, focused regression, manifest, ledger and this handoff.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Consume exact canonical Quality for UI-GAP-0036. If green, promote it to `FIXED / INTEGRATOR_READY`, return Screen 04 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then inspect one distinct Jobs accessibility/state/interaction gap without reopening job-detail focus or previously closed Research/Library focus diagnoses.
