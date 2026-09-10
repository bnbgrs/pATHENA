# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36`.
- Error worker entered this run at `postmerge/errors@d6ef65e11106aa6d43eba8c22c4173ee9c63ce60`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `49ff66eeb706695d0564bf87274a5f9087b8ef98`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop canonical Quality: `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = IN_PROGRESS`; Windows path safety is already `FAILURE` at `Run Windows storage path regressions`; Linux storage and Local install are `SUCCESS`; Python spec-validator/Ruff/mypy are green and full pytest is still running.
- Previous Develop canonical Quality: `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = SUCCESS`.
- Current Develop is one CI/Integrator-only commit over that exact green SHA. No production source or test assertion changed.
- `postmerge/errors@d6ef65e11106aa6d43eba8c22c4173ee9c63ce60` had zero canonical Quality runs before mutation; after the ledger commit there were still zero queued/in-progress runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0034`.
- IN_PROGRESS: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0034 current canonical isolation

### ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

Status: `OPEN`, P1, current canonical integration blocker.

Current canonical Quality `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36` has already failed the Windows path-safety job specifically at `Run Windows storage path regressions`. Linux storage regressions and Local install smoke are green on the same SHA; the Python job has passed specification validation, Ruff and mypy while full pytest remains active.

The exact current Develop commit changes no production or assertion code. Relative to canonical-green `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`, it only adds `tests/unit/test_durable_fs.py` and `tests/unit/test_durable_fs_parent_identity.py` to the Windows storage command plus Integrator documentation. Every test in `test_durable_fs_parent_identity.py` explicitly skips unless `os.name == "posix"`, so it executes no substantive Windows test. The newly exposed Windows failure is therefore isolated to `tests/unit/test_durable_fs.py` interacting with native Windows behavior.

The available exact-SHA evidence does not yet expose the individual pytest failure/exception while the canonical run is still active, so no speculative product or test mutation was made. On the next run, consume the completed canonical result first and obtain the exact failing-test/exception evidence if available. Then fix only that root cause and run the smallest focused native-Windows verification. Preserve HANDLE-bound rename, write-through durability, reparse/symlink rejection, directory identity and Storage/Recovery fail-closed semantics; no Skip/XFail or assertion weakening.

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned. The new canonical failure is not currently attributed to ERR-0033 because the added Windows coverage is `durable_fs`, not the emergency-reserve adversarial directory-swap contract. No parallel Backend product mutation was made.

## Integrator handoff

- Current Develop: `effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36`.
- Current canonical Quality: `34516879382 = IN_PROGRESS`; Windows path safety already failed at `Run Windows storage path regressions`.
- `ERR-0034 = OPEN / P1`: exact regression is confined by the CI-only delta to `tests/unit/test_durable_fs.py` on native Windows; `test_durable_fs_parent_identity.py` is entirely POSIX-gated on Windows.
- Exact individual failing test/exception: not yet evidenced by the available run data; do not patch speculatively.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned, unchanged by this run.
- Product mutation by Errors: none.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
