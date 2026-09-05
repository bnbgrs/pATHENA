# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@b9ab5ecb7fc49a5d3bd5c25f0254f118e21fc7ee`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `8be678b5fa3e19aa442e788d935436914a53452b`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff; current worker branches were checked before mutation.
- History-preserving NON-FORCE synchronization: `0d01f71e540f4a8f346f1267a6f1be9b6a6e8f23`, with parents prior Backend head `8be678b5fa3e19aa442e788d935436914a53452b` and exact Develop `b9ab5ecb7fc49a5d3bd5c25f0254f118e21fc7ee`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` reject bool/non-int values; `timeout_seconds` rejects bool and non-finite values while preserving valid numeric ranges. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve-release state invariant — VERIFIED

Product `79d6382f728fac2ca7bdae2306881327c82042ed` requires positive `released_reserve_bytes` to originate from an EMERGENCY before-state. Focused tests `02e9d210a946e9d782797cc5950902afd38a0781` cover rejection from NORMAL and acceptance of EMERGENCY -> CRITICAL reassessment.

Exact Backend head `8be678b5fa3e19aa442e788d935436914a53452b` passed canonical ATHENA Quality `33972009715 = success`. The prior foreign UI/PALLAS failure has therefore cleared on the current Backend lineage.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure released-volume bound — APPLIED / PENDING CANONICAL

`DiskPressureCheckResult` previously accepted `released_reserve_bytes` larger than the entire assessed volume. That telemetry is physically impossible for a reserve stored on the same volume and can corrupt recovery/audit interpretation even when the before-state is EMERGENCY.

Product/test commit `a6968852a8db404fdb52e5a157c8e6eb6d82a485` now fails closed when reported released reserve bytes exceed `before_release.total_bytes`. Existing EMERGENCY-only release and zero-release identity rules remain unchanged. Focused coverage adds rejection of a 101 GiB release against a 100 GiB volume while preserving the valid 1 GiB EMERGENCY release case.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- read-only safe-mode latching and noncritical-write gating remain unchanged;
- storage telemetry does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source-finalization semantics changed;
- valid Windows/Linux storage behavior remains unchanged;
- local model transport remains loopback-only, proxy-free and redirect-rejecting;
- response-size and total-deadline enforcement remain fail-closed;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy and compressed-response rejection unchanged;
- audit and provenance semantics unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Error / collision handoff

- Current Error handoff reports `ERR-0001` through `ERR-0013` fixed and no OPEN/BLOCKED signature.
- Current UI exact head is canonically green per Error handoff.
- No UI/Core-owned files were mutated in this Backend run.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state product `79d6382f728fac2ca7bdae2306881327c82042ed` + tests `02e9d210a946e9d782797cc5950902afd38a0781`, exact Backend head `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- NOT READY: released-volume-bound commit `a6968852a8db404fdb52e5a157c8e6eb6d82a485` until exact canonical evidence is green.

## Next backend slice

Consume the first exact canonical Quality run containing `a6968852a8db404fdb52e5a157c8e6eb6d82a485` or this documentation-only descendant. If green, promote the released-volume bound to VERIFIED/READY and immediately take the highest unclaimed disjoint Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact diagnostics and repair only a Backend-owned failure; do not weaken tests or cross owner scope.