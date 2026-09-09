# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Error worker pre-run head: `postmerge/errors@4e31fec500e4b51dbaaf38ae7956afeec8354995`.
- Current workers: Spec/Core `eb352369d5477c8b67fab5a76811916bfa28769b`; Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`; UI `3b0c11a16165036d5e8254ed59233408e077b782`.
- Exact Develop parent `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` is canonical green by Quality `34353904087 = SUCCESS`.
- Current Develop Quality `34360516307@c830b96a12d25914c52a0abc7749a6724b19cfae = IN_PROGRESS`.
- Current Backend Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9 = IN_PROGRESS`.
- No competing canonical run was started. `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / top-level FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 protected-source-blob subcluster

The current Backend worker owns a bounded harness-only repair on exact candidate `b2a2a20873390098f98a9125222ae5594a9d6cc9`.

`tests/unit/test_protected_source_blob.py::test_fresh_schema_is_v33_and_allows_protected_blob_records` already followed the actual `SCHEMA_VERSION`, but its fresh-schema metadata tuple still expected the predecessor v40 `GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID`. Backend v41 makes the current migration `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`, so the harness assertion was internally stale while the production contract was consistent.

The Backend candidate replaces only that stale migration-id expectation. Its handoff explicitly preserves protected-source encryption, persistence, archive replication, restart locking, fail-closed integrity, production schema/migrations, Storage, Recovery, Network/TOR, packaging and runtime guards. This is therefore an Error-ledger-owned verification target, not a reason for this worker to duplicate Backend product changes.

Subcluster status is `FIXED_PENDING_VERIFY`: canonical Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9` is currently `IN_PROGRESS`. Do not promote to `FIXED` from commit intent or aggregate status; consume exact assertion-level PASS first. If it fails, repair only the demonstrated harness defect.

Overall `ERR-0028` remains `IN_PROGRESS`; previously closed grounded-response-receipt, backup-retention, operational-error physical-cleanup and deletion-ledger subclusters remain closed absent exact-current regression.

## Other active root causes

### ERR-0026 — Backend Ruff I001

Still `IN_PROGRESS` on the Backend worker until exact Backend Ruff PASS exists. Exact-green Develop `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` already carries the formatter-clean schema state, so this is not by itself a current Develop blocker.

### ERR-0029 — WAL exact-type harness drift

Still `IN_PROGRESS`. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

### ERR-0027 — schema contract boundary

Remains `FIXED` from exact Backend 5/5 PASS evidence. Do not reopen absent exact-current regression.

## Integrator handoff

- Do not start a competing canonical Quality while `34360516307@c830b96a12d25914c52a0abc7749a6724b19cfae` or Backend `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9` is running.
- Develop parent `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` is exact canonical green.
- `ERR-0028/protected-source-blob`: `FIXED_PENDING_VERIFY` on exact Backend `b2a2a20873390098f98a9125222ae5594a9d6cc9`; require assertion-level exact PASS before closure.
- Overall Backend v41 / Research-dependent integration remains held for remaining independent `ERR-0028` / `ERR-0029` reds until exact evidence clears them.
- `ERR-0026` remains Backend-worker-local unless a current Develop regression reproduces it.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume completed exact Backend Quality `34357920394@b2a2a20873390098f98a9125222ae5594a9d6cc9`. Close only the protected-source-blob subcluster if its focused/assertion-level evidence is green; otherwise keep it active and fix only the demonstrated harness failure. Also consume Develop `34360516307@c830b96a12d25914c52a0abc7749a6724b19cfae` before making any current-Develop readiness claim.