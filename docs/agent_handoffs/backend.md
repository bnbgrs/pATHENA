# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@3ea908affd23f1d80e0b863a6af8cf366e2b8484`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `a3d0a19a499172d1a86f65f0486d3551df647de5`, parents `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` and exact Develop `3ea908affd23f1d80e0b863a6af8cf366e2b8484`.
- `main` remains strict read-only and untouched.

## Storage Health runtime boundaries — VERIFIED

Canonical ATHENA Quality Gate `33868034634` completed `success` on exact worker head `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`.

The verified Storage Health lineage rejects malformed numeric/open-state/text telemetry facts, including bool sizes/time, non-bool open state, non-text path/detail and empty path/detail, while preserving established negative-size and state-consistency contracts.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY` for the bounded Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`.

## ExternalAccessGateway runtime boundaries — EXECUTED / VERIFYING

Current product code on Develop already contains the required fail-before-side-effect guards:

- `authorize_explicit(... ttl_seconds=...)`: exact `int`, bool rejected, established `1..86400` range retained;
- `authorize_direct_fallback(... ttl_seconds=...)`: exact `int`, bool rejected, established `1..900` range retained before authorization lookup;
- `capture_url(... max_bytes=...)`: exact `int`, bool rejected, established safe range retained before authorization lookup/fetch;
- `capture_url(... timeout_seconds=...)`: numeric but not bool, finite via `math.isfinite`, established `(0, 300]` range retained before authorization lookup/fetch.

The named historical patch artifact is not present on the current Develop/Backend trees, so no stale patch was reconstructed or re-applied over already-integrated product code.

Test commit `3bd9e6ae4fd67344d5e8b094747daa5ff7ea405f` adds explicit fail-before-side-effect coverage for bool explicit TTL, bool direct-fallback TTL, bool max_bytes, and bool/NaN/+Inf/-Inf timeout in the dedicated ExternalAccessGateway authorization-boundary harness. Existing `tests/unit/test_external_access_gateway.py` remains part of the canonical regression suite and retains Tor/direct/response-policy/audit/provenance atomicity coverage.

Canonical Quality `33873350238` is associated with exact test head `3bd9e6ae4fd67344d5e8b094747daa5ff7ea405f`; it was `pending` with zero jobs at the latest check. No PASS/READY claim is made for the Gateway slice yet.

## Invariants retained

- no silent Tor -> Direct fallback; Direct remains explicit-only;
- no loopback/private proxy leak relaxation;
- redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no retries or cryptography added;
- no Skip/XFail, assertion weakening or guard relaxation.

## Integrator handoff

- READY: bounded Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`, canonical Quality `33868034634 = success`.
- NOT READY: ExternalAccessGateway runtime-boundary verification commit `3bd9e6ae4fd67344d5e8b094747daa5ff7ea405f` until a real executable run with jobs completes green.

## Next backend slice

First consume Quality `33873350238`. If it executes and passes, mark the Gateway verification lineage READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging runtime gap. If it remains zero-job/pending for the next cycle, use a different executable verification path or a disjoint real Backend slice rather than repeating the same runner blocker.
