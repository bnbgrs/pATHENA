# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-09T10:48Z
Branch: `develop/pathena-next`
HEAD at run start: `2a90e71bc2c604cd745766a608481fc14106ec07`

## Current evidence

- `main` remains read-only and untouched.
- Develop exact canonical Quality `34337745698@2a90e71bc2c604cd745766a608481fc14106ec07 = FAILURE`.
- The failure is bounded to Ruff `I001` in `tests/unit/test_quality_workflow_contract.py`; Mypy, full Pytest, Windows path safety, Linux storage regression, Local install smoke, and Spec validator passed on that exact SHA.
- Backend remains HOLD: its current v41/schema/WAL lineage is not exact-green; current Error handoff retains `ERR-0026` through `ERR-0029` as in progress while closing only independently proven subclusters.
- No Worker slice was promoted ahead of repairing the exact-current Develop root cause.

## Bounded corrective slice

- Apply only Ruff's exact import-block formatting correction to `tests/unit/test_quality_workflow_contract.py` by removing the extra blank line after the sole import.
- Test assertions and workflow policy are unchanged.
- No production runtime, UI, Storage, Recovery, Security, packaging topology, worker lifecycle, or release guard is changed.
- No Skip/XFail, assertion weakening, force push, history rewrite, auto-merge, or main mutation.

## Persistent release guards

- pypdf packaging metadata smoke remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE split remains unchanged.
- Exactly one Desktop instance with bounded workers remains required.
- Adaptive 2048-context Chat reserve remains required.
- Windows lane-lock cluster remains required.
- Duplicate-column/Core-startup/storage-bootstrap signatures remain explicit Windows-Beta regression checks, not newly claimed open defects without current reproduction.

## Next integration

1. Treat the resulting exact-head canonical Quality as authoritative and freeze Develop while it is queued/in progress.
2. Consume that exact-SHA result before any further Develop mutation.
3. Integrate UI only from a non-superseded exact-green current worker head.
4. Keep Backend/Storage/Migration/Runtime conservative until its exact-head Ruff and full-pytest lineage is green.
5. `main` and `bnbgrs/ATHENA` remain read-only.
