# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@7fa2108d820cfc5b48a9f92d42ffa61697b74818`.
- Error worker entered this run at `postmerge/errors@aa603d87200b937efce37fcabfa1195a338b78a5`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `baae5dd42195eea1e2a7320d1be813431a3beecf`; UI `2ede7add4d70ee9f11ef2e05103504e9a1838a2a`.
- Exact current Develop canonical Quality: `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = IN_PROGRESS`; Windows path safety is already `SUCCESS`, including both Windows storage regressions and the dedicated native-Windows durable-filesystem regressions; Linux storage and Local install are `SUCCESS`; Python spec-validator/Ruff/mypy are green while full pytest is still running.
- Previous Develop canonical Quality: `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = FAILURE`, isolated to the Windows storage command after POSIX-only durable-fs contracts were included wholesale.
- Current Develop is a CI/Handoff-only correction over that exact red SHA. No production source or test assertion changed.
- `postmerge/errors@aa603d87200b937efce37fcabfa1195a338b78a5` had zero canonical Quality runs before mutation; after the ledger commit there were still zero queued/in-progress runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0034`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0034 root cause and focused verification

### ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

Status: `FIXED_PENDING_VERIFY`, P1.

The prior failing Develop `effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36` introduced no production or assertion change. It added the durable-fs modules wholesale to `windows-latest`. `tests/unit/test_durable_fs.py` contains explicit `test_posix_*` contracts that force POSIX-only `dir_fd` / directory-fsync semantics, and `tests/unit/test_durable_fs_parent_identity.py` is entirely POSIX-gated. The canonical failure was therefore a platform-selection error in CI coverage, not evidence of a native-Windows product regression.

Develop `7fa2108d820cfc5b48a9f92d42ffa61697b74818` applies the bounded CI-only correction: restore the prior Windows-applicable storage set; run `tests/unit/test_durable_fs.py -k "not test_posix"` in a dedicated `Run Windows durable filesystem regressions` step; leave the POSIX parent-identity module in Linux storage coverage. No Skip/XFail, assertion weakening, product mutation or Storage/Recovery/Security relaxation was introduced.

Focused exact-SHA evidence is now green: canonical Quality `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818` has completed the entire Windows path-safety job `SUCCESS`; `Run Windows storage path regressions = SUCCESS` and `Run Windows durable filesystem regressions = SUCCESS`. Linux storage and Local install are also green. Spec-validator, Ruff and mypy are green; full pytest is still running, so `FIXED` is not claimed yet.

Next run must consume `34522965434` first. If the final canonical conclusion is `SUCCESS`, close ERR-0034 as `FIXED`. If another failure appears, classify it separately unless the same platform-selection signature recurs.

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned. Current Develop CI changes do not alter `emergency_reserve.py`; the source-traced Windows directory-identity gap therefore remains applicable. No parallel Backend product mutation was made.

## Integrator handoff

- Current Develop: `7fa2108d820cfc5b48a9f92d42ffa61697b74818`.
- Current canonical Quality: `34522965434 = IN_PROGRESS`; Windows path safety, Linux storage and Local install are already `SUCCESS`; Python full pytest remains active after spec-validator/Ruff/mypy success.
- `ERR-0034 = FIXED_PENDING_VERIFY / P1`: root cause is CI platform-selection drift; exact native-Windows durable-fs step is now green on current Develop.
- Bounded correction is already on Develop; Errors made no product mutation.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned, unchanged.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
