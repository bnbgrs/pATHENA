# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@cbd0f7036feebc92443b12dec79ac840834dea2d`.
- Error worker entered this run at `postmerge/errors@d6eee816789c8dc0fa421ac618b8793f80862099`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `b411e75a3481649b33edc70b74c22f64ab71c6d4`; UI `980729bc2d019b69169192ab3be76fb7b743e6f4`.
- Latest exact current Develop canonical Quality: `34529111566@cbd0f7036feebc92443b12dec79ac840834dea2d = IN_PROGRESS`; no failure is inferred from the incomplete run.
- Closure evidence consumed first: `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`, including full pytest, Windows path safety, native-Windows durable-filesystem regressions, Linux storage and Local install.
- `postmerge/errors@d6eee816789c8dc0fa421ac618b8793f80862099` had zero canonical Quality runs before the ledger mutation; after the ledger commit there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0034 closure

### ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

Status: `FIXED`, P1 when reproduced.

The failing exact SHA `effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36` had mixed explicit POSIX durable-filesystem contracts into the native Windows storage lane. Develop `7fa2108d820cfc5b48a9f92d42ffa61697b74818` applied only the bounded CI platform-selection correction: Windows executes the Windows-applicable durable-FS cases while the POSIX parent-identity contracts remain in Linux coverage. No Skip/XFail, assertion weakening, product mutation or Storage/Recovery/Security relaxation was introduced.

The previously pending exact canonical verification has now completed: `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`. Full pytest, Windows path safety, `Run Windows storage path regressions`, `Run Windows durable filesystem regressions`, Linux storage and Local install all passed. `ERR-0034` is therefore closed as `FIXED`.

Reopen only if the same platform-selection signature is reproduced on a then-current exact SHA. A different failure gets a new root-cause cluster.

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

The current Backend handoff still marks BE-046 `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE` and has no bounded product candidate. Errors therefore did not parallel-mutate Backend product code. Closure still requires a bounded Backend candidate plus focused native-Windows evidence proving reserve-directory identity remains bound across create/release mutation, including an adversarial directory-swap boundary.

## Integrator handoff

- Current Develop: `cbd0f7036feebc92443b12dec79ac840834dea2d`.
- Current canonical Quality: `34529111566 = IN_PROGRESS`; consume it before deriving any new current failure.
- `ERR-0034 = FIXED`: exact closure SHA `7fa2108d820cfc5b48a9f92d42ffa61697b74818`, canonical Quality `34522965434 = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; no Errors product mutation.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
