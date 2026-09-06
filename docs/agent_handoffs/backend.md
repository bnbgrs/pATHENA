# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@8ca3c7b87677a59b9d99d6a5b8703cfc78da6c28`.
- Worker branch pre-run head: `postmerge/backend@a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`.
- Worker heads reviewed: Error `46fb660d7980d83e1b22c061187bae2b99832610`; Spec/Core `0824bc5779d19e53585a315aeee2e468217b3f41`; UI `3c5fe2e16293e9bfb8228e62b0f7a183b34a92f7`; Integrator baseline `8ca3c7b87677a59b9d99d6a5b8703cfc78da6c28`.
- History-preserving NON-FORCE synchronization: `cbcb62e57d590c143bf4d6d58842b2cdc850699f`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving existing valid ranges. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

## Local provider HTTP error-body total deadline — VERIFIED / READY

Product `eaa0c891d794529708917461b600ebe4584ae2a2` propagates the validated request timeout into bounded `HTTPError` bodies. Exact Backend descendant `7b37f0629d3a137301ef04284524a8dfd78c36d3` passed canonical Quality `34001608473 = success`.

## Local provider bounded-read size type stability — FIXED / VERIFY STILL REQUIRED

Product `e6ae4998b675d8ed83efc266fd7d73063e1df63c` requires `_BoundedLocalResponse.read(amt)` to receive `None` or a true non-bool integer and retains the `remaining + 1` overflow probe. Harness correction `5abee1fb3cf9aa639a2600796036302ef63a773d` makes the focused fake response finite/remaining-aware without weakening the product guard.

Canonical Quality `34009015142@5abee1fb3cf9aa639a2600796036302ef63a773d` completed `cancelled`, not success. No PASS/READY claim is made. The identical runner blocker is not repeated in this cycle.

## New disjoint Provider slice — local response body runtime type boundary

Product `2a535bf6d9b1adebfb6a48a27451c72bd9625fba` removes static-only `cast(bytes, ...)` trust at the response boundary. `_BoundedLocalResponse.read()` and `.readline()` now require the delegate result to be actual `bytes` before byte accounting or returning data to provider parsers. `str`, `bytearray`, `memoryview` and other non-byte objects fail closed with `OSError`. The byte counter is not advanced for malformed body values.

Regression commit `2fa14059823873aa249fc2bc3999cd65994ae626` adds read and readline coverage for malformed body types and asserts zero accounting after rejection. No exact workflow run was bound at handoff-write time; no PASS is claimed.

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
- Previously recorded green Storage/DiskPressure Backend lineages remain READY under their exact green SHAs.

NOT READY:
- Bounded-read size type stability + finite harness: `e6ae4998b675d8ed83efc266fd7d73063e1df63c` + `5abee1fb3cf9aa639a2600796036302ef63a773d`; Quality `34009015142 = cancelled`.
- Local response body runtime type boundary: product `2a535bf6d9b1adebfb6a48a27451c72bd9625fba`, tests `2fa14059823873aa249fc2bc3999cd65994ae626`; exact canonical verification not yet available.

## Next backend slice

Consume the first exact canonical run containing `2fa14059823873aa249fc2bc3999cd65994ae626` or its documentation-only descendant. If green, promote both the finite bounded-read harness lineage and response-body runtime type boundary only where exact ancestry supports them, then immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If no run binds, use another executable verification path or a different real disjoint Backend/System slice rather than repeating the cancelled runner state. If red, repair only exact Backend-owned diagnostics without weakening byte/deadline/type, ExternalAccessGateway, persistence, recovery or Windows runtime invariants.