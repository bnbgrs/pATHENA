# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T07:51Z
Branch: `develop/pathena-next`
HEAD at run start: `c217747f73267842ebd26c10eb5affc4fbf7bc0d`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34443327522@c217747f73267842ebd26c10eb5affc4fbf7bc0d = SUCCESS`.
- No queued or in-progress canonical Quality existed on Develop immediately before this mutation.
- Worker heads reviewed: Errors `e1262766de39b06bbe43ea62b9497c3c0100f60e`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `c5e750a827de4b353da9873cb38d95b46a119d60`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- No new worker slice is promotion-ready: Backend remains broad HOLD with exact-head Ruff/pytest failures; Spec/Core and UI contain no new unintegrated product slice; Errors reports Backend-owned formatter drift rather than a Develop root cause.
- No already-integrated product slice is being re-applied.

## Cross-cutting slice — Windows Core/API restart smoke

- The persistent Windows-Beta Core-startup signature was not explicitly exercised in the Windows lane: `athena-local-smoke --restart-cycles 1` existed only in the Ubuntu local-install job.
- Canonical Quality now runs the same disposable Core/API restart smoke in the existing `windows-path-safety` job after Windows path/storage/runtime-boundary regressions.
- This is CI coverage only. Production Core, runtime, storage, recovery, security, packaging and migration behavior are unchanged.
- The change does not weaken, skip or xfail any test or guard. It adds Windows evidence for the existing Core/API restart contract.

## Persistent release guards

- pypdf packaging remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE topology remains guarded.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap is explicitly covered in the Windows lane.
- Core-startup is now explicitly exercised by the Windows Core/API restart smoke.
- Duplicate-column remains an explicit Windows-Beta regression signature requiring focused mapping before promotion.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued or in progress.
2. Do not integrate broad Backend/Storage/Migration/Runtime history from the worker branch.
3. Resume READY qualification only after exact-current Develop Quality completes.
4. Identify the exact focused duplicate-column regression test before adding any further Windows-lane coverage; do not infer an OPEN defect without reproduction.
5. Do not re-integrate already landed UI/Core slices.
