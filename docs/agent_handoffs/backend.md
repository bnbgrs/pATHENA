# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@4e18f75beeaa1c5b57bca28dcad5a062ac498051`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `9976f6bdbdf9478db7a31c33aa0ae3dcf660f1be`, using the exact Develop tree as the content base and preserving the Backend-owned WAL scheduler files.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Exact prior verification

Canonical Quality run `34163784073` on Backend head `fa676f0d677bec1d69b2339bf030d57d12431d44` completed FAILURE with `1 failed, 4819 passed, 3 skipped, 2 warnings`.

The only failure is UI-owned: `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]`, where completed-state copy contains the forbidden implementation phrase `lifecycle action`.

Backend evidence inside that exact run remains green: `tests/unit/test_wal_job_hook.py` is 16/16 PASS, the requested ExternalAccessGateway runtime-boundary tests pass, and no Backend-owned primary failure is present. Backend must not patch the UI copy failure.

## Current Backend slice

Area: bounded WAL maintenance interval scheduling.

Product commit `380149a7963109f05ec531a09b86733d8ad84694` makes deadline arithmetic fail closed: before any WAL cycle, `run_due()` computes `now_monotonic + interval_seconds` and rejects a non-finite result. This prevents a finite-but-extreme monotonic timestamp/interval pair from silently storing `inf` as the next deadline and permanently suppressing future maintenance.

Regression commit `32bd20e56721e3d2c1fe585f37a6128c30e8dd42` adds `tests/unit/test_wal_schedule_overflow.py`, proving overflow rejection occurs before `orchestrator.run_cycle()` and leaves `next_due_monotonic` unset.

Canonical Quality run `34167424033` is pending for exact product/test head `32bd20e56721e3d2c1fe585f37a6128c30e8dd42`. No PASS is claimed until that exact run completes.

## Invariants

- PASSIVE-only automatic WAL maintenance remains unchanged.
- Automatic TRUNCATE remains forbidden; TRUNCATE still requires explicit idle confirmation.
- No second scheduler loop, process, thread, timer, retry or new database side effect is introduced.
- Overflow validation is fail-before-WAL-side-effect.
- Existing PROVIDER-lane zero-WAL behavior and ALL/CONTROL ownership remain unchanged.
- ExternalAccessGateway runtime boundaries already present on Develop remain untouched: genuine non-bool ints for TTL/max-bytes; finite numeric non-bool timeout; no silent Tor-to-Direct fallback; redirect reauthorization and response hardening preserved.
- Persistence, recovery, provenance, fsync, schema, migration, packaging, process-tree and cryptographic semantics are unchanged.
- Known Windows lane-lock/packaged-worker, pypdf/frozen argv, two-EXE topology and Direct-Chat context signatures remain release-regression knowledge only absent exact-current reproduction.

## Deferred shared composition

`src/athena/core/application.py` still constructs canonical `DurableJobScheduler`. The verified `WalAwareDurableJobScheduler` integration point is identifiable, but direct replacement of the 32KB shared Core composition file was not performed in this run because connector mutation requires full-file replacement and current Core/UI work makes that unnecessarily collision-prone. The run therefore advanced a disjoint real Backend-owned fail-closed slice instead of repeating analysis.

## Next Backend slice

First consume exact Quality `34167424033`. If green, mark only the WAL deadline-overflow boundary verified/integrator-ready. Then either perform the application scheduler substitution through a collision-safe exact-file mutation if the shared file is stable, or immediately select another disjoint evidence-backed Recovery/Provider/Platform Backend P1/P2 slice. Do not modify the UI-owned lifecycle-copy failure.
