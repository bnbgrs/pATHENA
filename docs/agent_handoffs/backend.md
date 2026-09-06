# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@3bd2b7f0bc25f9b3b756a1765b27db7ab787b789`.
- Worker branch pre-run head: `postmerge/backend@c991482a9f49dec50e69779f73e3a0939df5c73b`.
- Worker heads reviewed: Error `90904477f4810d0580ca42f4be3b9290b703c1a4`; Spec/Core `e5a6c6bd2c84ec6101b93a354ef2515b240fd353`; UI `bf7fadf849140697dc63c92c6a5c6c69335e3278`; Integrator baseline `3bd2b7f0bc25f9b3b756a1765b27db7ab787b789`.
- History-preserving NON-FORCE synchronization: `7ff49ba1facb65fc0e578a39867e4051a36431bc`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving existing valid ranges. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

## Previously verified local-provider lineages — READY

- HTTP-error body total deadline: `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.
- Bounded-read type stability + ERR-0015 harness fix + response bytes boundary: `9dc8375399c6b07f9c52545783004607aa9dd430`, Quality `34011613102 = success`.
- Bounded-response constructor limits: `20edbed46471a50e72661e2e69502b094a0b599f`, Quality `34014111747 = success`.

## Oversize rejection before accounting mutation — NOT READY

Product `5e6862fe9544465e3aed66840601a204d4d2cae5` plus regression `3449aab12922d4ffc15ad576d6b458fd7ef8d1bf` preserves `_bytes_read` when an oversized delegate chunk is rejected. Exact canonical Quality `34016494344@3449aab12922d4ffc15ad576d6b458fd7ef8d1bf` completed `cancelled`, not success. No PASS/READY claim is made.

## New disjoint Provider slice — callable body-delegate boundary

Product `14a6cfdb7adf1e92cbcddf9c6d629afb5ff5106a` makes bounded `read()` and `readline()` require a callable delegate method before invocation. Missing or non-callable delegates now fail closed with `OSError` before body access or byte-accounting mutation instead of surfacing an incidental attribute/call `TypeError`.

Focused regression `c1c6b938f925c9e91cc73ab08ae80e599965a4bb` covers missing/non-callable `read` and non-callable `readline`, and asserts `_bytes_read == 0` after rejection.

Canonical Quality `34019203379` is bound to exact regression head `c1c6b938f925c9e91cc73ab08ae80e599965a4bb` and is currently pending. No PASS/READY claim is made.

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
- Oversized response chunks fail before cumulative byte-accounting state is committed.
- Missing/non-callable body delegates fail before accounting mutation.
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
- Bounded-read / ERR-0015 / response-body runtime bytes boundary: `9dc8375399c6b07f9c52545783004607aa9dd430`, Quality `34011613102 = success`.
- Bounded local response constructor limits: `20edbed46471a50e72661e2e69502b094a0b599f`, Quality `34014111747 = success`.
- Previously recorded green Storage/DiskPressure Backend lineages remain READY under their exact green SHAs.

NOT READY:
- Oversize rejection before accounting mutation: `5e6862fe9544465e3aed66840601a204d4d2cae5` + `3449aab12922d4ffc15ad576d6b458fd7ef8d1bf`; Quality `34016494344 = cancelled`.
- Callable local body-delegate boundary: `14a6cfdb7adf1e92cbcddf9c6d629afb5ff5106a` + `c1c6b938f925c9e91cc73ab08ae80e599965a4bb`; Quality `34019203379 = pending`.

## Next backend slice

Consume exact canonical Quality `34019203379@c1c6b938f925c9e91cc73ab08ae80e599965a4bb` or this documentation descendant. If green, promote only exact-supported Provider lineages READY and immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If red, repair only exact Backend-owned diagnostics without weakening byte/deadline/type, ExternalAccessGateway, persistence, recovery or Windows runtime invariants. If cancelled or otherwise unusable, use another real disjoint Backend/System slice rather than repeating the runner state.
