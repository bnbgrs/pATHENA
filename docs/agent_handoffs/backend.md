# pATHENA Backend & Systems Handoff

## Baseline

- Exact shared baseline reviewed: `develop/pathena-next@270f97c36bd114036658e322f68d8011983ff150`.
- Pre-run Backend worker: `postmerge/backend@ac9bf5c289b2979548cfabb9e45a0a9dce51be71`.
- History-preserving NON-FORCE sync: `b08097fd1df71f9a4be1ca0182b5338ad8fa90c1`, parents `ac9bf5c289b2979548cfabb9e45a0a9dce51be71` and exact Develop `270f97c36bd114036658e322f68d8011983ff150`. Develop-owned Jobs UI/test and Integrator blobs were imported byte-identically; Backend v41/WAL work was preserved.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Handoffs consumed

- Error handoff: exact Quality `34245022980` on synchronized predecessor `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` completed FAILURE with specification-validator/mypy/Linux-storage/Windows-path-safety/Local-install PASS, Ruff FAIL and canonical pytest FAIL. Error split is now exact: `ERR-0026` schema import order, `ERR-0027` missing v41 schema facade re-export, `ERR-0028` stale v40-shaped schema fixtures/expectations, `ERR-0029` WAL test-collaborator drift.
- Spec/Core handoff: §75 remains blocked on an exact-green durable Backend v41 prerequisite; no Core schema/storage work was consumed or overwritten.
- UI handoff: UI-GAP-0004 is exact-green/integrator-ready and is now present on Develop; Backend imported only the exact Develop blobs during synchronization.
- Integrator handoff: current Develop carries the verified Jobs copy integration and still holds Backend §75 until exact-green Backend evidence.

## ExternalAccessGateway priority

Exact Develop still contains the requested fail-before-side-effect runtime boundaries and regressions: `ttl_seconds` and `max_bytes` require genuine non-bool ints; `timeout_seconds` is numeric, non-bool and finite, rejecting NaN/Inf while preserving valid ranges. The prepared patch was not duplicated.

## Progress this run — ERR-0026 + ERR-0027 product repair

Product commit `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` repairs the two bounded schema facade defects without migration/runtime weakening:

- schema imports are mechanically consolidated/canonically ordered rather than suppressed, removing the known Ruff `I001` source;
- `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION` are re-exported from the real `schema_contract`, preserving the established schema facade identity pattern required by `test_schema_contract_boundary.py`;
- v40→v41 migration call chain, supported-version set, fail-closed verification, SQLite pragmas and physical-cleanup behavior are unchanged.

Canonical Quality `34251782009` is pending on exact product SHA `69e2a4707bba544af5d2d2ae53daffc1dbf786a3`. No Ruff PASS, pytest PASS, global-green or promotion-ready claim is made before that exact run completes.

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

Consume exact Quality `34251782009`. If Ruff and `test_schema_contract_boundary.py` clear, mark only ERR-0026/ERR-0027 fixed-pending-integrator verification and immediately repair exact `ERR-0028` harness drift: update truthful current v41 schema/migration expectations and remove v41-only `research_delta_boundaries` objects from legacy v30-v40 fixtures before exercising v40→v41. Then repair `ERR-0029` only by recomposing tests with canonical concrete `DurableJobScheduler`/`WalMaintenanceOrchestrator` collaborators and current dependency-error wording; do not relax production exact-type guards. Run focused v40→v41/restart/Research/WAL plus ExternalAccessGateway/network-security regressions and canonical Quality. Do not hand §75 to Core/Integrator until Backend-owned exact failures are green.
