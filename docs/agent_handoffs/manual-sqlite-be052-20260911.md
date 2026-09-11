# Manual BE-052 / ERR-0035 SQLite continuity handoff — 2026-09-11

## Lineage

Base: `develop/pathena-next@0298f0c4f2d28e516a458390f8b462131ebaf17e`
Branch: `manual/sqlite-be052-20260911`

This is an isolated repair candidate. It does not mutate `postmerge/backend` or any other worker branch.

## Root cause

The read-only startup preflight previously returned application/schema/integrity facts, then `SQLiteDatabase.start()` later opened a writable connection by pathname. No identity token bound the attested primary database plus WAL/SHM sidecars across that boundary. A sidecar or primary file could therefore change after preflight and before writer establishment.

## Candidate behavior

`DatabasePreflightReport` now carries a `DatabaseFileSetIdentity` for the primary database, WAL and SHM. Each present member records filesystem device/inode identity plus size, mtime and ctime mutation markers.

Writer startup now:

1. performs the existing read-only preflight;
2. exactly re-captures DB/WAL/SHM before opening the writer and fails closed on any change;
3. opens the writer through one explicit connection boundary;
4. immediately rebinds every file object that existed during preflight by device/inode identity before schema initialization or connection-policy mutation;
5. closes the new writer and raises recovery-required if the binding fails.

The read-only preflight also checks that the primary and any already-present sidecar objects did not get replaced while the inspection itself was active.

Previously absent files may legitimately appear as SQLite establishes a new database or sidecar; the exact pre-connect revalidation is the fail-closed fence for the post-inspection/pre-writer mutation window, while post-connect identity binding protects every object that already existed at that fence.

## Adversarial coverage

`tests/unit/test_database_preflight_continuity.py` adds:

- a file-set snapshot/currentness contract;
- deterministic WAL injection after preflight returns but before writer open, which must fail before writer startup;
- deterministic primary-file replacement at the writer-open boundary, which must be detected after connect and leave the service unstarted.

## Bot rules

1. Do not independently implement BE-052 on `postmerge/backend` while evaluating this candidate; compare first and reuse only if stronger/equivalent.
2. Do not weaken read-only preflight, quick-check, application-id/schema checks, locality or symlink/reparse rejection.
3. Do not reduce the file set to the primary DB only; WAL and SHM are part of the continuity contract.
4. Do not treat pathname equality as identity continuity.
5. Exact canonical Quality and Linux/Windows storage regressions are required before `ERR-0035` can move to FIXED.
6. If CI exposes legitimate SQLite sidecar metadata churn, preserve the pre-connect exact fence and adjust only the post-connect object-binding rule with evidence; do not remove the continuity fence.
7. Keep `ERR-0033 / BE-046` separate; this candidate does not claim EmergencyReserve closure.
