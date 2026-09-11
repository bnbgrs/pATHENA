# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c`.
- Error worker entered this run at `postmerge/errors@298bbf8ab08a680cb5157651ffa293ce544c62e1`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `44201f9dd2c1378c98afccc9a30ddf18c98b2405`; UI `d55877cd353f7ee598df8213b9508fb143e51e15`.
- Latest exact-current canonical Quality: `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = IN_PROGRESS`. Windows path safety, Linux storage and Local-install are `SUCCESS`; Python quality is still in full pytest after specification validator, Ruff and mypy passed.
- Last completed Develop canonical Quality: `34539454111@4634bdf28c98bc114e0369701122818d474f99d9 = FAILURE`, isolated to one full-pytest failure (`1 failed, 4830 passed, 3 skipped`).
- `postmerge/errors@298bbf8ab08a680cb5157651ffa293ce544c62e1` had zero canonical Quality runs before the ledger mutation; after the ledger commit there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0036`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0036 isolated and advanced to verification

### ERR-0036 — stale UI typography assertion after intentional hierarchy promotion

Status `FIXED_PENDING_VERIFY`, P1 while it blocked canonical Develop.

Canonical Quality `34539454111@4634bdf28c98bc114e0369701122818d474f99d9` completed `FAILURE` only in `Python 3.12 quality -> Quality — pytest`; all Windows path/storage/durable-FS/runtime/ownership/adaptive-reserve/pypdf lanes, Linux storage and Local-install passed. Canonical diagnostics report exactly `1 failed, 4830 passed, 3 skipped`. The sole failing test was `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales`: it still asserted the pre-hierarchy typography tuple `(14, 11, 34)` while the intentionally integrated UI/design-token contract is `(15, 12, 42)`.

The current Develop head `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c` is exactly one commit ahead of that failing SHA. Its bounded repair changes only `tests/unit/test_pathena_design_system.py` plus `docs/agent_handoffs/integrator.md`; the stale exact tuple is aligned to `(15, 12, 42)`. No assertion is removed or generalized, no Skip/XFail is added, and no product, Storage, Recovery, Security or runtime behavior changes.

Canonical Quality `34544225707@7a6b9ee5...` is already green for Windows path safety, Linux storage, Local-install, specification validation, Ruff and mypy; full pytest remains in progress. Therefore no `FIXED` claim is made yet. If the run completes `SUCCESS`, close ERR-0036 as `FIXED`. If another pytest signature appears, create/deduplicate a separate exact-current cluster rather than weakening the typography assertion.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned.

Current Develop changes only the design-system test and Integrator handoff, so the previously current source-trace remains applicable: `SQLiteDatabase.start()` performs read-only preflight and then independently opens the writable SQLite connection by pathname, without carrying an identity token/handle/descriptor from preflight into writer establishment. Backend owns BE-052; Errors does not parallel-mutate it.

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop does not modify `emergency_reserve.py`, so the source-trace gap remains applicable: POSIX binds reserve mutation to an opened parent directory FD; the Windows/non-POSIX path still relies on pathname create/stat/unlink/fsync sequencing without carrying reserve-directory identity through mutation/release. Backend owns BE-046; Errors does not parallel-mutate it.

### ERR-0034 — native Windows durable-filesystem lane/platform-selection drift

Status remains `FIXED`.

Exact closure remains `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`; no exact-current reproduction of its platform-selection signature exists.

## Integrator handoff

- Current Develop: `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c`.
- Current canonical Quality: `34544225707 = IN_PROGRESS`; consume it before any further classification of ERR-0036.
- Previous exact failing canonical: `34539454111@4634bdf28c98bc114e0369701122818d474f99d9 = FAILURE`, exactly one stale design-system typography assertion; all other canonical jobs green.
- `ERR-0036 = FIXED_PENDING_VERIFY / P1`: bounded current Develop test-contract repair exists; no Errors product mutation; await exact-SHA canonical completion.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; no Errors product mutation.
- `ERR-0034 = FIXED`; do not reopen absent exact-current reproduction of its own signature.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
