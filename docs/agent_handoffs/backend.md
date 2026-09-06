# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@8236500a5ae0ae58e7dce5bb3cf0771eb534670d`.
- Worker branch pre-run head: `postmerge/backend@a5904fc2078a8dec5eece17dd352436d14453d8f`.
- Worker heads reviewed: Error `90904477f4810d0580ca42f4be3b9290b703c1a4` then current error handoff with `ERR-0016`; Spec/Core `a43a471b611c78d24ebb8c67253b855b6a0642f3`; UI `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4`; Integrator baseline `8236500a5ae0ae58e7dce5bb3cf0771eb534670d`.
- History-preserving NON-FORCE synchronization: `cd05768f396ecd0eac44fec5d9f1305efb88ac66`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving existing valid ranges. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

## ERR-0016 — fix applied, pending canonical verification

Exact Error-worker evidence on Backend descendant `a5904fc2078a8dec5eece17dd352436d14453d8f` showed full pytest failing exactly the two overflow-poisoning regressions while Windows path safety, Linux storage, local install smoke, Validator, Ruff and mypy passed. The oversize-before-accounting change correctly avoided counting rejected bytes but accidentally removed the fail-closed poisoned state used to block subsequent underlying I/O.

Product fix `d721846ea9524ab18336ba72eeb082cca7ee0fb8` introduces an explicit `_byte_budget_poisoned` state. An oversized returned chunk sets the poison flag before raising `LocalResponseTooLargeError`; `_bytes_read` remains unchanged because rejected bytes are not successful consumption. Every subsequent bounded `read()`/`readline()` is rejected by `_assert_within_byte_budget()` before delegate access.

Regression commit `44bf215b999e727514fc10ddb88eb8379a5358b6` updates the oversize-accounting tests to prove both required truths simultaneously: rejected bytes do not advance `_bytes_read`, and follow-up body access is blocked without another underlying read/readline call. Existing canonical poisoning tests remain untouched. No exact workflow run is currently bound to the fix SHA, so ERR-0016 is FIXED_PENDING_VERIFY, not closed.

## Previously verified local-provider lineages — READY

- HTTP-error body total deadline: `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.
- Bounded-read type stability + ERR-0015 harness fix + response bytes boundary: `9dc8375399c6b07f9c52545783004607aa9dd430`, Quality `34011613102 = success`.
- Bounded-response constructor limits: `20edbed46471a50e72661e2e69502b094a0b599f`, Quality `34014111747 = success`.

## Persistent runtime / crash prevention invariants

- Frozen Windows packaging retains `pypdf` distribution metadata; historical `PackageNotFoundError`/supervisor relaunch must not recur.
- Unknown frozen child argv remains fail-closed; preserve `pATHENA.exe` Desktop / `pATHENA-Worker.exe` Worker separation.
- Windows runtime retains exactly one Desktop process and bounded/non-growing Worker population.
- Direct Chat retains adaptive output reserve for small LM Studio contexts, including 2048-context coverage.
- Windows lane-lock/scheduler/startup crash cluster remains Beta/release acceptance coverage: `_lock_nonblocking` `PermissionError [Errno 13]`, `SchedulerLaneOwnershipError`, packaged-worker `OSError [Errno 22]`.
- Preserve startup signatures `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'` as prevent-regression knowledge; reopen only on exact-SHA reproduction.

## Invariants retained

- Local model transport remains loopback-only, proxy-free and redirect-rejecting.
- Successful and HTTP-error bodies remain byte-bounded and total-deadline-bounded.
- Non-byte response bodies fail closed before byte accounting.
- Oversized response chunks are not counted as successful consumption and permanently poison further bounded body access.
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
- ERR-0016 explicit overflow poison fix: `d721846ea9524ab18336ba72eeb082cca7ee0fb8` + regression `44bf215b999e727514fc10ddb88eb8379a5358b6`; awaiting exact canonical Quality.
- Callable local body-delegate boundary remains included in the same descendant but its exact earlier Quality `34019203379` was cancelled; promote only after a successful exact descendant run.

## Next backend slice

Consume the first exact canonical Quality run containing `44bf215b999e727514fc10ddb88eb8379a5358b6` or this documentation descendant. If green, close ERR-0016 and promote only exact-supported Provider lineages READY, then immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If red, inspect exact diagnostics and minimally repair Backend-owned failure without weakening poison, byte/deadline/type, ExternalAccessGateway, persistence, recovery or Windows runtime invariants. If no run binds, use an alternate executable verification path or another real disjoint Backend/System slice rather than repeating runner state.
