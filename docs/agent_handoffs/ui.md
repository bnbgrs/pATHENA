# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@d40dc421585193db7bda039d113d7d81ccfb9c03`
- Worker: `postmerge/ui`
- History-preserving NON-FORCE synchronization commit: `e8fa9d20e865acc0aa56d867eede0a094721a954`, with parents `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c` and `d40dc421585193db7bda039d113d7d81ccfb9c03`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Verified handoff

- `UI-GAP-0072` is `FIXED_INTEGRATOR_READY`.
- Product commit: `c3637e08e64a6c1f08438b477a940b073b504de3`.
- Focused regression commit: `b927515fb5371f02f5da4cf4a90aa3d596d34ed0`.
- Exact worker head `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c` passed ATHENA Quality Gate `34167675010` with conclusion `success`.
- Jobs heading/intro now uses concise product guidance instead of SQLite, DurableJobService, lease/checkpoint or GUI-side-queue implementation terminology; job lifecycle/storage/scheduler/worker semantics are unchanged.

## Active UI slice

### UI-GAP-0073 — Jobs progress/status copy exposes persistence-oriented implementation terms

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Evidence: refresh/show/cancel progress plus refresh/show success text still used `durable` and `Persisting cancellation request` even though these are user-facing actions and status states, not storage architecture.

Product commit `4315a744a097c35ab46be4df883f0853544446b9` changes only the visible strings to `Refreshing jobs`, `Loading job details`, `Requesting cancellation`, `Jobs refreshed` and `Job … details loaded`.
Focused regression commit `cf777ca08ac0885c636aed95b5f6ddd6cd381386` constructs the real Qt Jobs workspace, verifies progress labels for refresh/show/cancel, and verifies refresh/show success status copy without durable/persistence terminology.

No job lifecycle, transition receipt, persistence, storage, scheduler, worker, provider, transport, security or cancellation semantics changed.

## Coordination

- Core: current `spec-core.md` reviewed; no UI-authored Core/Search semantics changed.
- Backend: current `backend.md` reviewed; no UI-authored backend/storage/scheduler/worker/provider/transport semantics changed.
- Errors: current `errors.md` reviewed; no historical Windows crash signature is reopened without exact-SHA reproduction.
- Integrator: current Develop handoff was preserved in synchronization merge `e8fa9d20e865acc0aa56d867eede0a094721a954`. `UI-GAP-0072` is ready for independent integration from exact verified worker head `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c`, backed by Quality `34167675010 = success`. Do not integrate `UI-GAP-0073` until canonical Quality succeeds on an exact worker head carrying unchanged product/test commits `4315a744a097c35ab46be4df883f0853544446b9` and `cf777ca08ac0885c636aed95b5f6ddd6cd381386`.

## Visual evidence

The original eleven screenshots are not accessible through the current repository/tool path. `VISUAL_REFERENCE_PENDING` remains mandatory. No `MATCH`, pixel-spacing, exact-color or screenshot-parity claim is made.