# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@7710c7aaa82b4fe4725238cbe8f84d5be9ed3017`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `f7913b50618998b9b16a48ae9a810ed9122b64bc`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff; worker branches were checked before mutation.
- History-preserving NON-FORCE synchronization: `2d368ace89999867d9ddc75df0555f30b304ea41`, with parents prior Backend head `f7913b50618998b9b16a48ae9a810ed9122b64bc` and exact Develop `7710c7aaa82b4fe4725238cbe8f84d5be9ed3017`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health single-line detail invariant — VERIFIED

Product `9183cf1d5c5bae6831b7a31302a7aee8eb856ff4` rejects CR/LF-containing `detail` strings and tests `e074bd13d77b92821d9b84ecd803ef3c22c081c1` cover LF/CR/CRLF payloads. Exact Backend descendant `f7913b50618998b9b16a48ae9a810ed9122b64bc` passed canonical ATHENA Quality `33963593580 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health ASCII-control detail invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

`StorageHealthSnapshot.detail` is a single diagnostic fact propagated into status, log and presentation surfaces. Embedded C0 or DEL control characters can alter rendering or downstream text framing even when CR/LF and NUL are already rejected.

Product commit `09893113ec42337db2c590bac99263db393f75e4` adds a fail-closed ASCII-control guard after the existing non-empty, non-whitespace, NUL and single-line guards. Existing service-generated diagnostics contain no control characters and remain unchanged.

Focused test commit `454ae52cae8baeaec82a787dabb588e8ecf2ff6a` covers embedded TAB, backspace, vertical-tab, form-feed and DEL characters and requires rejection before state-specific acceptance.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- storage telemetry remains read-only and does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source-finalization semantics changed;
- valid Windows/Linux storage paths and ordinary diagnostic text remain unchanged;
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
- READY: StorageHealth single-line-detail product `9183cf1d5c5bae6831b7a31302a7aee8eb856ff4` + tests `e074bd13d77b92821d9b84ecd803ef3c22c081c1` through exact green Backend head `f7913b50618998b9b16a48ae9a810ed9122b64bc`, Quality `33963593580 = success`.
- NOT READY: StorageHealth ASCII-control-detail product `09893113ec42337db2c590bac99263db393f75e4` + tests `454ae52cae8baeaec82a787dabb588e8ecf2ff6a` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `454ae52cae8baeaec82a787dabb588e8ecf2ff6a` or a documentation-only descendant. If green, mark ASCII-control-detail hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
