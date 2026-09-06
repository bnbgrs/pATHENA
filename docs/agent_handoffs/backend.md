# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@fd15a75212acac7f88886117835b8d754577ea91`.
- Worker branch pre-run head: `postmerge/backend@9dc8375399c6b07f9c52545783004607aa9dd430`.
- Worker heads reviewed: Error `2b42d3acfc11cf3862659e272ff920cd43f77873`; Spec/Core `b4d7ac9d0102981b133983c5fa93e113e2df4360`; UI `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea`; Integrator baseline `fd15a75212acac7f88886117835b8d754577ea91`.
- History-preserving NON-FORCE synchronization: `537604cd2350a9db102abd99e0bc8a8a1ca4db28`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving existing valid ranges. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

## Local provider bounded-read + response-body boundaries — VERIFIED / READY

Exact Backend documentation descendant `9dc8375399c6b07f9c52545783004607aa9dd430` passed canonical ATHENA Quality `34011613102 = success`.

That exact green ancestry contains:

- bounded read-size true-int validation product `e6ae4998b675d8ed83efc266fd7d73063e1df63c`;
- finite/remaining-aware regression harness fix `5abee1fb3cf9aa639a2600796036302ef63a773d` closing ERR-0015 without weakening the `remaining + 1` overflow probe;
- local response-body runtime bytes boundary product `2a535bf6d9b1adebfb6a48a27451c72bd9625fba` and regression `2fa14059823873aa249fc2bc3999cd65994ae626`.

The earlier Local-provider HTTP error-body total deadline remains READY under `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.

## New disjoint Provider slice — bounded response constructor limits

Product `575f3a722ad682e80ea5ac05af2c23d326c75922` hardens `_BoundedLocalResponse` at construction time:

- `max_bytes` must be a true non-bool positive integer;
- `total_timeout_seconds`, when supplied, is routed through the existing finite-positive numeric timeout validator, rejecting bool, zero/negative, NaN and +/-Inf before response use;
- valid runtime callers using `MAX_LOCAL_RESPONSE_BYTES` plus the already validated request timeout are unchanged.

Focused regression `3eca7fce6ffedfff15bdfeb252db63d88b671de6` covers invalid byte limits, invalid total deadlines and a valid constructor case. Canonical Quality `34014086876` is bound to the exact test head and was `pending` at handoff-write time; no PASS/READY claim is made for this new slice yet.

## Persistent runtime / crash prevention invariants

- Frozen Windows packaging retains `pypdf` distribution metadata; historical `PackageNotFoundError`/supervisor relaunch must not recur.
- Unknown frozen child argv remains fail-closed; preserve `pATHENA.exe` Desktop / `pATHENA-Worker.exe` Worker separation.
- Windows runtime retains exactly one Desktop process and bounded/non-growing Worker population.
- Direct Chat retains adaptive output reserve for small LM Studio contexts, including 2048-context coverage, without weakening safety/context guards.
- Windows lane-lock/scheduler/startup crash cluster remains Beta/release acceptance coverage: `_lock_nonblocking` `PermissionError [Errno 13]`, `SchedulerLaneOwnershipError`, packaged-worker `OSError [Errno 22]`.
- Preserve startup signatures `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'` as prevent-regression knowledge; reopen only on exact-SHA reproduction.

## Invariants retained

- Local model transport remains loopback-only, proxy-free and redirect-rejecting.
- Successful and HTTP-error bodies remain byte-bounded and total-deadline-bounded.
- Non-byte response bodies fail closed before byte accounting.
- No new retries, provider routing behavior or cryptography.
- No silent Tor -> Direct fallback; Direct remains explicit-only.
- ExternalAccessGateway redirect reauthorization, HTTPS/default-port fail-closed policy, compressed-response rejection and response-size bounds remain unchanged.
- Audit, provenance, fsync and transactional Source-finalization semantics remain unchanged.
- Storage/DiskPressure truth contracts, SQLite/WAL, persistence format and recovery protocol remain unchanged.
- No Skip/XFail, assertion weakening or guard relaxation.
- No merge to `main`, force-push or history rewrite.

## Integrator handoff

READY:
- ExternalAccessGateway runtime boundaries: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- Local-provider HTTP error-body deadline: `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.
- Bounded-read size type stability + ERR-0015 harness correction + response-body runtime bytes boundary: exact green successor `9dc8375399c6b07f9c52545783004607aa9dd430`, Quality `34011613102 = success`.
- Previously recorded green Storage/DiskPressure Backend lineages remain READY under their exact green SHAs.

NOT READY:
- Bounded response constructor limits: product `575f3a722ad682e80ea5ac05af2c23d326c75922`, tests `3eca7fce6ffedfff15bdfeb252db63d88b671de6`; Quality `34014086876 = pending` at handoff-write time.

## Next backend slice

Consume exact canonical Quality `34014086876@3eca7fce6ffedfff15bdfeb252db63d88b671de6` or an exact documentation-only descendant. If green, promote bounded response constructor limits VERIFIED/READY and immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If red, repair only exact Backend-owned diagnostics without weakening byte/deadline/type, ExternalAccessGateway, persistence, recovery or Windows runtime invariants. If no usable run binds, use a different real disjoint Backend/System slice rather than repeating runner state.
