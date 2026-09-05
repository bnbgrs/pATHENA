# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@de2f5a64e7a0fbc282df81db6beee3431297f2de`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `235a13086985341edc02ee61e742e63a863974ab`.
- History-preserving NON-FORCE synchronization: `358c81718b7ad51689307c2613ebdf4010b0ea24`, with parents prior Backend head `235a13086985341edc02ee61e742e63a863974ab` and exact Develop `de2f5a64e7a0fbc282df81db6beee3431297f2de`.
- Worker heads reviewed before mutation: errors `2d5bca8124d9e9cd013ea9885469d295194b6ac8`; spec-core `8fab2f3080adc50c4093124c8e0bc1906176da40`; ui `37a097b9e97314184c36780b38b39b217418be12`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP direct and error-body total deadlines — VERIFIED

Direct-read deadline lineage through `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` passed Quality `33921338439 = success`. HTTP-error deadline product `4f94d07f87849aec832437c2ac0dde66bd7433b2` + tests `08973df26572e66a3ecb26ace403362701e7376e` passed exact descendant Quality `33925587762 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP terminal size-overflow state — VERIFIED

Product `f1fba82ed81bb1fe744fa698bdacc8d25c1a1f8e` accounts bytes consumed by the underlying response before evaluating the cumulative cap and leaves the wrapper in a terminal fail-closed overflow state. Test commit `31fa8d4cd25cd9a67a1e43bce22a600a98b98128` covers direct-read and readline overflow poisoning and verifies subsequent access performs no new underlying read.

Exact descendant Backend head `235a13086985341edc02ee61e742e63a863974ab` passed canonical ATHENA Quality `33929643363 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP alternative read API bypass — FIXED_PENDING_VERIFY

`_BoundedLocalResponse.__getattr__` previously delegated alternative data-consuming response APIs such as `readinto()`, `read1()`, `readinto1()` and `peek()` directly to the underlying HTTP response. Those calls bypassed the wrapper's cumulative response-size accounting and monotonic total-deadline checks.

Product `91bf40b1a8cfd72403e4b81061980079460b7c16` now rejects those alternative read APIs fail-closed while continuing to delegate non-data metadata/accessor attributes. Test commit `23e914033a1012d7f6901ae86299e49d435a90ed` proves all four bypass names are rejected before underlying I/O and ordinary metadata delegation remains available.

This does not alter normal `read()`/`readline()` behavior, configured byte/timeout values, loopback destination policy, proxy/redirect policy, routing, retries, persistence, provenance, audit or cryptography.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until a product-containing canonical Quality run is green.

## Invariants retained

- local model transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation unchanged;
- response-size enforcement remains cumulative and terminal after overflow;
- total response deadline remains fail-closed on successful and HTTP-error paths;
- alternate raw response read APIs cannot bypass bounded `read()`/`readline()` paths;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: local HTTP direct deadline through `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`, Quality `33921338439 = success`.
- READY: HTTP-error deadline `4f94d07f87849aec832437c2ac0dde66bd7433b2` + `08973df26572e66a3ecb26ace403362701e7376e`, Quality `33925587762 = success`.
- READY: terminal size-overflow product `f1fba82ed81bb1fe744fa698bdacc8d25c1a1f8e` + tests `31fa8d4cd25cd9a67a1e43bce22a600a98b98128`, exact descendant `235a13086985341edc02ee61e742e63a863974ab`, Quality `33929643363 = success`.
- NOT READY: alternate-read bypass product `91bf40b1a8cfd72403e4b81061980079460b7c16` + tests `23e914033a1012d7f6901ae86299e49d435a90ed` until canonical green evidence.

## Next backend slice

Consume the exact canonical Quality run containing `23e914033a1012d7f6901ae86299e49d435a90ed`. If green, mark alternative-read bypass hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
