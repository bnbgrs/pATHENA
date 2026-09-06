# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@451b2f39377653b44fb178e58d86705b6026bef8`.
- Worker branch pre-run head: `postmerge/backend@d6fca835ad432e05aecbdc3c790a55ec2691a11b`.
- Worker heads reviewed: Error `b8e050c9756299a70e8f5d4df0139ef54a5f08a0`; Spec/Core `96c8f17d99017060238da27b51f6e59b77b9eafc`; UI `8cbec3ef97a13caf626450a0111ee3dc50b262cc`; Integrator/Develop `451b2f39377653b44fb178e58d86705b6026bef8`.
- History-preserving NON-FORCE synchronization: `e8449509f9f6acd8cb63e19d4675eef712ae1077`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving valid ranges. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

## ERR-0016 — fix applied, canonical closure blocked by ERR-0017

Product fix `d721846ea9524ab18336ba72eeb082cca7ee0fb8` retains rejected oversized bytes outside successful `_bytes_read` accounting while introducing explicit `_byte_budget_poisoned` fail-closed state. Regression `44bf215b999e727514fc10ddb88eb8379a5358b6` proves follow-up body access is blocked before delegate I/O.

Exact Backend documentation Quality `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b = failure`, but current Error-worker analysis proves the failure is the independent Personal-Memory import graph defect `ERR-0017`, not a recurrence of the poisoning signature. Keep ERR-0016 `FIXED_PENDING_VERIFY` until a corrected exact descendant can complete canonical verification.

## ERR-0017 coordination — do not duplicate Core ownership

Current Develop imports `ModelInferredMemoryProposal` from `athena.memory.models` but does not define it. Error worker `b8e050c9756299a70e8f5d4df0139ef54a5f08a0` binds this as the root cause for mypy failure, pytest collection abort, API path-boundary failures and local-install smoke failure. Spec/Core owns the compatible verified model contract and has synchronized it on `postmerge/spec-core@96c8f17d99017060238da27b51f6e59b77b9eafc`.

Backend does not duplicate or reinterpret that Core model. Canonical Backend Quality remains expected to stay blocked until Integrator composes the exact-green Core dependency onto Develop.

## New P2 Provider slice — lifecycle-hook runtime boundary

Product commit: `e6c4176261640c6bdfbb11ee299de40896cbe034`.
Focused regression: `72539330ff3f7e9ace511ce9e6be63e2a15ac595`.
Canonical Quality: `34024769901` is pending on the exact focused-test head at handoff time; no PASS claim.

`_BoundedLocalResponse` previously called present `__enter__`, `__exit__`, and fallback `close` attributes without checking callability. Malformed/future response delegates could therefore surface arbitrary `TypeError` from lifecycle handling rather than a deterministic transport-boundary failure, including cleanup paths. The wrapper now validates optional lifecycle hooks as callable before invocation and raises deterministic `OSError` for non-callable hooks. Missing hooks retain the existing behavior; valid callable hooks are unchanged. The focused test covers non-callable enter, exit and close hooks plus the valid lifecycle path, with byte accounting unchanged.

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
- Lifecycle hooks now fail deterministically before invocation when present but non-callable.
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
- ERR-0016 overflow poison fix: `d721846ea9524ab18336ba72eeb082cca7ee0fb8` + `44bf215b999e727514fc10ddb88eb8379a5358b6`; canonical closure blocked by independent ERR-0017 import graph.
- Callable body-delegate boundary remains in the same Backend descendant and still awaits an exact successful descendant.
- Lifecycle-hook callable boundary: `e6c4176261640c6bdfbb11ee299de40896cbe034` + `72539330ff3f7e9ace511ce9e6be63e2a15ac595`; Quality `34024769901` pending at handoff time.

## Next backend slice

First consume the exact Quality result for `72539330ff3f7e9ace511ce9e6be63e2a15ac595` or this documentation descendant. Do not attribute ERR-0017 import-graph failures to Provider code. Once Integrator composes the verified Core proposal-model dependency onto Develop, re-synchronize NON-FORCE and require focused local HTTP poisoning/oversize/delegate/lifecycle regressions plus canonical Quality before closing ERR-0016 or promoting pending Provider slices. If the Core blocker remains unchanged for one run, take a distinct evidence-backed Backend/System slice rather than repeating the same runner state.
