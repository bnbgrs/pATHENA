# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@1b83466490291fe07dd3d99dd476d0cb6290d307`.
- Error worker entered this run at `postmerge/errors@f493a50e999fcea5811e86b22338b1fcaff137da`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `ac3d3c851186b8caa152d4a22815bd1390998e55`.
- Latest exact-current canonical Quality: `34548505498@1b83466490291fe07dd3d99dd476d0cb6290d307 = IN_PROGRESS`; no new failure is inferred while it is running.
- Last completed Develop canonical Quality: `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.
- `postmerge/errors@f493a50e999fcea5811e86b22338b1fcaff137da` had zero canonical Quality runs before the ledger mutation; after the ledger commit there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0036 closed on exact canonical evidence

### ERR-0036 — stale UI typography assertion after intentional hierarchy promotion

Status `FIXED`.

Canonical Quality `34539454111@4634bdf28c98bc114e0369701122818d474f99d9` had previously failed only in `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales`: the test still asserted `(14, 11, 34)` while the intentionally integrated typography contract was `(15, 12, 42)`.

The bounded repair on `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c` changed only that stale exact tuple plus Integrator documentation; it did not remove/generalize an assertion, add Skip/XFail, or alter product/runtime/Storage/Recovery/Security semantics.

Exact closure evidence is now complete: canonical Quality `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`. `ERR-0036` is therefore closed as `FIXED` and must not be reopened without reproduction of the same signature on a then-current exact SHA.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned.

The current Backend handoff still confirms the source-trace gap: `SQLiteDatabase.start()` performs read-only preflight and then independently opens the writable SQLite connection by pathname, without carrying a verified identity token/handle/descriptor from preflight into writer establishment. Errors does not parallel-mutate Backend-owned product code. Closure requires a bounded candidate plus focused cross-platform identity-swap regression evidence.

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

The current Backend handoff still confirms the source-trace gap: POSIX binds reserve mutation to an opened parent directory FD; the Windows/non-POSIX path remains pathname-based across create/stat/unlink/fsync and does not carry reserve-directory identity through mutation/release. Errors does not parallel-mutate Backend-owned product code. Closure requires a bounded candidate plus focused native-Windows adversarial directory-swap evidence.

### ERR-0034 — native Windows durable-filesystem lane/platform-selection drift

Status remains `FIXED`.

Exact closure remains `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`; no exact-current reproduction of its platform-selection signature exists.

## Integrator handoff

- Current Develop: `1b83466490291fe07dd3d99dd476d0cb6290d307`.
- Current canonical Quality: `34548505498 = IN_PROGRESS`; consume it before classifying any new Develop failure.
- Last completed canonical: `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.
- `ERR-0036 = FIXED`: exact canonical closure achieved; do not reopen absent exact-current recurrence of its own signature.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; no Errors product mutation.
- `ERR-0034 = FIXED`; do not reopen absent exact-current reproduction of its own signature.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
