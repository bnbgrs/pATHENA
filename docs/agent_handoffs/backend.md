# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9`.
- Worker pre-run head: `postmerge/backend@bc622dcb0554d2449183afe2331669ab15c7c8ef`.
- Worker heads reviewed at run start: Error `f434f9f714f1453cac5fda8b1aa5b7f8684dedda`; Spec/Core `b62e08cac198fde7ce7c5f081dd577decdcc216d`; UI `6558031bb31e5e35f5c8639bf4f5c8591f7fa250`; Integrator/Develop `86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9`.
- History-preserving NON-FORCE synchronization: `fe00c27430dc535b5ffb2b318c559cd77b4e461e`, parents prior Backend head + exact Develop, with exact Develop tree plus Backend-owned blobs only.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving valid ranges. Exact green lineage remains `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

No Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync or transactional Source-finalization invariant was weakened.

## Current canonical blocker

Exact lifecycle test-head Quality `34024769901@72539330ff3f7e9ace511ce9e6be63e2a15ac595 = failure`. Specification validator and Ruff passed; canonical mypy/pytest and API/local-install paths remained blocked by the independent Personal-Memory import graph defect `ERR-0017`, not by a new Provider diagnostic. Current Develop still imports `ModelInferredMemoryProposal` while `src/athena/memory/models.py` lacks that class.

Error worker now carries a bounded `ERR-0017` correction and keeps both `ERR-0017` and Backend `ERR-0016` at `FIXED_PENDING_VERIFY`. Backend did not duplicate the Core model contract.

## New P2 Provider slice — zero-byte read side-effect boundary

Product commit: `d4c9ccbddb56495de42a5ea53bd1b8da5dd40e9d`.
Focused regression: `52d7920bbdacd6e3e6e576f136476edb23c586cc`.
Exact canonical workflow at handoff: none yet; no PASS claim.

`_BoundedLocalResponse.read(0)` previously validated deadline/budget/delegate and then still invoked the underlying response `read(0)`. A malformed or side-effecting local-provider delegate could therefore perform body-side effects for a zero-byte request even though no bytes are requested. The bounded wrapper now preserves all existing fail-before-use guards and callable validation, but returns `b""` before delegate I/O when `amt == 0`.

Focused regression proves:
- valid `read(0)` returns `b""` with zero delegate calls and unchanged byte accounting;
- poisoned byte-budget state still fails closed before delegate access;
- a missing/non-callable `read` delegate is still rejected, so the callable boundary is not weakened.

## Pending Provider verification

- `ERR-0016` overflow poison fix: `d721846ea9524ab18336ba72eeb082cca7ee0fb8` + `44bf215b999e727514fc10ddb88eb8379a5358b6`, pending canonical closure after ERR-0017 correction is composed.
- Callable body-delegate boundary remains pending exact green.
- Lifecycle-hook callable boundary: `e6c4176261640c6bdfbb11ee299de40896cbe034` + `72539330ff3f7e9ace511ce9e6be63e2a15ac595`; its exact Quality failed on ERR-0017 cascade.
- Zero-byte read side-effect boundary: `d4c9ccbddb56495de42a5ea53bd1b8da5dd40e9d` + `52d7920bbdacd6e3e6e576f136476edb23c586cc`; no exact workflow run yet.

## Previously verified READY lineages

- ExternalAccessGateway runtime boundaries: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- Local-provider HTTP error-body total deadline: `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.
- Bounded-read / ERR-0015 / response-body bytes boundary: `9dc8375399c6b07f9c52545783004607aa9dd430`, Quality `34011613102 = success`.
- Bounded-response constructor limits: `20edbed46471a50e72661e2e69502b094a0b599f`, Quality `34014111747 = success`.
- Previously recorded green Storage/DiskPressure lineages remain READY under their exact green SHAs.

## Persistent runtime / crash prevention invariants

Retain Beta/release acceptance for Windows `pypdf` metadata, fail-closed frozen child argv, `pATHENA.exe` Desktop + `pATHENA-Worker.exe` split, exactly one Desktop with bounded workers, adaptive 2048-context DirectChat reserve, lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`, and startup signatures `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'`. Reopen historical signatures only on exact-current reproduction.

## Invariants retained

Local-provider transport remains loopback-only, proxy-free, redirect-rejecting, byte-bounded and total-deadline-bounded. Non-byte bodies fail closed. Overflow remains permanently poisoned without counting rejected bytes. Alternative read APIs/raw handles stay blocked. No new retries or cryptography. SQLite/WAL, Recovery, Security, audit/provenance/fsync and Source finalization are unchanged. No Skip/XFail, assertion weakening, force push, history rewrite or main mutation.

## Next backend slice

Consume the first exact workflow/canonical run containing `52d7920bbdacd6e3e6e576f136476edb23c586cc` or this documentation descendant. If ERR-0017 remains the sole cascade, do not repeat it unchanged; once Integrator composes the exact-green proposal-model dependency, non-force re-synchronize and run focused local_http poisoning/oversize/delegate/lifecycle/zero-read coverage plus canonical Quality. If the Core blocker is unchanged, take the next disjoint evidence-backed Backend/System P0/P1/P2 slice.
