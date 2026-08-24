# Quality Gate run 1819 — first mypy slice after Ruff PASS

## Scope

Repository: `bnbgrs/pATHENA` only.

Observed workflow run: `32642510482` / run number `1819`.

## Gate state

- Specification validator: **PASS**, 63/63.
- Ruff: **PASS** (`All checks passed!`).
- mypy: **FAIL**, four primary errors in three files, 289 source files checked.
- pytest: **NOT EXECUTED** because the fail-fast gate stopped at mypy.

This is the first observed run in this sequence that cleared Ruff and exposed the mypy layer.

## Primary error 1–2 — recovery row counts

File: `src/athena/jobs/recovery.py`

mypy reported that `paused_count` and `cancelled_count` were `Any | None` when passed to `RestoredJobRecoverySummary`, which requires `int`.

Root cause: runtime validation in a loop did not provide a type-narrowing result that mypy could carry to the constructor.

Fix: validate each raw `rowcount` through a typed `_require_rowcount(value: object) -> int` helper, retaining the existing fail-closed checks for bool, non-int, negative or missing values.

Fix commit: `c6efb6b9bd4b5c1472e27da71a7fd542b01f8f00`.

## Primary error 3 — required/optional RuntimePaths loop variable

File: `src/athena/storage/paths.py`

mypy reported an incompatible assignment because one loop variable was inferred as `Path` while a later loop reused the same name for `Path | None` values.

Root cause: variable-name reuse across two differently typed validation loops.

Fix: use distinct `required_value` and `optional_value` variables. Runtime validation behavior is unchanged.

Fix commit: `2ac85daa1a65f8e26ca251c8f7a3403602bf224d`.

## Primary error 4 — Qt QByteArray conversion

File: `src/athena/desktop/pathena_empty_state_guidance_3400.py`

mypy reported that no `bytes()` overload accepts PySide's `QByteArray` returned by `QDynamicPropertyChangeEvent.propertyName()`.

Root cause: runtime-compatible conversion syntax was not compatible with the PySide type stubs under strict mypy.

Fix: compare `event.propertyName().data()` directly with `b"pathenaUiState"`.

Fix commit: `08a452005d171461eaaef5bae56ceb0146dbadf2`.

## Verification requirement

The fixes above are committed but are not marked PASS until a subsequent GitHub Actions quality run confirms them. The next authoritative sequence is:

1. Specification validator remains green.
2. Ruff remains green.
3. mypy re-runs and either passes or exposes the next primary type error.
4. Only if mypy passes may pytest be classified; until then pytest remains **NOT EXECUTED**.

No unobserved test or CI result is claimed here.
