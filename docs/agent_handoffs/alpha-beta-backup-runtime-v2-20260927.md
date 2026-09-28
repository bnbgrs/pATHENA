# Alpha/Beta Backup runtime v2 — Deep verify composition

Date: 2026-09-27
Base Develop: `ddedfa8d19c661f4fe27c2901c618f2aef6a96b9`
Branch: `fix/alpha-beta-backup-runtime-v2`

## This slice
- switches the application job service to the already-qualified `BackupDeepVerifyDurableJobService`;
- instantiates `DurableBackupDeepVerifyWorker` against the canonical BackupService;
- exposes `backup.verify_deep` as a real scheduler-supported CONTROL-lane job;
- schedules due Deep verification only from the control/all housekeeping lane;
- dispatches leased Deep-verify jobs through the scheduler;
- includes Deep-verify errors in the scheduler's bounded durable failure path;
- extends provider-lane housekeeping regression so provider workers cannot schedule Deep verification.

## Tests added
- application composition and lane ownership;
- due Deep-verify materialization + scheduler dispatch to completion.

## Next
After exact-head Quality is green, continue Alpha 15/Beta 21 and lifecycle gaps. Do not rework #191/#195; those are already integrated on Develop.
