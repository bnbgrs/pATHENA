# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@ff780f2edf367320340771ffc3176d9fc1724c5c`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `02707d295e31e8d321ba6f2ed1bd6f50197eeb81`.
- Required worker heads reviewed before mutation: Error `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`, Spec/Core `0166f4dbc6962fe8fd1f96de2d265d6767b009dc`, UI `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- History-preserving NON-FORCE synchronization: `61d2755651657859cfa2ae78bf8ff232d826c494`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` require true integers and reject bool; `timeout_seconds` accepts finite numeric values only, rejects bool/NaN/Inf, and preserves the existing `(0, 300]` range. No silent Tor-to-Direct fallback, proxy leak, redirect bypass, HTTPS/default-port relaxation, compressed-response acceptance, response-size relaxation, retry addition, audit weakening, provenance weakening, or Source-finalization change was introduced.

Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` remains backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure canonical reserve-release size truth — VERIFIED

Product `ef7dbde6e660d095272e14febcbbd1fc4cfa4370` bounds positive `DiskPressureCheckResult.released_reserve_bytes` by `emergency_reserve_size_bytes(before_release.total_bytes)`. Test `415691b0cac741f461ed41bcecbbe08bd9011330` covers malformed telemetry claiming a 2 GiB release from a 100 GiB volume whose canonical reserve is 1 GiB.

Exact Backend descendant `02707d295e31e8d321ba6f2ed1bd6f50197eeb81` passed canonical ATHENA Quality `33999117392 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local provider HTTP error-body total deadline — APPLIED / PENDING CANONICAL

The shared loopback-only local provider transport already enforced proxy-free routing, redirect rejection, response-byte limits and a monotonic total deadline for successful responses. Its `HTTPError` path wrapped the error body with `_BoundedLocalResponse` but omitted `total_timeout_seconds`, despite the transport contract stating that HTTP error bodies use the same byte and total-time bounds before provider-specific error parsing. A provider could therefore keep an error body alive beyond the request's total deadline while continuing to make progress within the lower-level socket timeout.

Product `eaa0c891d794529708917461b600ebe4584ae2a2` changes `_bound_http_error_body` to require the already validated request timeout and propagates it into `_BoundedLocalResponse`; `open_local_request` passes the exact `validated_timeout`. No retry, proxy, redirect, routing, byte-limit, provider parsing or cryptographic behavior changed.

Test `18710d1441206c8282f7c7dacae15f8116365c17` adds `tests/unit/test_local_http_error_body_timeout.py`, proving that an HTTP error-body read fails with `TimeoutError` once the monotonic total deadline is reached.

No exact workflow run is currently bound to test head `18710d1441206c8282f7c7dacae15f8116365c17`; no PASS/READY claim is made for this slice.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Persistent runtime / crash prevention invariants

- Windows frozen packaging must retain `pypdf` distribution metadata; historical `PackageNotFoundError`/supervisor relaunch must not recur.
- Frozen unknown child argv remains fail-closed; production `pATHENA.exe` Desktop / `pATHENA-Worker.exe` Worker separation remains intact.
- Windows process-tree stability remains a runtime invariant: one Desktop instance and bounded/non-growing Worker population.
- Direct Chat context budgeting must retain adaptive output reserve for small loaded LM Studio contexts while preserving safety/context guards, including the 2048-token regression.
- Preserve the Windows lane-lock/scheduler/startup crash class as release-acceptance coverage: `PermissionError: [Errno 13] Permission denied` in `athena/jobs/lane_lock.py::_lock_nonblocking`, subsequent `SchedulerLaneOwnershipError`, and secondary packaged-worker `OSError: [Errno 22] Invalid argument` require Windows lane-lock/scheduler/startup/process-tree smokes before Beta/Release when a new Windows candidate exists.
- Preserve startup prevention signatures: `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, and `Failed to start service 'storage-bootstrap'`.
- Historical failures reopen only on exact-SHA reproduction; prevention invariants remain binding.

## Invariants retained

- local model transport remains loopback-only, proxy-free and redirect-rejecting;
- successful and HTTP-error response bodies are byte-bounded and total-deadline-bounded;
- no new retries, provider routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size bounds remain unchanged;
- audit, provenance, fsync and transactional Source-finalization semantics remain unchanged;
- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- reserve provisioning and disk-pressure truth contracts remain intact;
- no SQLite/WAL, persistence-format, transaction or recovery-protocol mutation;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Error / collision handoff

- Error worker `0017b4d83481ba46e020d12492eb5c1d0a5fca7a` reports OPEN none and historical `ERR-0014` STALE; Backend does not reopen it without exact recurrence.
- Spec/Core head `0166f4dbc6962fe8fd1f96de2d265d6767b009dc` owns disjoint Core work.
- UI head `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa` owns disjoint UI work.
- Exact Develop UI/Integrator changes were preserved during synchronization.
- No UI/Core-owned file was mutated.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state through `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- READY: Disk-pressure released-volume-bound through `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- READY: Disk-pressure threshold-consistency through `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- READY: Disk-pressure assessment-state truth and reserve-provision free-space-bound through `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`, Quality `33984348331 = success`.
- READY: reserve-provision EMERGENCY-boundary truth through `35a7ca4a31a86aa31cecc2d6140518071f1c7b71`, Quality `33987267648 = success`.
- READY: reserve canonical required-size truth through `876fcd4dcffbcca50ac6cf137b5299343135c0e8`, Quality `33990310049 = success`.
- READY: deterministic safe-allocation result truth through `90084f68bab8b8ec55aefe0edfb30bfa55c23dde`, Quality `33993264724 = success`.
- READY: canonical assessment-threshold truth through `8d07a57809507ada1ae5a87cd1fb6e360b66f74d`, Quality `33996189939 = success`.
- READY: canonical reserve-release-size truth through exact Backend descendant `02707d295e31e8d321ba6f2ed1bd6f50197eeb81`, Quality `33999117392 = success`.
- NOT READY: local provider HTTP error-body total-deadline hardening product `eaa0c891d794529708917461b600ebe4584ae2a2` + test `18710d1441206c8282f7c7dacae15f8116365c17` until executable canonical verification is green.

## Next backend slice

Consume the first exact canonical Quality run containing `18710d1441206c8282f7c7dacae15f8116365c17` or this documentation-only descendant. If green, promote local provider HTTP error-body total-deadline hardening to VERIFIED/READY and immediately take the highest current unclaimed disjoint Storage/Recovery/Provider/Packaging/Runtime P0/P1/P2 gap. If no run binds, use an alternate executable verification path or another real disjoint Backend/System slice instead of repeating runner state. If red, inspect exact diagnostics and repair only a Backend-owned failure while preserving ExternalAccessGateway and persistent Windows release/crash invariants.
