# Backup scheduler negative durable slot — 2026-10-02

## Ausgangslage

Base: `develop/pathena-next` at `467ef434236c320e4afe9d21a39c20a4a2b75728`.

The daily Backup worker validates public scheduler timestamps through `_nonnegative_timestamp()`, but durable job scope parsing in `DurableBackupWorker._job_scope()` only rejected booleans and non-integers.

A persisted scope such as:

```json
{"schedule_slot_us": -1, "target_id": "<uuid>"}
```

was therefore accepted as a valid Backup occurrence.

## Root Cause

The durable serialization boundary was weaker than the public scheduling boundary.

`schedule_slot_us` is an absolute microsecond timestamp and must be non-negative. The parser validated type but omitted the lower-bound invariant.

Because `process_leased()` consumes `_job_scope()` before deciding whether a slot is already satisfied, a corrupted negative value could proceed into real target/Backup work instead of failing closed.

## Änderungen

- `DurableBackupWorker._job_scope()` now rejects `slot_raw < 0` using the existing “no valid schedule slot” error contract.
- Added a regression that creates a real durable `backup.create` job with `schedule_slot_us=-1`, leases it, executes the Backup worker, and asserts:
  - `BackupJobError` is raised;
  - no completed Backup snapshot is created.

## Dateien

- `src/athena/jobs/backup.py`
- `tests/unit/test_backup_scheduler.py`
- `docs/agent_handoffs/backup-scheduler-negative-slot-20261002.md`

## Verhalten danach

Malformed durable Backup jobs with a negative scheduled occurrence cannot silently be interpreted as ancient valid occurrences and cannot start Backup filesystem work.

Normal daily scheduling, missed-run catch-up, manual-backup idempotence, retry behavior and quiet-hour calculation are unchanged.

## Parallelität / Konfliktrisiko

Before editing, all open Backup-related PRs were checked for these paths. No open PR changed:

- `src/athena/jobs/backup.py`
- `tests/unit/test_backup_scheduler.py`
- `tests/unit/test_job_backup_scheduler_scalar_validation.py`

Existing Deep-Verify PRs operate in separate Backup verify/job files.

This slice is independent of Backup filesystem redirect candidate #375.

## Branch / Commits

Branch: `fix/backup-scheduler-negative-slot-20261002-sol`

- `8ba25c3b45be9bcfa0885749abb1ec7a1d4642c5` — reject negative durable Backup schedule slots
- `77cf506cd6b3ee113ce60dc4a41c1209600dd96a` — regression: corrupt negative slot cannot create a snapshot

## Validierung

No local test result is claimed: the current ChatGPT container cannot clone GitHub because outbound DNS to `github.com` fails.

No PR was opened intentionally during this run because the repository's GitHub Actions runners already had the consolidated Backup candidate #375 fully queued. This branch therefore has no CI evidence yet.

## Nächste sinnvolle Schritte

1. After #375's runner pressure clears, open one small PR from this branch to the then-current `develop/pathena-next`.
2. Recheck whether newer Jobs work touched `jobs/backup.py` before opening that PR.
3. Run focused `tests/unit/test_backup_scheduler.py` plus canonical Quality.
4. If current Develop has advanced without touching these files, rebuild a fresh candidate on the new head rather than rebasing/force-pushing.
