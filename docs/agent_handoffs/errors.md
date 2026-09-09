# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@8b6023b64991489f3570f9c99a0feb89f5bbe500`.
- Error worker pre-run head: `postmerge/errors@7e83a9ad6045f547ef1670431d7af6775a21c0b3`.
- Current workers: Spec/Core `850b631007ba3f359b9b16c619c692d853d75663`; Backend `0f07617e6982f029eb6210e7b7f5a28fab853ffe`; UI `4fad529c471c783e62d6029d6ea72a2147727196`.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 protected-source fixture candidate consumed

Backend advanced from `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a` to exact head `0f07617e6982f029eb6210e7b7f5a28fab853ffe`, whose product parent `f3a0ca7f763ce554d60f5fd5ffa3fc05a6ec5f12` is a bounded harness-only repair in `tests/unit/test_protected_source_semantic_schema.py`. It updates stale v40/current-version expectations to v41 and removes the v41-only `research_delta_boundaries` table when reconstructing the v38 predecessor fixture. Production schema/migration/Storage/WAL/Recovery code is unchanged.

Exact canonical Quality `34324159266@0f07617e6982f029eb6210e7b7f5a28fab853ffe` completed `FAILURE`. Windows path safety, Local install smoke and Linux storage regressions passed. In Python quality, specification validator and mypy passed; Ruff and full pytest failed. Canonical diagnostics artifact `10093816318` was uploaded successfully.

This advances the protected-source ERR-0028 subcluster from “candidate awaiting exact run” to “exact run consumed, assertion-level status still unresolved”. The overall red run is not evidence that the two protected-source tests failed, and it is not evidence that they passed. Therefore no false FIXED claim is made. The subcluster remains `IN_PROGRESS` pending readable assertion-level evidence from the exact candidate or a direct successor.

## Other active root causes

### ERR-0026 — schema Ruff I001

Exact formatter evidence remains authoritative: one autofixable Ruff I001 over the import block in `src/athena/storage/schema.py`. The new Backend exact run is still Ruff red, so ERR-0026 remains `IN_PROGRESS`. Do not commit another hand-sorted import guess; require exact Ruff 0.15.22 autofix output plus focused Ruff PASS.

### ERR-0029 — WAL exact-type harness drift

Production exact-type fail-closed guards remain authoritative. No current focused/assertion-level PASS has been consumed for remaining WAL harness cases; keep `IN_PROGRESS`.

### ERR-0027 — v41 schema-facade re-export

Current Backend lineage visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration.
- Exact Backend head: `0f07617e6982f029eb6210e7b7f5a28fab853ffe`; canonical Quality `34324159266 = FAILURE`.
- `ERR-0028` protected-source candidate product commit: `f3a0ca7f763ce554d60f5fd5ffa3fc05a6ec5f12`; status `IN_PROGRESS` pending assertion-level exact evidence. Do not infer subcluster PASS/FAIL from aggregate pytest red.
- `ERR-0026`: still Ruff red on exact Backend head; require formatter-generated fix and focused Ruff PASS.
- `ERR-0027`: require focused schema-contract verification before closure.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume assertion-level diagnostics for canonical artifact `10093816318` / Quality `34324159266` and classify only the protected-source ERR-0028 subcluster. If those exact tests pass, close only that subcluster; if they fail, repair only the demonstrated harness defect. Do not start a competing canonical run while an exact-head run is queued/in-progress.