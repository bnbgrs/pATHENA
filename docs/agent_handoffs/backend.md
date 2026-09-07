# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@7b9cc9ea78733e6df7f3cb0aa542064bbc8c934a`.
- Worker before synchronization: `postmerge/backend@a664ba7aba35c1865046b2db286a4ca883017d9c`.
- Current worker heads reviewed: Error `22bc248f35f3d9d11aa4717356e3b3edd7a3d6de`; Spec/Core `8bb8822a3423ac4fa1ab2873ecf052d16c390199`; UI `4e20612024bc5ffe0289b5c8ecd541ea25b8b10b`; Integrator/Develop `7b9cc9ea78733e6df7f3cb0aa542064bbc8c934a`.
- `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, Alpha/Beta progress and Beta Storage WAL §§39/41 were reviewed before mutation.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Canonical evidence consumed

- Previous Backend exact head `a664ba7aba35c1865046b2db286a4ca883017d9c` passed ATHENA Quality Gate `34086812930 = success`.
- Integrator had already consumed the verified `WalMaintenanceService._checkpoint()` fail-before-side-effect mode boundary into Develop; current Develop records that integration.
- ExternalAccessGateway runtime boundaries remain exact-green at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, canonical Quality `33884210684 = success`; no rework was required.
- Error handoff reports no OPEN/BLOCKED defect and no exact-current recurrence of retained Windows runtime crash signatures.

## History-preserving synchronization

Backend synchronized to exact current Develop via two-parent commit `b412bd5921cfc5157e3c4dd6e1573f098e710b3e`, using exact Develop tree `8bb3959c72cb53928b0e3db53b15ff7d3cf4b60f` with parents previous Backend `a664ba7aba35c1865046b2db286a4ca883017d9c` and Develop `7b9cc9ea78733e6df7f3cb0aa542064bbc8c934a`. `postmerge/backend` advanced NON-FORCE. No foreign product file was overwritten and no history rewrite occurred.

## Product slice — scheduler-facing PASSIVE WAL maintenance interval gate

Beta Storage §39 requires real WAL-size observation in addition to SQLite `wal_autocheckpoint`; §41 requires normal-operation PASSIVE checkpoints in background intervals, with TRUNCATE only at an explicit idle boundary.

Product commit `73adb94fe84dc09b36d8ac40718dd9c7610f8649` adds `src/athena/storage/wal_schedule.py` with `WalMaintenanceIntervalRunner`:

- requires an actual `WalMaintenanceOrchestrator`;
- validates `interval_seconds` as finite, positive, numeric and non-bool before any maintenance side effect;
- validates scheduler-supplied monotonic time as finite, non-negative, numeric and non-bool;
- rejects monotonic time regression before invoking the orchestrator;
- runs the first scheduler tick immediately and subsequent cycles only when the configured interval is due;
- advances the due time only after a valid `WalMaintenanceDiagnosis` returns;
- owns no thread, timer, retry loop, database path or TRUNCATE path;
- therefore preserves PASSIVE-only automatic maintenance and leaves explicit-idle TRUNCATE ownership unchanged.

Focused regression commit `a8d9a487d414ad739d18d78bb7c5b192e3a00baa` adds `tests/unit/test_wal_maintenance_interval_runner.py` covering invalid bool/zero/negative/NaN/Inf interval values, immediate/interval-gated execution, invalid scheduler timestamps before side effects, monotonic regression, invalid diagnosis result and no reschedule after invalid diagnosis.

## Call chain

Core scheduler tick -> `WalMaintenanceIntervalRunner.run_due(now_monotonic=...)` -> finite/non-bool monotonic validation -> interval due gate -> `WalMaintenanceOrchestrator.run_cycle()` -> `WalMaintenanceService.maintain_once()` -> WAL status/live `wal_autocheckpoint` threshold -> optional PASSIVE checkpoint only -> long-reader/growth diagnosis. No automatic TRUNCATE path is introduced.

## Retained invariants

- no silent Tor -> Direct fallback; Direct fallback remains explicit-only;
- no loopback/private proxy leak; redirects require reauthorization; HTTPS/default-port and compressed/oversize response handling remain fail-closed;
- ExternalAccessGateway TTL/max-bytes remain genuine non-bool ints; timeout remains numeric, non-bool and finite;
- audit/provenance/fsync/transactional Source finalization unchanged;
- PASSIVE remains the only automatic WAL checkpoint mode;
- TRUNCATE still requires explicit idle confirmation;
- active ATHENA transactions still refuse checkpointing;
- no manual WAL deletion; no-follow regular-file handle/path identity WAL observation preserved;
- no new retries, background threads, crypto, schema, migration, transaction or Provider/Security semantics;
- retained Windows pypdf/frozen argv/two-EXE/bounded-worker/DirectChat/lane-lock/storage-bootstrap crash classes remain Beta/release regression acceptance knowledge only absent exact-current reproduction;
- no Skip/XFail/assertion or guard weakening.

## Verification state

- Exact predecessor Backend: Quality `34086812930 = success`.
- Product-only Quality for `73adb94fe84dc09b36d8ac40718dd9c7610f8649` was superseded by the focused-test successor.
- Product+test exact Quality `34091462602@a8d9a487d414ad739d18d78bb7c5b192e3a00baa` was queued when this handoff was written; do not claim PASS until an exact run completes successfully.
- A final documentation descendant canonical run may supersede/cancel the queued product+test run; only an exact completed success on a descendant carrying unchanged product/test blobs is sufficient for Integrator-ready status.

## Integrator handoff

READY_SOURCE: ExternalAccessGateway runtime boundary `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`; previous checkpoint-service boundary `a664ba7aba35c1865046b2db286a4ca883017d9c`, Quality `34086812930 = success`, already integrated.

PENDING: scheduler-facing PASSIVE WAL interval gate product `73adb94fe84dc09b36d8ac40718dd9c7610f8649` + regression `a8d9a487d414ad739d18d78bb7c5b192e3a00baa` until exact canonical Quality succeeds.

## Next backend slice

Consume exact canonical Quality on the final descendant carrying the interval gate and regression. If green, mark only this scheduler-facing interval gate Integrator-ready and trace the concrete Core scheduler composition point needed to invoke it without creating a second scheduler/thread or automatic TRUNCATE path. If red, repair only the exact Backend-owned primary failure. If scheduler composition proves owned elsewhere or collision-prone, take the next disjoint provider/recovery/platform P1/P2 gap rather than extending DTO-only hardening.
