# pATHENA Backend & Systems Handoff

## Baseline
- Shared baseline: `develop/pathena-next@4e18f75beeaa1c5b57bca28dcad5a062ac498051`.
- Worker: `postmerge/backend`.
- NON-FORCE history sync: `9976f6bdbdf9478db7a31c33aa0ae3dcf660f1be`, exact Develop tree plus Backend-owned WAL files only.
- `main` and `bnbgrs/ATHENA` untouched/read-only.

## Prior canonical evidence
`Quality_34163784073@fa676f0d677bec1d69b2339bf030d57d12431d44` completed FAILURE: `1 failed, 4819 passed, 3 skipped, 2 warnings`. Sole failure is UI-owned completed-job copy containing `lifecycle action`. Backend-owned `test_wal_job_hook.py` is 16/16 PASS and requested ExternalAccessGateway boundary tests are green. Do not patch the UI failure from Backend.

## Current real Backend slice
Area: bounded WAL maintenance interval deadline arithmetic.

- `380149a7963109f05ec531a09b86733d8ad84694`: add finite next-deadline validation before `orchestrator.run_cycle()`.
- `32bd20e56721e3d2c1fe585f37a6128c30e8dd42`: add fail-before-WAL overflow regression.
- `77a9ca573fa46bbdd13580c14d3441892a80eb49`: preserve pre-existing `_last_observed_monotonic` update semantics; only overflow behavior remains new.
- `911fec154be2a895aa7021b27156a69feabc8c7f`: make the side-effect sentinel test fully typed without guard/assertion weakening.

The defect: individually finite `now_monotonic` and `interval_seconds` can sum to `inf`; storing that as `_next_due_monotonic` would silently suppress all future automatic WAL maintenance. The new check rejects non-finite deadline arithmetic before any WAL cycle and leaves `_next_due_monotonic` unset.

## Invariants
PASSIVE-only automatic maintenance; explicit-idle-only TRUNCATE; no second scheduler/process/thread/timer/retry; PROVIDER zero-WAL behavior unchanged; existing monotonic-state semantics unchanged except fail-closed deadline overflow; no schema/migration/recovery/provenance/fsync/packaging/process-tree/lane-lock/DirectChat/security/crypto change. ExternalAccessGateway true-int TTL/max-bytes, finite non-bool timeout, no Tor-to-Direct fallback, redirect reauthorization, HTTPS/default-port, compressed-response and response-size hardening remain unchanged.

Known Windows pypdf/frozen-argv, two-EXE bounded-worker, Direct-Chat small-context and lane-lock→scheduler-owner→packaged-worker crash signatures remain Beta/release regression knowledge only absent exact-current reproduction.

## Deferred shared composition
`src/athena/core/application.py` still constructs `DurableJobScheduler`. The `WalAwareDurableJobScheduler` substitution point is known, but replacing the current 32KB shared Core composition file through a whole-file connector write was judged collision-prone. This run therefore executed the disjoint Backend-owned overflow hardening instead of repeating composition analysis.

## Verification
Canonical Quality for the current exact lineage is not yet claimed green. Consume the newest exact workflow on the final handoff head before promotion/integration.

## Next
First consume exact canonical Quality on this final head. If green, mark only WAL deadline-overflow hardening VERIFIED/INTEGRATOR_READY. Then perform the shared application scheduler substitution only through a collision-safe exact mutation; otherwise immediately select a different disjoint evidence-backed Recovery/Provider/Platform Backend P1/P2 slice. Do not touch the UI-owned lifecycle-copy failure.
