# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@14ca6fece527d6b51956b3e5fa3ec7b291252420`.
- Worker branch pre-run head: `postmerge/backend@20edbed46471a50e72661e2e69502b094a0b599f`.
- Worker heads reviewed: Error `3392f70d4c4c0830fefe2833d098bed34fa2127b`; Spec/Core `f7e29299871394fb78d9129a4436b9cedcaee3a3`; UI `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`; Integrator baseline `14ca6fece527d6b51956b3e5fa3ec7b291252420`.
- History-preserving NON-FORCE synchronization: `56a78635a8404ac4d7fb1aa2129d1ef2054040bb`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving existing valid ranges. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

## Local provider bounded response constructor limits — VERIFIED / READY

Exact Backend documentation descendant `20edbed46471a50e72661e2e69502b094a0b599f` passed canonical ATHENA Quality `34014111747 = success`.

That exact green ancestry contains product `575f3a722ad682e80ea5ac05af2c23d326c75922` plus regression `3eca7fce6ffedfff15bdfeb252db63d88b671de6`:

- `_BoundedLocalResponse.max_bytes` requires a true non-bool positive integer;
- supplied `total_timeout_seconds` is validated as finite, positive and non-bool before response use;
- valid production callers using `MAX_LOCAL_RESPONSE_BYTES` plus validated provider request timeouts are unchanged.

Previously verified local-provider lineages remain READY: HTTP-error body total deadline under `7b37f0629d3a137301ef04284524a8dfd78c36d3` / Quality `34001608473`; bounded-read type stability + ERR-0015 harness fix + response bytes boundary under `9dc8375399c6b07f9c52545783004607aa9dd430` / Quality `34011613102`.

## New disjoint Provider slice — oversize rejection before accounting mutation

Product `5e6862fe9544465e3aed66840601a204d4d2cae5` changes bounded `read()` and `readline()` accounting so an oversized delegate chunk is checked against the cumulative byte limit before `_bytes_read` is committed. The existing `remaining + 1` overflow probe, exception type and byte cap remain unchanged.

Focused regression `3449aab12922d4ffc15ad576d6b458fd7ef8d1bf` verifies both read and readline overflow paths leave `_bytes_read == 0` when the first returned chunk exceeds the configured cap.

Canonical Quality `34016494344` is bound to the exact regression head and is pending; no PASS/READY claim is made for this new slice.

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
- Oversized response chunks now fail before cumulative byte-accounting state is committed.
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
- Bounded-read size type stability + ERR-0015 harness correction + response-body runtime bytes boundary: `9dc8375399c6b07f9c52545783004607aa9dd430`, Quality `34011613102 = success`.
- Bounded local response constructor limits: `20edbed46471a50e72661e2e69502b094a0b599f`, Quality `34014111747 = success`.
- Previously recorded green Storage/DiskPressure Backend lineages remain READY under their exact green SHAs.

NOT READY:
- Oversized local response rejection before accounting mutation: product `5e6862fe9544465e3aed66840601a204d4d2cae5`, tests `3449aab12922d4ffc15ad576d6b458fd7ef8d1bf`; Quality `34016494344 = pending`.

## Next backend slice

Consume exact canonical Quality `34016494344@3449aab12922d4ffc15ad576d6b458fd7ef8d1bf` or an exact documentation-only descendant. If green, promote oversize-before-accounting semantics VERIFIED/READY and immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If red, repair only exact Backend-owned diagnostics without weakening byte/deadline/type, ExternalAccessGateway, persistence, recovery or Windows runtime invariants. If no usable run binds, use a different real disjoint Backend/System slice rather than repeating runner state.
