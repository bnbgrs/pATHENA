# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@38586782fd9b615ecd4226a4b0afe674d5520978`.
- Error worker entered this run at `postmerge/errors@75f25a6c74f1631892e211454975c277663010ed`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop canonical Quality `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978 = SUCCESS`.
- Current Backend head is a handoff-only descendant of older worker-red history and has no exact-current canonical failure; its handoff explicitly marks broad Storage/Migration/WAL history HOLD and non-authoritative against current Develop.
- `postmerge/errors` had zero canonical Quality runs before the first mutation and still had zero after the ledger commit.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`.
- BLOCKED: none.

## Hard progress this run — ERR-0026 stale reclassification

### ERR-0026 — Backend Ruff/import-layout drift

Status: `STALE`, P2 when exactly reproduced.

The historical Backend worker failure carried Ruff `I001` at `src/athena/storage/schema.py:3:1`, but the current Backend head is now `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`, a documentation-only handoff refresh with no exact-current canonical reproduction of that signature. Under the error worker's current-evidence rule, that historical finding is no longer an active error merely because it once had priority.

Authoritative Develop `38586782fd9b615ecd4226a4b0afe674d5520978` completed canonical Quality `34473603186 = SUCCESS`, including Ruff. Develop/Error already carry the normalized schema import layout, while the current Backend handoff explicitly marks broad worker history HOLD/non-authoritative relative to Develop. Therefore no duplicate formatter or product mutation on `postmerge/errors` is justified.

Reopen `ERR-0026` only if the same Ruff/import-layout signature is reproduced on a then-current exact Backend or Develop SHA. This run changes status/evidence only; no production code, tests, assertions, guards, Storage, Recovery, Security or Runtime behavior changed.

## Lower-priority worker clusters held

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2 worker-local. Last worker diagnostics decompose into stale terminal-v41 assertions, duplicate-v41-table fixture collisions and downstream storage-bootstrap cascades, but the current Backend handoff explicitly places broad schema-v41 / Storage / Migration history on HOLD. Do not mechanically repair worker-only historical fixtures. Fresh exact-current evidence is required before this cluster can remain active in a later run.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending fresh exact-current Backend evidence. Preserve production exact-type fail-closed guards. Fresh exact-current evidence is required before mutation or closure.

## Recently closed clusters retained

### ERR-0032 — schema-reinitialization harness row-shape mismatch

`FIXED`, P1 when reproduced. Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` changed only the two `PRAGMA user_version` assertions to scalar comparison while retaining `sqlite3.Row`, both `initialize_schema()` calls and the same schema-version invariant. Canonical Quality `34468185990 = SUCCESS`. Newer Develop `38586782fd9b615ecd4226a4b0afe674d5520978` is also canonical-green at Quality `34473603186`; no recurrence is evidenced.

### ERR-0031 — Windows storage-bootstrap reserve path

`FIXED`, P1 when reproduced. Test-only POSIX `/tmp/...` reserve path was replaced with a platform-valid absolute path; authoritative Windows storage/path-safety verification is green. No production Storage/Recovery semantics were weakened.

## Integrator handoff

- Current Develop: `38586782fd9b615ecd4226a4b0afe674d5520978`.
- Current canonical Quality: `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978 = SUCCESS`.
- `ERR-0026 = STALE`; historical Backend Ruff evidence is not reproduced on the current Backend exact SHA, and current Develop Ruff is canonical-green.
- No current Develop P1 is evidenced.
- Do not absorb or repair broad Backend worker-only history as a unit; require fresh bounded exact-current reproduction first.
- On the next run consume then-current Develop/worker heads and canonical results first. If `ERR-0028` or `ERR-0029` still lacks current exact-SHA reproduction, reclassify one cluster at a time rather than preserving historical priority by default.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards.
