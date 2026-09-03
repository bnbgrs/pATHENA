# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@a76537a1002e323a97d18a0a95a4d39ce5f298ee`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `2ee92e0f776ab5333039c7cbd6912d19d36b273b`, preserving the prior Backend history while using the exact current Develop tree.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Current backend slice — capture URL runtime type boundary

Area: `ExternalAccessGateway.capture_url()` fail-before-side-effect runtime validation.

Current Develop validates `max_bytes` and `timeout_seconds` before authorization, but a non-text `url` was passed into `_authorized_or_audit()` first. That path can perform authorization lookup and local-actor resolution before `_require_authorized()` eventually calls `urlsplit(url)`. This is inconsistent with the established Gateway runtime-boundary pattern for malformed caller input.

Product/test commit: `07782c78d6e2cb1e9f4bfb6bf9175c9fb041a806`.

The production change is intentionally minimal: `capture_url()` now rejects non-text `url` values with `ExternalDestinationError("External URL must be text.")` before max-bytes/timeout processing and, critically, before authorization/audit/actor/transport/Source paths. Valid string URLs continue through the existing authorization, destination, redirect, audit, transport and transactional capture logic unchanged.

Focused coverage in `tests/unit/test_external_access_gateway_authorization_boundaries.py` exercises `None`, integer, bool, bytes and list URL values while monkeypatching `_authorized_or_audit()` to fail if the malformed input reaches authorization lookup.

Independent tree comparison from synchronized Backend `2ee92e0f776ab5333039c7cbd6912d19d36b273b` to product commit `07782c78d6e2cb1e9f4bfb6bf9175c9fb041a806` shows an effective net delta of only:

- `src/athena/external/gateway.py`: +2 / -0;
- `tests/unit/test_external_access_gateway_authorization_boundaries.py`: bounded test update.

A temporary verifier workflow was created in tooling commit `bf3b957cbe409db7456f0fc7f261f448f08d679b`, but connector-originated push behavior did not execute that temporary workflow. It is absent from the final product tree and must never be integrated.

## Call-chain / retained invariants

New malformed-input boundary:

`capture_url(runtime input) -> URL text guard -> existing max_bytes guard -> existing timeout guard -> authorization/audit -> privacy route -> redirect reauthorization -> transport -> response policy -> fsync staging -> transactional Source/audit/provenance finalize`.

Retained invariants:

- no silent Tor to Direct fallback;
- Direct fallback remains explicitly authorized only;
- loopback/private destination and proxy-leak protections unchanged;
- every redirect is still re-authorized before fetch;
- HTTPS/default-port policy remains fail-closed;
- compressed-response and response-size policies unchanged;
- audit/provenance/fsync/transactional Source-finalization semantics for valid text URLs unchanged;
- no retry, cryptography, storage, recovery or platform-path behavior changed.

## Verification state

Canonical Quality run `33818120429` is associated with exact product SHA `07782c78d6e2cb1e9f4bfb6bf9175c9fb041a806`. At this handoff update it is still pending and has not produced exact-head jobs, therefore no PASS or Integrator-READY claim is made yet.

Baseline/synchronization Quality run `33817819189` on pre-slice sync SHA `2ee92e0f776ab5333039c7cbd6912d19d36b273b` currently shows Linux storage, Local install smoke and Windows path safety PASS; its Python quality job has specification validator, Ruff and mypy PASS while full pytest is still running. This is useful baseline-health evidence only and is not treated as verification of the new URL guard.

Local checkout remained unavailable because DNS resolution of `github.com` failed. Per the established worker rule, mutation used complete GitHub blobs/tree construction and NON-FORCE ref advancement rather than treating DNS as a durable blocker.

## Coordination

- Error: no new confirmed Backend regression has been observed from this bounded mutation; exact product Quality remains pending.
- Core: no Core-owned Chat/Knowledge/PALLAS/Search-semantic files changed.
- UI: no Qt/UI files changed.
- Integrator: do not integrate this slice until exact product run `33818120429` completes green (or later equivalent exact-content evidence exists). Then independently review only the two-file product/test delta from `07782c78d6e2cb1e9f4bfb6bf9175c9fb041a806`; exclude temporary workflow history.

## Next backend slice

First consume exact Quality `33818120429`. If green, inspect `ExternalResearchService.enqueue(urls=...)` for a real runtime-boundary gap: current normalization iterates the supplied container and invokes `.strip()` on elements, so naked string/bytes containers or non-text elements may bypass a clear fail-closed contract or fail with incidental Python exceptions before Gateway capture. Only harden if reproduced and supported by the existing external-Research contract, and preserve Gateway authorization/audit semantics. If exact Quality is red, classify and correct that failure before taking a new slice.
