# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@e9c931f5ae00e2db70e8a42ac6110b78cf35b789`
- Worker: `postmerge/ui`
- History-preserving NON-FORCE synchronization commit: `2e75b71ca469b2356d9443b7e4a271f75210262b`, with parents `352b4c72c39d5cafe866c604a050a1b93df71940` and `e9c931f5ae00e2db70e8a42ac6110b78cf35b789`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Verified handoff

- `UI-GAP-0073` is `FIXED_INTEGRATOR_READY`.
- Product commit: `4315a744a097c35ab46be4df883f0853544446b9`.
- Focused regression commit: `cf777ca08ac0885c636aed95b5f6ddd6cd381386`.
- Harness correction: `352b4c72c39d5cafe866c604a050a1b93df71940` restores the real `refresh()` method immediately after constructor suppression; assertions and product behavior are unchanged.
- Exact worker head `352b4c72c39d5cafe866c604a050a1b93df71940` passed ATHENA Quality Gate `34174030199` with conclusion `success`.
- Jobs refresh/show/cancel progress plus refresh/show success text now uses product language (`Refreshing jobs`, `Loading job details`, `Requesting cancellation`, `Jobs refreshed`, `Job … details loaded`) instead of persistence-oriented wording.
- No job lifecycle, transition receipt, persistence, storage, scheduler, worker, provider, transport, security or cancellation semantics changed.

## Active UI slice

### UI-GAP-0074 — Jobs nonzero-exit status exposes command-oriented implementation language

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Evidence: the common nonzero-exit path in `JobsWorkspace._process_finished()` rendered `Jobs command ... failed (exit N)` for refresh, detail loading and job actions, exposing the CLI/transport mechanism instead of the user operation.

Product commit `ee2dafc9453c8e3b5d67aed107a955b086111f68` changes only visible failure copy: list failures report that Jobs could not be refreshed; show failures report that job details could not be loaded; transition failures name the real action and preserve whether it completed in the background plus the exit code.
Focused regression commit `10ddf88043757628906480541e179323f5af7247` exercises the real Qt Jobs workspace for list/show/transition/background nonzero exits and requires the human-facing copy without `command` jargon.

No job lifecycle, transition receipt, persistence, storage, scheduler, worker, provider, transport, security, cancellation or process-spawn semantics changed.

## Coordination

- Core: current `spec-core.md` reviewed; no UI-authored Core/Search semantics changed.
- Backend: current `backend.md` reviewed; no UI-authored backend/storage/scheduler/worker/provider/transport semantics changed.
- Errors: current `errors.md` reviewed; no historical Windows crash signature is reopened without exact-SHA reproduction.
- Integrator: current Develop handoff and §68 acceptance test were preserved through synchronization commit `2e75b71ca469b2356d9443b7e4a271f75210262b`. `UI-GAP-0073` is ready for independent integration from exact verified worker head `352b4c72c39d5cafe866c604a050a1b93df71940`, backed by Quality `34174030199 = success`. Do not integrate `UI-GAP-0074` until canonical Quality succeeds on an exact worker head carrying unchanged product/test commits `ee2dafc9453c8e3b5d67aed107a955b086111f68` and `10ddf88043757628906480541e179323f5af7247`.

## Visual evidence

The original eleven screenshots are not accessible through the current repository/tool path. `VISUAL_REFERENCE_PENDING` remains mandatory. No `MATCH`, pixel-spacing, exact-color or screenshot-parity claim is made.
