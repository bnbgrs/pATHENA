# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@f9938b0f3c3a016b1cc7837441caaec72974e1cf`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `cdc61439364028d29ecc56f3c39d34cd9a3dcc12`.
- History-preserving NON-FORCE synchronization: `70221dfda715b96a4b6b01f3e511e3127026b6f2`, with parents prior Backend head `cdc61439364028d29ecc56f3c39d34cd9a3dcc12` and exact Develop `f9938b0f3c3a016b1cc7837441caaec72974e1cf`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP delegated bulk-read escape — VERIFIED

Product `0d0844a70d6e825253ec15e5544b8b716990dad0` rejects delegated `readall()` and `readlines()` so callers cannot bypass bounded `read()` / `readline()`, cumulative byte accounting, overflow poisoning, or the monotonic total deadline. Focused tests `f55f092b5d20568f20f1172dd6500bc4a55c7f31` verify fail-before-underlying-I/O rejection. Exact Backend descendant `cdc61439364028d29ecc56f3c39d34cd9a3dcc12` passed canonical ATHENA Quality `33941852514 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP file-descriptor escape — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

Product commit `58ddb559a69f0278225a439c9118617b51bab7bc` closes a distinct wrapper escape: delegated `fileno` could expose the underlying response file descriptor and allow direct I/O outside cumulative byte and total-deadline enforcement. `fileno` is now rejected through the existing raw-body-handle fail-closed boundary.

Focused test commit `5f38ed071b384021395f084ca53aab6575a71b96` extends the raw-body-handle rejection harness to `fileno` and verifies rejection without underlying body reads while ordinary metadata delegation remains unchanged.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- local model transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation unchanged;
- response-size enforcement remains cumulative and terminal after overflow;
- total response deadline remains fail-closed on successful and HTTP-error paths;
- delegated alternative/bulk response read APIs, raw body handles, and file-descriptor escape cannot bypass bounded access;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: delegated bulk-read product `0d0844a70d6e825253ec15e5544b8b716990dad0` + tests `f55f092b5d20568f20f1172dd6500bc4a55c7f31` through exact green Backend head `cdc61439364028d29ecc56f3c39d34cd9a3dcc12`, Quality `33941852514 = success`.
- NOT READY: file-descriptor escape product `58ddb559a69f0278225a439c9118617b51bab7bc` + tests `5f38ed071b384021395f084ca53aab6575a71b96` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `5f38ed071b384021395f084ca53aab6575a71b96`. If green, mark file-descriptor escape hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
