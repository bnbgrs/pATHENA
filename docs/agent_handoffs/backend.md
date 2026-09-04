# pATHENA Backend & Systems Handoff

## Baseline

- Current integration base reviewed: `develop/pathena-next@5d7061678afd2e2f6195d5a3ce6e15cde2797007`.
- Worker branch: `postmerge/backend`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.
- History-preserving NON-FORCE synchronization merge: `e336c32b39138b4067bb4aa84520bb1def65eedf`, with parents `e5b021ac3e99fc4ef8bf15f3d790c5220799fedd` and current Develop `5d7061678afd2e2f6195d5a3ce6e15cde2797007`.
- Synchronization tree starts from exact current Develop and overlays only Backend-owned Research boundary files plus this handoff; no foreign worker or main mutation was performed.

## READY — Research source-types runtime boundary

Product/test commit `5f9f3713c53c16375453c4a0f6be9a9a086700d6` introduces `_stable_source_types(values: object)`, rejects scalar text-like and non-Sequence containers, retains the per-element `SourceType` guard, and preserves deterministic `.value` sorting/deduplication before actor setup, snapshot pinning or durable job creation.

Canonical ATHENA Quality Gate `33840621670` on synchronized candidate `75ae07fdb0bf72c100cc8401f7881ffa03b96b03` completed `success` with real jobs. The earlier zero-job run `33837041846` remains explicitly non-evidence.

Integrator status: READY_FOR_BOUNDED_REVIEW. Independently isolate/review the source-types product/test delta rooted at `5f9f3713c53c16375453c4a0f6be9a9a086700d6`; do not treat synchronization or documentation commits as product behavior.

## Current backend slice — WAL checkpoint runtime-mode boundary

Current `WalMaintenanceService._checkpoint()` interpolates its `mode` into `PRAGMA wal_checkpoint(...)`. Static `CheckpointMode` typing is not a runtime security boundary, so a malformed runtime value could reach SQLite before the existing `WalCheckpointResult` mode validation.

Product commit `536728afe987af35884318641f2250b1f63fefdf` adds an explicit allow-list guard for exactly `PASSIVE` and `TRUNCATE` before obtaining the connection or executing SQL. Test commit `72b73df19b8152146e02aa42922f585ca72ed582` adds a regression asserting an invalid runtime mode fails with `WalMaintenanceError`.

Canonical Quality `33844840855` was triggered on exact product/test head `72b73df19b8152146e02aa42922f585ca72ed582`; at this handoff write it is pending and therefore no PASS/READY claim is made for the WAL slice.

## Current queue re-trace

- `BE-038` queue wording is stale on current Develop: Windows durable publication already uses bound source/destination HANDLEs and `NtSetInformationFile` relative rename in `storage/durable_fs.py`.
- `BE-020` is stale on current Develop: `chat/generation.py` already invokes `assert_runtime_model_matches_signature()` before provider generation from a ContextPackage.
- `BE-021` is stale on current Develop: `ContextPackage.generation_temperature()` already catches `OverflowError` and keeps the error inside `ContextPackageError`.
- The WAL runtime-mode guard is therefore a current, independently reproduced system hardening slice rather than mutation against stale queue evidence.

## Retained invariants

- No silent Tor to Direct fallback and no new Direct authorization path.
- No external transport retry, cryptography, redirect, provenance, audit, fsync or transactional Source-finalization change.
- Research persistence, snapshot pinning and durable job semantics are unchanged for valid input.
- WAL maintenance remains SQLite-owned; PASSIVE remains the automatic mode and TRUNCATE remains explicitly idle-confirmed only.
- No skip/XFail, assertion weakening or guard weakening.

## Integrator handoff

- READY: Research source-types boundary `5f9f3713c53c16375453c4a0f6be9a9a086700d6`, backed by canonical green `33840621670` on synchronized candidate `75ae07fdb0bf72c100cc8401f7881ffa03b96b03`.
- NOT_READY: WAL runtime-mode boundary `536728afe987af35884318641f2250b1f63fefdf` + test `72b73df19b8152146e02aa42922f585ca72ed582` until canonical Quality completes green on an exact head containing both changes.

## Next backend slice

First consume the canonical WAL result. If green, mark the WAL slice READY and continue with the highest current evidence-backed Storage/Recovery/Provider/Packaging gap after re-tracing stale queue entries. If red, fix the exact primary failure before unrelated work.
