# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-09T13:50Z
Branch: `develop/pathena-next`
HEAD at run start: `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34353904087@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba = SUCCESS`; no exact-current Develop Quality was queued or in progress immediately before mutation.
- Current worker heads reviewed: Errors `4e31fec500e4b51dbaaf38ae7956afeec8354995`, Spec/Core `eb352369d5477c8b67fab5a76811916bfa28769b`, Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`, UI `3b0c11a16165036d5e8254ed59233408e077b782`.
- UI is not READY while exact-head Quality `34358994989@3b0c11a16165036d5e8254ed59233408e077b782` is in progress.
- Backend is not READY while exact-head Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9` is in progress; Storage/Migration/Runtime remains conservative.
- No non-superseded exact-green worker slice was available for integration at mutation time.

## Bounded cross-cutting slice

- Added `tests/unit/test_windows_packaging_contract.py` as a release-policy regression guard for the supported Windows portable build.
- The guard requires the package script to retain the Desktop/Worker two-EXE topology with distinct `packaged_app.py` and `packaged_worker.py` entry points, assembly of `pATHENA-Worker.exe` beside `pATHENA.exe`, and removal of the temporary worker dist tree after runtime merge.
- It also pins existing packaging acceptance facts: PyInstaller `6.15.0`, `--collect-all pypdf`, and the `app_runtime` onedir contents directory.
- This slice changes tests and Integrator evidence only. Runtime, UI, Storage, Recovery, Security, worker lifecycle, and packaging implementation semantics are unchanged.
- No Skip/XFail, assertion weakening, force push, history rewrite, auto-merge, or main mutation.

## Persistent release guards

- pypdf packaging metadata smoke remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE split is now additionally protected by a repository contract test.
- Exactly one Desktop instance with bounded workers remains required.
- Adaptive 2048-context Chat reserve remains required.
- Windows lane-lock/path-safety cluster remains required.
- Duplicate-column/Core-startup/storage-bootstrap signatures remain explicit Windows-Beta regression checks, not newly claimed open defects without current reproduction.

## Next integration

1. Treat the exact-head Develop canonical Quality triggered by this commit as authoritative and freeze Develop while it is queued/in progress.
2. Consume that result before any further Develop mutation.
3. Integrate UI only from a non-superseded exact-green current worker head.
4. Keep Backend/Storage/Migration/Runtime conservative until exact-head Ruff and full-pytest lineage is green.
5. Do not reopen closed historical signatures without current reproduction.
