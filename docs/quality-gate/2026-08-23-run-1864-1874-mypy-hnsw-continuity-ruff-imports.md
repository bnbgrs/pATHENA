# Quality Gate incident: runs 1864-1874

Date: 2026-08-23
Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`

## Scope

This log records the primary gate failures observed while the branch was changing concurrently. `bnbgrs/ATHENA` was not modified.

## Run 1864

Observed merge head: `0272a269f05ca2e2ab1a62346c378ff8d7065dc3` for branch head `f4c3b2068f2bfa091c862dded3fa9253fe50925d`.

- Specification validator: PASS (`63/63`).
- Ruff: PASS.
- mypy: FAIL with 14 errors in two files.
- pytest: not reached because the gate is fail-fast.

### Primary causes

1. `src/athena/desktop/pathena_operational_continuity_3800.py`
   - Eight `call-overload` errors came from converting values retrieved from `dict[str, object]` directly with `int(...)`.
   - Root cause classification: static type narrowing missing at the presentation-state restore boundary.
   - Safe correction: decode snapshot integers through an explicit `isinstance(value, int)` helper rather than trusting arbitrary `object` values.

2. `src/athena/retrieval/hnsw.py`
   - Six `unreachable` errors came from applying `numbers.Real` runtime checks directly to values whose static type was already `float`.
   - Root cause classification: runtime validation was expressed in a form incompatible with mypy's static narrowing model.
   - Safe correction: centralize runtime numeric validation behind an `object`-typed helper and return a normalized `float`; preserve rejection of booleans, non-numeric values, and non-finite values.

Concurrent branch work subsequently implemented both correction patterns before this log was written. The SHA guard also rejected an attempted stale write to `hnsw.py`, proving that parallel changes were not overwritten.

## Run 1874

Observed merge head: `9a96197d2c25aa9a3964f7c48907ebbb8706e2e1` for branch head `99dc03698fa50f81ab16b906bdbdf3c16445cebc`.

- Specification validator: PASS (`63/63`).
- Ruff: FAIL with exactly two `I001` import-order errors.
- mypy: not reached.
- pytest: not reached.

### Primary causes

1. `src/athena/desktop/pathena_microinteraction_3900.py`
   - `QApplication` appeared before `QAbstractButton` in the `PySide6.QtWidgets` import list.
   - Classification: deterministic import-order formatting regression in a newly added UI refinement module.

2. `src/athena/desktop/pathena_operational_continuity_3800.py`
   - QtCore import members were not in Ruff/isort canonical order.
   - Classification: deterministic import-order formatting regression introduced while the mypy boundary fix was being extended.

The branch then advanced and at least the microinteraction import file changed by one line, consistent with an import-only correction. A second stale write attempt was rejected by GitHub because the file had changed concurrently; no force update was used.

## Safety / concurrency result

- All reads used `agent/pathena` or the exact observed run head.
- Mutations attempted with blob-SHA preconditions were rejected when stale (`409`) rather than overwriting parallel work.
- No force-push or history rewrite was used.
- `bnbgrs/ATHENA` remained untouched.

## Next gate slice

Re-evaluate the newest `agent/pathena` CI run. Required sequence: specification validator -> Ruff -> mypy -> pytest. Treat newly added parallel files as fresh potential primaries; do not attribute downstream failures to the already-resolved 1864/1874 causes without a new reproducing run.
