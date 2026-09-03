# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@a728668f046bf0d8b66724bb8004a1767bd5589f`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `234df3398e96165bd4df7b628981b9c6e8c21d9c`, retaining prior Backend history while taking the exact Develop tree.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Prior Gateway slice

ExternalAccessGateway TTL/max-bytes/timeout runtime hardening is already integrated on Develop by the Integrator. Backend does not reopen that slice.

## Current selected slice

Area: ExternalAccessGateway explicit authorization runtime boundaries.

Anchor: prior Backend audit findings 295-296 plus current Integrator handoff, which explicitly assigns `authorize_explicit` purpose/allowed-host exact runtime validation to Backend.

Product commit: `7fb68f20e48a463282c4f29e08c531cadc71b60b`.

The mutation is deliberately bounded to `ExternalAccessGateway.authorize_explicit()` and a new focused test file. It adds fail-before-side-effect runtime validation so that:

- `purpose` must be text before `.strip()` is used;
- a naked `str`/`bytes` value is rejected as `allowed_hosts` instead of being iterated as a host sequence;
- non-Sequence host containers are rejected;
- every host element must be text before `_normalize_host()` is called;
- valid tuple/list inputs retain existing normalization, deduplication, sorting and unsafe/local/private destination rejection.

No privacy-route, Tor/Direct, redirect, audit, Source capture, fsync, transaction, provenance, retry, recovery or platform-path semantics changed.

## Call-chain / failure boundary

`authorize_explicit(runtime input) -> purpose runtime validation -> purpose normalization -> allowed_hosts container/element validation -> existing privacy-route validation -> existing TTL validation -> host normalization/deduplication -> unsafe-host rejection -> ensure_local_user -> authorization INSERT/readback`.

Malformed purpose/host runtime values now terminate before `ensure_local_user()` and before any `external_access_authorizations` persistence.

## Verification

Temporary branch-only workflow `Backend Gateway Boundary Apply` was used solely because the local checkout path could not resolve `github.com`. It was removed immediately after the verified product commit; the workflow itself is not part of the product handoff.

Focused run `33802635370` completed SUCCESS. Exact successful steps:

- dependency lock check;
- `tests/unit/test_external_access_gateway_authorization_boundaries.py`;
- `tests/unit/test_external_access_gateway_runtime_boundaries.py`;
- `tests/unit/test_external_access_gateway.py`;
- Ruff on Gateway plus both runtime-boundary test files;
- mypy on `src/athena/external/gateway.py`;
- `git diff --check` before commit.

The new focused tests explicitly monkeypatch `ensure_local_user()` to fail if malformed runtime input reaches actor resolution, and verify no authorization row is written. They also preserve valid host normalization behavior.

Canonical Quality on the cleanup/current worker lineage is running as `33802762604`; do not claim canonical PASS until it completes successfully.

## Commits

- Develop synchronization: `234df3398e96165bd4df7b628981b9c6e8c21d9c`.
- Temporary apply-runner add: `53b961ddb46d95276600abd48d3f555e10c3c510` — tooling only, do not integrate.
- Product + focused tests: `7fb68f20e48a463282c4f29e08c531cadc71b60b`.
- Temporary apply-runner removal: `cadb7682a9271415b7aadc7e78c7e409201139f0`.

## Integrator handoff

`7fb68f20e48a463282c4f29e08c531cadc71b60b` is BOUNDED_FOCUSED_VERIFIED and ready for independent Integrator diff review. It should be integrated only with the product/test files, not the temporary workflow history. Canonical Quality `33802762604` remains additional pending evidence on the current worker lineage.

## Coordination

- Error worker: no new Backend-owned error signature was created by the focused run.
- Core: normal-Hybrid composition is already integrated; no overlap.
- UI: no UI/Qt files touched.
- Backend owns no active UI/Error root cause.

## Next backend slice

After consuming canonical Quality for this slice, inspect the next highest unclaimed Backend/System P0/P1/P2 boundary. First candidate: remaining ExternalAccessGateway exact runtime validation around `privacy_route` / direct-fallback host inputs if current code permits untyped values to escape as generic Python exceptions or reach side effects; otherwise move to the next evidence-backed Research/Jobs/Storage/Recovery/Provider/Packaging gap.
