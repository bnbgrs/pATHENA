# Alpha/Beta Backup seed — 2026-09-27

Base Develop: `0c68facde0f7bf9e5d0210925674eb24ddf969bf`
Worker: `fix/alpha-beta-backup-lifecycle`

## #191 atomic occurrence reservation
`DurableBackupDeepVerifyWorker.schedule_due()` now:
- selects only to identify the target;
- acquires the existing cross-process `backup_target_lock`;
- re-selects authoritative due state under the lock;
- re-reads target identity/status;
- checks active-target and duplicate occurrence state under the same lock;
- persists the durable job before releasing that lock;
- creates no work when the target lock is busy or due state changed.

## #195 progress-driven lease liveness
`BackupService.verify_deep()` now accepts an optional progress callback.
Real byte progress is reported from:
- full database/object hashing;
- restore-smoke SQLite copy;
- restore object copy and copy verification.

The worker renews its fenced durable lease only when those progress callbacks advance and uses a throttled cadence based on one third of the lease extension. Initial heartbeat remains immediate. If heartbeat reports cancellation, verification unwinds at the next safe progress boundary and cancellation is acknowledged. Lease/fencing exceptions are not swallowed.

## Durable admission
The canonical-green `BackupDeepVerifyDurableJobService` from PR #239 is included, and `backup.verify_deep` is explicitly CONTROL-lane safe.

## Next bot action
Run focused backup tests, Ruff and mypy first. Do not re-diagnose #191/#195 unless exact-head evidence fails. Runtime scheduler/application composition is intentionally still a separate next slice after these invariants qualify.
