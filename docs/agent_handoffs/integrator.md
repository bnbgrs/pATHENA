# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T04:52Z
Branch: `develop/pathena-next`
HEAD at run start: `fafbeabdde1207ebc97712aa61ee947410cbf691`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691 = FAILURE`.
- The failure is isolated to the Windows path-safety job, specifically `Run Windows storage path regressions`; canonical Python quality, Linux storage regressions, and local-install/pypdf smoke are green on the same Develop SHA.
- Worker heads reviewed: Errors `a855aca00d090f6762fe1a47095b3a213653b130`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `31752aefe0d5f79d8c305c531cc7584c0585e175`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- No already-integrated product slice is being re-applied. Broad Backend/Storage/WAL/Runtime changes remain conservative HOLD.

## Corrective slice — Windows-safe storage bootstrap test path

- The newly exercised Windows storage-bootstrap test used a hard-coded POSIX path, `Path("/tmp/bootstrap-emergency.reserve")`, inside `_ReserveStub.ensure()`.
- `postmerge/backend@31752aefe0d5f79d8c305c531cc7584c0585e175` contains a bounded one-line portability correction: `Path.cwd() / "bootstrap-emergency.reserve"`.
- Only that test-path correction is integrated. Test assertions and production storage/recovery/runtime behavior are unchanged.
- The relevant Windows path/storage lane is green on the Backend candidate head; unrelated global Backend failures are outside this bounded test-only diff and are not integrated.
- No Skip/XFail, test weakening, storage/recovery/security relaxation, or workflow-command weakening is introduced.

## Persistent release guards

- pypdf packaging remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE topology remains guarded.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety cluster remains guarded.
- Duplicate-column/Core-startup/storage-bootstrap signatures remain explicit Windows-Beta regression checks unless exact-current evidence reopens them.

## Next integration

1. Run/consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued or in progress.
2. Do not integrate broad Backend/Storage/Migration/Runtime history from the worker branch.
3. Resume READY qualification only after exact-current Develop Quality completes.
4. Do not re-integrate already landed UI/Core slices.
