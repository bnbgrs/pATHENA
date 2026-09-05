# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@a6500b54246c42acb898696bcf009845ce1ecf80`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `4adcf14dc67a617a4a2a5ff942cc600e40aaf456`.
- History-preserving NON-FORCE synchronization: `184c8ca7eb518be7bd8180567d53c1cfd8920f50`, with parents prior Backend head `4adcf14dc67a617a4a2a5ff942cc600e40aaf456` and exact Develop `a6500b54246c42acb898696bcf009845ce1ecf80`.
- Worker heads reviewed: errors handoff observed `postmerge/errors` state with no open error; exact spec-core head `5be34bf266c0a0bda3a80c01ab5337e560ec9255`; exact UI head `2193332eeb3a390c263baa66e83324ff70a61168`; no `postmerge/integrator` branch exists, so current `develop/pathena-next` `integrator.md` was used as the integrator handoff source.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP direct and error-body total deadlines — VERIFIED

Direct-read deadline lineage through `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` passed Quality `33921338439 = success`. HTTP-error deadline product `4f94d07f87849aec832437c2ac0dde66bd7433b2` + tests `08973df26572e66a3ecb26ace403362701e7376e` passed exact descendant Quality `33925587762 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP terminal size-overflow state — VERIFIED

Product `f1fba82ed81bb1fe744fa698bdacc8d25c1a1f8e` + test commit `31fa8d4cd25cd9a67a1e43bce22a600a98b98128` passed exact descendant canonical Quality `33929643363 = success` on Backend head `235a13086985341edc02ee61e742e63a863974ab`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP alternative read API bypass — PRODUCT_FIXED / HARNESS_CORRECTED_PENDING_VERIFY

Product `91bf40b1a8cfd72403e4b81061980079460b7c16` rejects alternative data-consuming response APIs `peek`, `read1`, `readinto`, and `readinto1` before underlying I/O, preventing bypass of the cumulative byte cap and monotonic deadline while retaining ordinary metadata delegation. Focused test commit `23e914033a1012d7f6901ae86299e49d435a90ed` covers the blocked APIs.

Exact descendant Backend head `4adcf14dc67a617a4a2a5ff942cc600e40aaf456` ran canonical Quality `33933291735`. Windows path safety, Linux storage regressions, local install smoke, specification validator, Ruff and mypy passed. Full pytest failed exactly one test: `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline`; canonical diagnostics reported `4625 passed, 3 skipped` plus this one failure.

The product guard was not weakened. Root cause was the pre-existing monotonic timestamp fixture: the wrapper now performs `__iter__` pre-check plus `readline()` pre/post deadline checks and an `__iter__` post-check, so the old four timestamps `[10.0, 10.2, 10.6, 11.0]` reached the deadline during the first yielded line. Test-only commit `e62fcc2db49815e7d32579d0dc68a143f8af07b0` changes the sequence to `[10.0, 10.2, 10.4, 10.6, 10.8, 11.0]`, allowing the first line to complete and expiring before the second underlying read, which is the original behavioral assertion.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

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
- READY: terminal size-overflow product `f1fba82ed81bb1fe744fa698bdacc8d25c1a1f8e` + tests `31fa8d4cd25cd9a67a1e43bce22a600a98b98128`, Quality `33929643363 = success`.
- NOT READY: alternate-read bypass product `91bf40b1a8cfd72403e4b81061980079460b7c16` + focused tests `23e914033a1012d7f6901ae86299e49d435a90ed` + monotonic fixture correction `e62fcc2db49815e7d32579d0dc68a143f8af07b0` until exact descendant canonical green evidence.

## Next backend slice

Consume the exact canonical Quality run containing `e62fcc2db49815e7d32579d0dc68a143f8af07b0`. If green, mark alternative-read bypass hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
