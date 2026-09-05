# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@d69fcc570bceac78536614f40b0ae3e1b867d791`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `7d380631f69b8b9b9f580f01f4510760f11de577`.
- History-preserving NON-FORCE synchronization: `ca1750d681e6ff521fba01211ef4947df5c923a3`, with parents prior Backend head `7d380631f69b8b9b9f580f01f4510760f11de577` and exact Develop `d69fcc570bceac78536614f40b0ae3e1b867d791`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP raw body-handle escape — VERIFIED

Product `05730b74a2bb64aa240b6199a0476bd3e0c83998` rejects delegated `fp`, `file`, and `raw` body-handle attributes before escape. Focused tests `202d2f6ac5d3c0e7da4dede2e381d838f25abf8f` prove rejection before underlying body consumption. Exact descendant Backend head `7d380631f69b8b9b9f580f01f4510760f11de577` passed canonical ATHENA Quality `33939326942 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP delegated bulk-read escape — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

Product commit `0d0844a70d6e825253ec15e5544b8b716990dad0` closes a distinct response-wrapper escape: delegated `readall()` and `readlines()` methods could bypass `_BoundedLocalResponse.read()` / `.readline()`, cumulative byte accounting, overflow poisoning, and the monotonic total deadline. They are now rejected through the same fail-closed delegated-read boundary as `peek`, `read1`, `readinto`, and `readinto1`.

Focused test commit `f55f092b5d20568f20f1172dd6500bc4a55c7f31` extends the existing parameterized rejection harness to `readall` and `readlines` and verifies rejection before underlying I/O while metadata delegation remains unchanged.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- local model transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation unchanged;
- response-size enforcement remains cumulative and terminal after overflow;
- total response deadline remains fail-closed on successful and HTTP-error paths;
- delegated alternative/bulk response read APIs and raw body-handle attributes cannot bypass bounded `read()`/`readline()` paths;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: raw body-handle escape product `05730b74a2bb64aa240b6199a0476bd3e0c83998` + tests `202d2f6ac5d3c0e7da4dede2e381d838f25abf8f` through exact green Backend head `7d380631f69b8b9b9f580f01f4510760f11de577`, Quality `33939326942 = success`.
- NOT READY: delegated bulk-read product `0d0844a70d6e825253ec15e5544b8b716990dad0` + tests `f55f092b5d20568f20f1172dd6500bc4a55c7f31` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `f55f092b5d20568f20f1172dd6500bc4a55c7f31`. If green, mark delegated bulk-read hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
