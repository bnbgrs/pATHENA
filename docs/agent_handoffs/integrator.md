# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `859e1a68e8d9a207a5094462aefe189f6f276c9d`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `46fb660d7980d83e1b22c061187bae2b99832610`; spec-core `396a66302d0e4e96deb2d69076fdaa340bb395c5`; backend `a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`; ui `3c5fe2e16293e9bfb8228e62b0f7a183b34a92f7`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — local-provider HTTP error-body total deadline

READY Backend lineage independently reviewed:

- product commit `eaa0c891d794529708917461b600ebe4584ae2a2`;
- focused regression commit `18710d1441206c8282f7c7dacae15f8116365c17`;
- exact-green Backend descendant `7b37f0629d3a137301ef04284524a8dfd78c36d3`;
- canonical Quality `34001608473 = success`.

Compatibility review against the product parent `61d2755651657859cfa2ae78bf8ff232d826c494` showed current Develop had not changed `src/athena/model/adapters/local_http.py`; Develop-only changes were Integrator, Personal Memory, and DiskPressure files. The exact verified product blob was therefore applied without importing unrelated Backend history. The focused test `tests/unit/test_local_http_error_body_timeout.py` was added unchanged from its verified worker commit.

Develop integration commits:

- product `8d82b55a621f5e597893043eba3e37ed7ec3bc1d`;
- focused test `0b0d1b3fb9c5abca821b107078d177e78c5bfc62`.

## Contract now covered

HTTP provider-error bodies inherit the already validated per-request total timeout before provider-specific parsing. `_bound_http_error_body()` wraps the error stream with `_BoundedLocalResponse` using both the existing byte cap and the same validated total timeout. Loopback-only routing, proxy rejection, redirect rejection, normal success-body byte/deadline bounds, provider routing and error semantics remain unchanged.

## Validation state

- Exact worker lineage passed canonical ATHENA Quality `34001608473` with conclusion `success`.
- Focused regression proves a wrapped HTTP error body raises `TimeoutError` after its inherited total deadline.
- Independent compatibility review found no Develop mutation to the product file since the worker product parent.
- Exact-current-Develop repository-wide green is not yet claimed; no post-integration Quality result is bound to the new Develop SHA at handoff-write time.
- `ALPHA_BETA_PROGRESS.md` was re-read, but connector retrieval is truncated; unsafe whole-file replacement was not attempted. Evidence is retained here until a safe patch-capable update is available.

## Other current inputs

- Backend ExternalAccessGateway runtime boundaries remain VERIFIED/READY in their exact green lineage but were not re-integrated because Develop already carries the contract.
- Backend bounded-read size-type stability remains pending its exact canonical verification in the current Backend handoff and was not consumed.
- Error worker currently has no independently verified new exact-SHA blocker requiring this Integrator slice to stop.
- Eleven UI screens remain implemented pending visual review; pixel-level MATCH remains unclaimed.

## Runtime/release guards retained

Known Windows pypdf packaging, fail-closed frozen argv routing, bounded process tree, adaptive 2048-context DirectChat budgeting, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster and storage-bootstrap/migration startup signatures remain explicit Beta/release regression requirements. This Backend slice does not alter their owning code.

## Next integration order

1. Prefer any newer exact-green bounded Core composition successor after independent compatibility review.
2. Otherwise consume exactly one compatible READY Backend/UI successor; do not absorb the bounded-read size-type successor until its own exact canonical run is green.
3. Obtain exact-current-Develop Quality before repository-wide green or promotion-ready claims.
4. Before Beta/release readiness, explicitly regress all retained Windows packaging/process-tree/startup/chat-context/lane-lock crash classes on the exact candidate SHA.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
