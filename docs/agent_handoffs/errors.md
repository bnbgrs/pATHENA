# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@3330a0092eaddf58fd3a4fdcb7128f77f01b0301`.
- Error worker entered this run at `postmerge/errors@6477760a9fd2e849d20d128e62390ba27458a710`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `338e4514d144f4701e52515c0196e0f968f5db47`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop canonical Quality: `34492275924@3330a0092eaddf58fd3a4fdcb7128f77f01b0301 = SUCCESS`, including Linux storage regressions, Python Quality (spec validator/Ruff/mypy/full pytest), Windows path safety and Local install smoke.
- Current Backend `338e4514d144f4701e52515c0196e0f968f5db47` has zero canonical Quality runs. Its current handoff says broad historical schema-v41 / Storage / Migration / WAL worker history is non-authoritative against current Develop and any surviving delta must be freshly re-proven as a bounded current-Develop gap.
- `postmerge/errors@6477760a9fd2e849d20d128e62390ba27458a710` had zero canonical Quality runs before mutation; after the ledger commit `6a558de97b01160c9c7e8734843a6d125609cf8a` there were also zero canonical runs, so this handoff update did not supersede an active run.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0029 stale reclassification

### ERR-0029 — WAL exact-type harness drift

Status: `STALE`, P2 when exactly reproduced.

Historical worker diagnostics associated this cluster with WAL harness collaborators that did not satisfy production exact-type fail-closed guards. That evidence belongs to older worker lineage and is not authoritative for the current exact Backend head.

Current Backend is `338e4514d144f4701e52515c0196e0f968f5db47`. GitHub reports zero canonical Quality runs for that exact SHA, so there is no current Backend reproduction of the ERR-0029 WAL collaborator/runtime-guard signature. The current Backend handoff explicitly says broad historical WAL/Storage/Migration worker history is non-authoritative relative to current Develop and requires any surviving delta to be re-proven as a bounded current-Develop gap before mutation or integration.

Current Develop `3330a0092eaddf58fd3a4fdcb7128f77f01b0301` is exact canonical-green at Quality `34492275924`, including full pytest, Windows path safety, Linux Storage and Local-install smoke. No current Develop WAL/runtime-guard failure is evidenced.

Under the current-evidence rule, ERR-0029 therefore cannot remain `IN_PROGRESS` solely because an older worker SHA once reproduced related failures. No harness, WAL, runtime, Storage, Recovery or Security code was changed. Production exact-type fail-closed guards remain authoritative and must not be weakened. Reopen only after the same signature is reproduced on a then-current exact Backend or Develop SHA.

## Retained stale/closed clusters

### ERR-0028 — Backend v41 legacy schema fixture/current-version drift

`STALE`, P2 when exactly reproduced. Historical fixture/current-version evidence is not reproduced on current Backend exact SHA; current Backend broad schema-v41/Storage/Migration/WAL history is explicitly non-authoritative against green Develop. No migration or fixture mutation is justified.

### ERR-0026 — Backend Ruff/import-layout drift

`STALE`, P2 when exactly reproduced. Historical Backend Ruff `I001` evidence is not reproduced on current Backend exact SHA, while current authoritative Develop Quality is green including Ruff. No duplicate formatter/product mutation is justified.

### ERR-0032 — schema-reinitialization harness row-shape mismatch

`FIXED`, P1 when reproduced. Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` changed only the two `PRAGMA user_version` assertions to scalar comparison while retaining `sqlite3.Row`, both `initialize_schema()` calls and the same schema-version invariant. Canonical Quality `34468185990 = SUCCESS`; current Develop is also canonical-green.

### ERR-0031 — Windows storage-bootstrap reserve path

`FIXED`, P1 when reproduced. Test-only POSIX `/tmp/...` reserve path was replaced with a platform-valid absolute path; authoritative Windows storage/path-safety verification is green. No production Storage/Recovery semantics were weakened.

## Integrator handoff

- Current Develop: `3330a0092eaddf58fd3a4fdcb7128f77f01b0301`.
- Current canonical Quality: `34492275924@3330a0092eaddf58fd3a4fdcb7128f77f01b0301 = SUCCESS`.
- `ERR-0029 = STALE`: current Backend `338e4514d144f4701e52515c0196e0f968f5db47` has zero canonical runs and no current exact-SHA WAL collaborator/runtime-guard reproduction; current Backend handoff places broad historical WAL lineage on non-authoritative HOLD.
- No currently active error remains in the Error Ledger. This is not a blanket defect-free claim: new exact-SHA failures or current-source root-cause evidence can open a new cluster on future runs.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and WAL exact-type fail-closed semantics.
