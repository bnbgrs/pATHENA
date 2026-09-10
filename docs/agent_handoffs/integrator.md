# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T18:48Z
Branch: `develop/pathena-next`
HEAD at run start: `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `d6ef65e11106aa6d43eba8c22c4173ee9c63ce60`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `49ff66eeb706695d0564bf87274a5f9087b8ef98`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = SUCCESS`; immediately before mutation there were zero queued and zero in-progress canonical Develop runs.
- No new worker product slice is promotion-ready. Errors keeps `ERR-0033` OPEN as the Backend-owned BE-046 Windows emergency-reserve directory-identity gap and makes no product mutation; Backend's current head is documentation-only and supplies no bounded focused candidate; Spec/Core and UI expose no new unintegrated bounded product slice.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present under those exact names in current searchable repository evidence and therefore are not synthesized or treated as authoritative.
- UI source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven pending real exact-SHA renders against opened originals.

## Bounded cross-cutting slice — native Windows durable filesystem boundary coverage

Current Develop already contains focused `tests/unit/test_durable_fs.py` and `tests/unit/test_durable_fs_parent_identity.py`. Linux storage regressions execute both, while the native Windows storage lane previously omitted them even though durable replace/mkdir, symlink/reparse boundaries and parent-directory identity are part of the release-critical Windows storage/path-safety surface.

This slice adds both existing focused test modules to `Run Windows storage path regressions`. It changes no Storage/Recovery production code and no assertion. It adds direct native-Windows evidence for durable filesystem and parent-identity boundaries without attempting to implement or claim closure of BE-046/ERR-0033.

## Persistent release guards

- pypdf packaging remains fail-closed and explicitly exercised on Linux and Windows canonical lanes.
- Frozen argv remains fail-closed and explicitly exercised in the Windows packaged runtime lane.
- Desktop/Worker two-EXE topology remains explicit in canonical Windows Quality.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement; process ownership/lifecycle and server lifecycle remain explicitly selected for native Windows verification.
- Adaptive 2048-context Chat reserve remains explicitly exercised in Windows canonical Quality.
- Windows lane-lock/path-safety cluster remains guarded; durable filesystem and parent-directory identity are now explicitly selected for native Windows verification.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization remain explicitly represented in Windows canonical Quality.
- ERR-0033/BE-046 remains Backend-owned OPEN; this Integrator slice does not mutate or weaken its directory-identity invariant.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued/in progress.
2. If exact Quality is red, diagnose only that exact-SHA failure and do not weaken durable filesystem, Storage, Recovery or path-safety contracts.
3. Keep BE-046/ERR-0033 on Backend ownership absent a fresh bounded exact-green candidate with native-Windows adversarial directory-swap evidence.
4. Do not re-integrate already landed UI/Core/runtime slices.
