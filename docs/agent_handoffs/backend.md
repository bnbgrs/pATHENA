# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@5c5cb8d3011f3fb1c7df01faeeacaf1b0033e2d8`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `cb23f971ac68ed5c4cf67a5638efc6a44a9c3fb2`.
- Worker heads reviewed: errors `af81167e35c0c8f7eda24fd8a818c1532cbb89da`, spec-core `e2c04019465ed9499e8e66ad6d97901c6591d4ef`, ui `f2cc20321c79809a37079b0525b2aab676ac8682`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- History-preserving NON-FORCE synchronization: `11551b4b2827862c3e7268fbcdf14c7f12e068b6`, with parents prior Backend head `cb23f971ac68ed5c4cf67a5638efc6a44a9c3fb2` and exact Develop `5c5cb8d3011f3fb1c7df01faeeacaf1b0033e2d8`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP file-descriptor escape — VERIFIED

Product `58ddb559a69f0278225a439c9118617b51bab7bc` rejects delegated `fileno` so callers cannot obtain the underlying response descriptor and perform body I/O outside cumulative byte and total-deadline enforcement. Focused tests `5f38ed071b384021395f084ca53aab6575a71b96` verify fail-before-I/O rejection. Exact Backend descendant `15c06e210952aabcb49c22f08e92ed0c0c73272e` passed canonical ATHENA Quality `33944818290 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health open-path invariant — VERIFIED

Product `114aee1b46f199548c0b87c1c0ae431e240fee94` rejects `database_open=True` snapshots without a concrete database path. Focused test commit `bac92f7fa682b551369ace821f46c18cc9743f76` covers the previously accepted contradictory open-error state. Exact Backend descendant `cb23f971ac68ed5c4cf67a5638efc6a44a9c3fb2` passed canonical ATHENA Quality `33947479509 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health whitespace-path invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

A runtime `StorageHealthSnapshot` could still claim a database identity such as `" "`, `"\t"`, or newline-only text. That is not a concrete filesystem identity and could make an open/error health snapshot appear grounded while carrying no usable database path.

Product commit `ca790d2e79477ecc23f7654e5544d171fe13e647` now rejects a non-None `database_path` whose text contains only whitespace, before status-specific state is accepted. Valid Windows/Linux paths and existing unavailable/available/error semantics are unchanged.

Focused test commit `5b381076659f75a80666100045a73562eb68acd7` covers space-, tab-, and CRLF-only database paths.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- storage telemetry remains read-only and does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source finalization semantics changed;
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
- READY: local HTTP file-descriptor escape product `58ddb559a69f0278225a439c9118617b51bab7bc` + tests `5f38ed071b384021395f084ca53aab6575a71b96` through exact green Backend head `15c06e210952aabcb49c22f08e92ed0c0c73272e`, Quality `33944818290 = success`.
- READY: StorageHealth open-path product `114aee1b46f199548c0b87c1c0ae431e240fee94` + tests `bac92f7fa682b551369ace821f46c18cc9743f76` through exact green Backend head `cb23f971ac68ed5c4cf67a5638efc6a44a9c3fb2`, Quality `33947479509 = success`.
- NOT READY: StorageHealth whitespace-path product `ca790d2e79477ecc23f7654e5544d171fe13e647` + tests `5b381076659f75a80666100045a73562eb68acd7` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `5b381076659f75a80666100045a73562eb68acd7` or a documentation-only descendant. If green, mark StorageHealth whitespace-path hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
