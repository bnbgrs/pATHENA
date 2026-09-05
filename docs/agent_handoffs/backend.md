# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@52e702912b3b2c0f4cfc7c93baf4c656a02231ad`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `6cdb9095b265230b5484a7ce203c09c798b9a0a6`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- History-preserving NON-FORCE synchronization: `330d47573daa0ccbcf124b15c3c2cb8c6642b4fc`, with parents prior Backend head `6cdb9095b265230b5484a7ce203c09c798b9a0a6` and exact Develop `52e702912b3b2c0f4cfc7c93baf4c656a02231ad`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health whitespace-detail invariant — VERIFIED

Product `73ed1c6fa99078f2559dcc2e7236dcffae10553f` rejects non-None `detail` values containing only whitespace. Focused tests `3e29d5e012a82795c064ea2e574e49e6546d464e` cover space, tab and CRLF-only details. Exact Backend descendant `6cdb9095b265230b5484a7ce203c09c798b9a0a6` passed canonical ATHENA Quality `33952543793 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health unavailable-path invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

`StorageHealthService.snapshot()` always knows and emits the configured SQLite path even before database start, but the runtime `StorageHealthSnapshot` contract still accepted `status="unavailable"` with `database_path=None`. That allowed contradictory telemetry to pass validation.

Product commit `3421ea19c33b16a7694d7cb96951787225cb0d4c` now requires a concrete database path for the unavailable state. Existing available/error path requirements and valid unavailable service snapshots are unchanged.

Focused test commit `fbc3e214b822e8f25477ece0248d21f5fbe5d4fe` verifies fail-closed rejection of an unavailable snapshot without a path.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- storage telemetry remains read-only and does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source finalization semantics changed;
- local model transport remains loopback-only, proxy-free and redirect-rejecting;
- response-size and total-deadline enforcement remain fail-closed;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy and compressed-response rejection unchanged;
- audit and provenance semantics unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth whitespace-detail product `73ed1c6fa99078f2559dcc2e7236dcffae10553f` + tests `3e29d5e012a82795c064ea2e574e49e6546d464e` through exact green Backend head `6cdb9095b265230b5484a7ce203c09c798b9a0a6`, Quality `33952543793 = success`.
- NOT READY: StorageHealth unavailable-path product `3421ea19c33b16a7694d7cb96951787225cb0d4c` + tests `fbc3e214b822e8f25477ece0248d21f5fbe5d4fe` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `fbc3e214b822e8f25477ece0248d21f5fbe5d4fe` or a documentation-only descendant. If green, mark StorageHealth unavailable-path hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
