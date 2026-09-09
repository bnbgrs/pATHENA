# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-09T12:52Z
Branch: `develop/pathena-next`
HEAD at run start: `ee7803f9b73140a3789893c25919b011d4e8d23b`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34343282932@ee7803f9b73140a3789893c25919b011d4e8d23b = SUCCESS`.
- Current worker heads reviewed: Errors `28dc066f04d90b5e942fd3cdd2f710db4bc9906c`, Spec/Core `6b833fdbe9066dbd17f8a54272b0543d7c5d5ece`, Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`, UI `0ba6811f939dc464f2ba78c4b8494da16f5eefab`.
- UI is not READY while exact-head Quality `34352820678` remains in progress.
- Backend is not READY: exact Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; Error handoff keeps `ERR-0026`, `ERR-0028`, and `ERR-0029` in progress.
- Spec/Core has no new Integrator-ready product delta on the current Develop baseline.

## Bounded cross-cutting slice

- Extended `tests/unit/test_quality_workflow_contract.py` with a Windows release-policy regression.
- The contract now requires canonical `windows-path-safety` to remain on `windows-latest`, to check out exact `CANDIDATE_SHA`, and to keep both deterministic Windows locality and Windows storage path regression steps, including `test_storage_safe_mode.py`.
- This is test-only release-guard hardening. No runtime, UI, Storage, Recovery, Security, packaging topology, worker lifecycle, or product semantics change.
- Focused contract execution: 3 passed.
- No Skip/XFail, assertion weakening, force push, history rewrite, auto-merge, or main mutation.

## Persistent release guards

- pypdf packaging metadata smoke remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE split remains unchanged.
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
