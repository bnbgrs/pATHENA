# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@fdbf882eede84bfcc5debc6cfffc311fdfb1e440`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `15c06e210952aabcb49c22f08e92ed0c0c73272e`.
- Worker heads reviewed: errors `32d59d7b43bbd6d6cf4108ba8b00b6f8726645a7`, spec-core `88b9bad5a3c6cd028b421cafc2e7fb65caeb6a53`, ui `525ae04361dd29cc4a9e05f62f810c5ec47ac16d`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- History-preserving NON-FORCE synchronization: `2d2d09907806ecf633a48cd614ef2b6ffe7c924a`, with parents prior Backend head `15c06e210952aabcb49c22f08e92ed0c0c73272e` and exact Develop `fdbf882eede84bfcc5debc6cfffc311fdfb1e440`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP file-descriptor escape — VERIFIED

Product `58ddb559a69f0278225a439c9118617b51bab7bc` rejects delegated `fileno` so callers cannot obtain the underlying response descriptor and perform body I/O outside cumulative byte and total-deadline enforcement. Focused tests `5f38ed071b384021395f084ca53aab6575a71b96` verify fail-before-I/O rejection. Exact Backend descendant `15c06e210952aabcb49c22f08e92ed0c0c73272e` passed canonical ATHENA Quality `33944818290 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health open-path invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

A malformed runtime `StorageHealthSnapshot` could previously claim `database_open=True` while carrying `database_path=None`. That contradicts the live-database boundary and weakens truthful storage telemetry/provenance.

Product commit `114aee1b46f199548c0b87c1c0ae431e240fee94` now rejects every open snapshot without a concrete database path before the status-specific state is accepted. Existing valid available/unavailable/error states remain unchanged.

Focused test commit `bac92f7fa682b551369ace821f46c18cc9743f76` covers the previously accepted contradictory open-error state with `database_path=None`.

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
- NOT READY: StorageHealth open-path product `114aee1b46f199548c0b87c1c0ae431e240fee94` + tests `bac92f7fa682b551369ace821f46c18cc9743f76` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `bac92f7fa682b551369ace821f46c18cc9743f76` or a documentation-only descendant. If green, mark StorageHealth open-path hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
