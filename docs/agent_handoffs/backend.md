# pATHENA Backend & Systems Handoff

## Baseline

- Exact shared baseline reviewed and synchronized: `develop/pathena-next@cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Pre-run Backend worker: `postmerge/backend@0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d`.
- History-preserving NON-FORCE sync: `9301961ec33231989bf7b00760da4895e6642143`, parents `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` and exact Develop `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`. Develop-owned Integrator/startup-experience blobs were imported byte-identically; Backend v41/WAL lineage was preserved.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Handoffs and exact evidence consumed

- Error, Spec/Core, UI and Integrator handoffs were reviewed before mutation.
- Exact predecessor Quality `34269071606` on `0d579f718f97f7d0ba6d39d4cd8bcc6741beb72d` completed FAILURE: mypy, Linux-storage-regressions, Windows-path-safety, Local-install-smoke and specification-validator passed; Ruff and canonical pytest failed.
- Diagnostics artifact `10073791560` was downloaded and consumed. Ruff supplies exact I001 formatter evidence for `src/athena/storage/schema.py`: `DatabaseCompatibilityError` must sort after the lowercase `_user_tables` / `assert_writable_schema` names in the relevant `schema_contract` import block. No further guessed import move is permitted.
- Canonical pytest diagnostics separate current-v41/legacy-fixture drift from WAL test-collaborator drift. The latter includes `tests/unit/test_wal_scheduler_dependency_boundary.py` failing before its intended hook assertion because the scheduler fake is no longer canonical under the hardened exact-type guard.

## ExternalAccessGateway priority

Exact Develop still contains the requested fail-before-side-effect runtime boundaries and regressions: `ttl_seconds` and `max_bytes` require genuine non-bool ints; `timeout_seconds` is numeric, non-bool and finite, rejecting bool/NaN/Inf while preserving valid ranges. The prepared patch is therefore already executed in the shared lineage and was not duplicated.

## Progress this run — synchronization and WAL dependency-boundary test recovery

The worker was genuinely synchronized to current Develop via two-parent commit `9301961ec33231989bf7b00760da4895e6642143` with force=false.

Commit `c8b12bb2bd0362540c8a9474aecb27a6e168c6d1` repairs one exact `ERR-0029` cluster without touching production guards. `tests/unit/test_wal_scheduler_dependency_boundary.py` now:

- expects the current canonical `DurableJobScheduler` error for a noncanonical scheduler;
- constructs a real canonical `DurableJobScheduler` with inert typed dependencies before testing an invalid WAL hook, so validation reaches the intended exact-type hook boundary;
- keeps the production `type(...) is ...` guards unchanged and adds no Skip/XFail/guard weakening.

Quality `34275996841` on `c8b12bb2bd0362540c8a9474aecb27a6e168c6d1` was queued at handoff time. No focused PASS, Ruff PASS, pytest PASS, global-green or promotion-ready claim is made before exact completion.

## Remaining exact recovery

- `ERR-0026`: apply the formatter-proven `DatabaseCompatibilityError` import ordering only; then require real Ruff PASS.
- `ERR-0028`: update truthful current-schema expectations to v41/`0041_research_delta_boundary` and strip v41-only `research_delta_boundaries` state from legacy v30-v40-shaped fixtures before unchanged production migration. Do not make production migration permissive.
- `ERR-0029`: remaining WAL tests must use canonical concrete `DurableJobScheduler` / `WalMaintenanceOrchestrator` collaborators or assert the new fail-before-side-effect type boundary where invalid dependency behavior is itself the subject.

## Invariants retained

- v40→v41 remains additive, verified and transactional; Delta lower-bound provenance remains explicit and restart-durable.
- production migration does not silently tolerate malformed legacy fixtures.
- production WAL exact-type fail-closed guards remain unchanged.
- no silent Tor→Direct fallback; Direct fallback explicit only; no loopback/private proxy leak; redirect re-authorization preserved; HTTPS/default-port/compression/response-size boundaries fail closed.
- Audit/Provenance/fsync/transactional Source finalization unchanged.
- PASSIVE-only automatic WAL maintenance; explicit-idle TRUNCATE only; no manual WAL deletion.
- no new scheduler process/loop/thread/timer/retry, cryptography, lane-lock, process-tree, packaging or DirectChat changes.
- release crash-signature matrix retained without reopening absent exact-current reproduction.
- no force push, rebase, history rewrite or main mutation.

## Next Backend action

Consume exact Quality `34275996841`. Apply the exact Ruff formatter diff for `schema.py` with no semantic change; then continue `ERR-0028` legacy-fixture cleanup and the remaining `ERR-0029` canonical-collaborator conversions. Run focused v40→v41/restart/Research/WAL plus `tests/unit/test_external_access_gateway.py`, the smallest Network/Security regressions and canonical Quality. Do not hand §75 to Core/Integrator until Backend-owned exact failures are green.
