# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@4e18f75beeaa1c5b57bca28dcad5a062ac498051`
- Worker: `postmerge/ui`
- History-preserving NON-FORCE synchronization commit: `4ec9b59d01b87cb9feaad3cea84dec99942a85dc`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Verified handoff

- `UI-GAP-0071` is `FIXED_INTEGRATOR_READY`.
- Product commit: `b7e96e01e5690d914be62d489faae92bf0e59571`.
- Focused regression commit: `067983b6613a42526ac48cbd5d21b3e36d1e3e74`.
- Exact worker head `377d5494b8a6aa9d5a65447b7fe12b5851664914` passed ATHENA Quality Gate `34164101918` with conclusion `success`.
- Empty-selection and no-jobs guidance now uses product language without durable/persisted/checkpoint/lease/pinned-state implementation terminology; job lifecycle/storage/scheduler/worker semantics are unchanged.

## Active UI slice

### UI-GAP-0072 — Jobs workspace intro exposes implementation architecture

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Evidence: the persistent Jobs heading/intro visibly exposed `DURABLE JOB CONTROL`, SQLite, leases/checkpoints, `DurableJobService transitions` and a `GUI-side queue` implementation distinction instead of explaining the user-facing surface.

Product commit `c3637e08e64a6c1f08438b477a940b073b504de3` changes only the heading and intro: `JOBS`, followed by concise guidance that background work from Research and Sources appears here and can be inspected or managed with available controls.
Focused regression commit `b927515fb5371f02f5da4cf4a90aa3d596d34ed0` constructs the real Qt Jobs workspace, inspects visible labels, asserts the product guidance and forbids the implementation-heavy heading/SQLite/DurableJobService/checkpoint/lease/GUI-side-queue terminology.

No job lifecycle, persistence, storage, scheduler, worker, provider, transport, security or cancellation semantics changed.

## Coordination

- Core: current `spec-core.md` reviewed; no UI-authored Core/Search semantics changed.
- Backend: current `backend.md` reviewed; no UI-authored backend/storage/scheduler/worker/provider/transport semantics changed.
- Errors: current `errors.md` reviewed; no historical Windows crash signature is reopened without exact-SHA reproduction.
- Integrator: current Develop handoff from `4e18f75beeaa1c5b57bca28dcad5a062ac498051` was preserved in synchronization merge `4ec9b59d01b87cb9feaad3cea84dec99942a85dc`. `UI-GAP-0071` is ready for independent integration from exact verified worker head `377d5494b8a6aa9d5a65447b7fe12b5851664914`, backed by Quality `34164101918 = success`. Do not integrate `UI-GAP-0072` until canonical Quality succeeds on an exact worker head carrying unchanged product/test commits `c3637e08e64a6c1f08438b477a940b073b504de3` and `b927515fb5371f02f5da4cf4a90aa3d596d34ed0`.

## Visual evidence

The original eleven screenshots are not accessible through the current repository/tool path. `VISUAL_REFERENCE_PENDING` remains mandatory. No `MATCH`, pixel-spacing, exact-color or screenshot-parity claim is made.
