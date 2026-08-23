# Quality Gate incident: runs 1864-1896 and proactive pytest boundary fixes

Date: 2026-08-23
Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`

## Scope

This log records the primary gate failures observed while the branch was changing concurrently, plus stale test contracts identified proactively before pytest reached them. `bnbgrs/ATHENA` was not modified.

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

## Run 1896

Observed merge head: `e7aa2321af97bb681426572ae5e429c43f686e82` for branch head `934dd0a2335a2c70063291a03461cfbffb011991`.

- Specification validator: PASS (`63/63`).
- Ruff: FAIL with exactly one `F401`.
- mypy: not reached.
- pytest: not reached.

### Primary cause

`tests/unit/test_service_manager_interrupt_boundaries.py` imported `dataclasses.field` but never used it. The test only needs `dataclass` for the `_Service` fixture. This is a deterministic dead-import regression in a newly added boundary-test file, not a production-code failure.

### Fix

Commit `5482fbd898432d682baddfea409407080690cb1f` removes only the unused `field` import and leaves all three interrupt/shutdown tests unchanged.

## Proactive stale pytest contract: backup target symlink root

`backup_target_lock()` first rejects symbolic-link ancestors. Therefore a symlink supplied as the target root raises `BackupTargetBusyError` with `symbolic-link ancestor` before the later unavailable-directory branch can run. `tests/unit/test_backup_target_lock_boundaries.py` still expected `RuntimeError` matching `unavailable`.

- Classification: stale test expectation after security hardening; production behavior is the safer behavior.
- Fix: commit `b65763eccba5004f089991aaf72f5e727f272599` changes only the expected exception/message to the current fail-closed contract.
- Targeted local execution: NOT EXECUTABLE in this automation runtime because the isolated container cannot resolve `github.com`; verification is delegated to the repository CI gate.

## Proactive stale pytest contract: source-analysis negative ordinal

`SourceAnalysisWorkInput` delegates ordinal validation to `_require_int(..., minimum=0)`, whose stable message is `must be >= 0`. `tests/unit/test_source_analysis_models_boundaries.py` expected the obsolete phrase `must not be negative`.

- Classification: stale assertion text; no production defect.
- Fix: commit `7219da59f8cc3881740ed31b48f631d059cbd90d` changes only the regex expectation to `must be >= 0`.
- Targeted local execution: NOT EXECUTABLE for the same container network limitation; verification is delegated to CI.

## Safety / concurrency result

- All reads used `agent/pathena` or the exact observed run head.
- Mutations used current blob SHAs where an existing file was replaced.
- Stale writes were rejected (`409`) instead of overwriting parallel work.
- No force-push or history rewrite was used.
- `bnbgrs/ATHENA` remained untouched.

## Next gate slice

Re-evaluate the newest `agent/pathena` CI run. Required sequence: specification validator -> Ruff -> mypy -> pytest. Treat newly added parallel files as fresh potential primaries; do not attribute downstream failures to the already-resolved causes without a new reproducing run.
