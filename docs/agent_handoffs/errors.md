# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Error worker pre-run head: `postmerge/errors@1f9c41d7dd88945876ab0eb2a9893a05a3a1117e`.
- Current workers: Spec/Core `a9b1cb8b3354c9afdc206fbf435af0d1bf5d451f`; Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`; UI `90a51e111851f80c5e2388c11c4026c6ec62fa09`.
- Exact current Develop Quality `34360516307@c830b96a12d25914c52a0abc7749a6724b19cfae = SUCCESS`.
- Exact current Backend Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9 = FAILURE`; Windows path safety, Linux storage and Local install smoke are green, Python Quality remains red on Ruff/full pytest.
- Exact Backend diagnostics artifact `10108241562` was consumed this run.
- No competing canonical run was started. `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / top-level FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 protected-source-blob subcluster

Status: `FIXED` on exact Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`.

Canonical Quality `34357920394` completed failure overall, so aggregate run status was not used as closure. Its exact diagnostics artifact `10108241562` was downloaded and consumed at assertion level. `pytest.txt` records:

`tests/unit/test_protected_source_blob.py ...... [78%]`

That is six of six protected-source-blob tests passing on the exact candidate. The bounded Backend repair changed only the stale v40 current-migration expectation to `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`; no production schema, Storage, Recovery, encryption, archive replication, restart locking, integrity or runtime guard was weakened or changed.

The remaining exact Backend failures are independent. Diagnostics still show stale/current-version legacy fixture failures in `test_knowledge_schema.py` and `test_protected_content.py`, plus migration-fixture collisions such as `sqlite3.OperationalError: table research_delta_boundaries already exists`. Those remain under overall `ERR-0028`; they do not reopen this closed protected-source-blob subcluster.

Previously closed grounded-response-receipt, backup-retention, operational-error physical-cleanup and deletion-ledger subclusters also remain closed absent exact-current regression.

## Other active root causes

### ERR-0026 — Backend Ruff

Still `IN_PROGRESS` on the Backend worker: exact Backend Quality `34357920394` remains Ruff red. Current Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` is exact canonical green, so this is not by itself a current Develop blocker. Require exact Backend focused/canonical Ruff PASS before closure.

### ERR-0029 — WAL exact-type harness drift

Still `IN_PROGRESS`. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

### ERR-0027 — schema contract boundary

Remains `FIXED` from exact Backend 5/5 PASS evidence. Do not reopen absent exact-current regression.

## Integrator handoff

- Current Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` is exact canonical green by Quality `34360516307`.
- `ERR-0028/protected-source-blob` is `FIXED` on exact Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`, backed by assertion-level 6/6 PASS from artifact `10108241562`.
- Overall Backend v41 / Research-dependent integration remains held for independent `ERR-0028` / `ERR-0029` reds and Backend Ruff until exact evidence clears them.
- `ERR-0026` remains Backend-worker-local unless a current Develop regression reproduces it.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Select the highest still-active independent Backend root-cause from exact diagnostics. Do not reopen the protected-source-blob subcluster without a new exact-current regression. Prioritize a primary migration-fixture/current-version cluster over cascaded `storage-bootstrap` failures, and keep production Storage/Recovery/WAL guards fail-closed.