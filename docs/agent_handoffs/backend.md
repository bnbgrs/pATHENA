# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@8c2f08ef5a9dcafd9cf029da944527d97313cd2b`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `2d5b22801d5889c374ae1a75bd9880e3070e21c4`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- Worker heads reviewed: errors `6ccac5e5add098e4981f7d95d5fc912ca776259f`, spec-core `1ed4b9c4b2e41c52f787e1a9e26f9d2e523a89ce`, ui `9f24999c62b309e25ac512a110ef18011225a4cc`.
- History-preserving NON-FORCE synchronization: `220bd47b2f17508b61fe6c18a25ffe6d01583dba`, with parents prior Backend head `2d5b22801d5889c374ae1a75bd9880e3070e21c4` and exact Develop `8c2f08ef5a9dcafd9cf029da944527d97313cd2b`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health NUL-detail invariant — VERIFIED

Product `60af3d61e687108fb07ed3569dd5459f4721b551` rejects NUL-containing `detail` strings. Focused tests `8bb2adb2951900a0389eab57e1d4735b87cb0d29` cover all-NUL and embedded-NUL diagnostics. Exact Backend descendant `2d5b22801d5889c374ae1a75bd9880e3070e21c4` passed canonical ATHENA Quality `33960721888 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health single-line detail invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

`StorageHealthSnapshot.detail` is propagated into status/transport/presentation surfaces. Embedded CR/LF sequences could therefore produce multiline diagnostic payloads despite the boundary representing one diagnostic fact.

Product commit `9183cf1d5c5bae6831b7a31302a7aee8eb856ff4` rejects non-None detail values containing `\r` or `\n` after the existing non-empty, non-whitespace and NUL guards and before state-specific acceptance. Existing service-generated diagnostics are already single-line and remain unchanged.

Focused test commit `e074bd13d77b92821d9b84ecd803ef3c22c081c1` covers LF, CR and CRLF embedded diagnostic text and requires fail-closed rejection.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- storage telemetry remains read-only and does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source finalization semantics changed;
- valid Windows/Linux storage paths and valid single-line diagnostic text remain unchanged;
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
- READY: StorageHealth NUL-detail product `60af3d61e687108fb07ed3569dd5459f4721b551` + tests `8bb2adb2951900a0389eab57e1d4735b87cb0d29` through exact green Backend head `2d5b22801d5889c374ae1a75bd9880e3070e21c4`, Quality `33960721888 = success`.
- NOT READY: StorageHealth single-line-detail product `9183cf1d5c5bae6831b7a31302a7aee8eb856ff4` + tests `e074bd13d77b92821d9b84ecd803ef3c22c081c1` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `e074bd13d77b92821d9b84ecd803ef3c22c081c1` or a documentation-only descendant. If green, mark StorageHealth single-line-detail hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
