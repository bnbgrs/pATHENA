# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@0d3ca68731ded061b0720bd94d649f3dfed59a45`.
- Error worker entered this run at `postmerge/errors@df3f63e0c0c717f0bbd8a4388535c5cd645e83ee`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Latest exact Develop canonical Quality is `34486592055@0d3ca68731ded061b0720bd94d649f3dfed59a45 = IN_PROGRESS`. At inspection time Linux storage regressions and Local install smoke/pypdf were green; Windows path safety and Python quality were still running and no exact-SHA failure was yet evidenced.
- Last completed Develop canonical Quality is `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978 = SUCCESS`.
- Current Backend head is a handoff-only descendant of older worker-red history and has no exact-current canonical reproduction; its handoff explicitly marks broad Storage/Migration/WAL history HOLD and non-authoritative against current Develop.
- `postmerge/errors` had zero canonical Quality runs before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`.
- BLOCKED: none.

## Hard progress this run — ERR-0028 stale reclassification

### ERR-0028 — Backend v41 legacy schema fixture/current-version drift

Status: `STALE`, P2 when exactly reproduced.

The last Backend diagnostics that supported this cluster belong to older worker SHAs. They decomposed failures into terminal-current-schema assertions, duplicate-v41-table fixture collisions and downstream Storage-startup cascades on worker-only schema history. That historical evidence is not authoritative for the current worker head.

Current Backend is `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`. The newest Backend canonical Quality remains `34455900467@7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2 = FAILURE`; there is no canonical run reproducing an ERR-0028 signature on current Backend `a5e28d3c...`. The current Backend handoff explicitly labels broad schema-v41 / Storage / Migration / WAL history `HOLD / NOT READY` and non-authoritative relative to Develop.

The last completed authoritative Develop baseline `38586782fd9b615ecd4226a4b0afe674d5520978` is canonical-green at Quality `34473603186`. A newer Develop Quality `34486592055@0d3ca68731ded061b0720bd94d649f3dfed59a45` is already running; at inspection time its Linux Storage and Local-install/pypdf jobs were green and no failure had yet been evidenced. Therefore no current exact-SHA evidence justifies keeping ERR-0028 active.

No product code, migration, fixture, assertion or guard was changed. In particular, do not add `IF NOT EXISTS` to the v40→v41 production migration, swallow `OperationalError`, or weaken Storage/Recovery fail-closed behavior. Reopen only after a specific ERR-0028 signature is reproduced on a then-current exact Backend or Develop SHA.

## Remaining worker cluster held

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending fresh exact-current Backend evidence. Preserve production exact-type fail-closed guards. On the next eligible run, re-check current Backend/Develop exact-SHA evidence before deciding whether this cluster remains active; do not preserve historical priority by default.

## Recently closed/stale clusters retained

### ERR-0026 — Backend Ruff/import-layout drift

`STALE`, P2 when exactly reproduced. Historical Backend Ruff `I001` evidence is not reproduced on current Backend exact SHA, while the last completed authoritative Develop Quality is green including Ruff. No duplicate formatter/product mutation is justified.

### ERR-0032 — schema-reinitialization harness row-shape mismatch

`FIXED`, P1 when reproduced. Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` changed only the two `PRAGMA user_version` assertions to scalar comparison while retaining `sqlite3.Row`, both `initialize_schema()` calls and the same schema-version invariant. Canonical Quality `34468185990 = SUCCESS`; newer completed Develop `38586782...` is also canonical-green.

### ERR-0031 — Windows storage-bootstrap reserve path

`FIXED`, P1 when reproduced. Test-only POSIX `/tmp/...` reserve path was replaced with a platform-valid absolute path; authoritative Windows storage/path-safety verification is green. No production Storage/Recovery semantics were weakened.

## Integrator handoff

- Current Develop: `0d3ca68731ded061b0720bd94d649f3dfed59a45`.
- Current canonical Quality: `34486592055@0d3ca68731ded061b0720bd94d649f3dfed59a45 = IN_PROGRESS`; consume it before any failure claim or new Develop work.
- Last completed Develop canonical: `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978 = SUCCESS`.
- `ERR-0028 = STALE`; its historical Backend v41 fixture/current-version failures are not reproduced on current Backend exact SHA, and the Backend handoff marks that broad lineage HOLD/non-authoritative.
- `ERR-0029` remains the only IN_PROGRESS historical worker cluster, pending fresh current exact-SHA evidence.
- No current Develop P1 failure was evidenced at inspection time.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards.
