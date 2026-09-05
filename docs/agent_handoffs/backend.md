# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@cf33955bcaa91649f2b5ac1142940e5e72ffa43a`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0`.
- History-preserving NON-FORCE synchronization: `ff7702e620b6cdb40075ae9cd6038578c4743eaa`, with parents prior Backend head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0` and exact Develop `cf33955bcaa91649f2b5ac1142940e5e72ffa43a`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP alternative read API bypass — VERIFIED

Product `91bf40b1a8cfd72403e4b81061980079460b7c16` rejects alternative data-consuming response APIs `peek`, `read1`, `readinto`, and `readinto1` before underlying I/O. Focused tests `23e914033a1012d7f6901ae86299e49d435a90ed` plus monotonic fixture correction `e62fcc2db49815e7d32579d0dc68a143f8af07b0` passed exact descendant Backend head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0` in ATHENA Quality `33936396203 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP raw body-handle escape — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

Product commit `05730b74a2bb64aa240b6199a0476bd3e0c83998` closes a distinct response-wrapper escape: delegated `fp`, `file`, or `raw` attributes could expose the underlying body object and therefore allow callers to bypass the established cumulative byte cap and monotonic total deadline even after alternative read methods were blocked. `_BoundedLocalResponse.__getattr__` now rejects these raw body-handle attributes fail-closed while retaining ordinary response metadata delegation.

Focused test commit `202d2f6ac5d3c0e7da4dede2e381d838f25abf8f` proves `fp`, `file`, and `raw` are rejected without consuming underlying bytes and that ordinary bounded response state remains intact.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- local model transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation unchanged;
- response-size enforcement remains cumulative and terminal after overflow;
- total response deadline remains fail-closed on successful and HTTP-error paths;
- alternative raw response read APIs and raw body-handle escape attributes cannot bypass bounded `read()`/`readline()` paths;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: alternate-read bypass product `91bf40b1a8cfd72403e4b81061980079460b7c16` + focused tests `23e914033a1012d7f6901ae86299e49d435a90ed` + fixture correction `e62fcc2db49815e7d32579d0dc68a143f8af07b0` through exact green Backend head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0`, Quality `33936396203 = success`.
- NOT READY: raw body-handle escape product `05730b74a2bb64aa240b6199a0476bd3e0c83998` + tests `202d2f6ac5d3c0e7da4dede2e381d838f25abf8f` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `202d2f6ac5d3c0e7da4dede2e381d838f25abf8f`. If green, mark raw body-handle escape hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
