# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@da493c1390192425d50caddc451c1a497027027a`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `7b37f0629d3a137301ef04284524a8dfd78c36d3`.
- Required handoffs reviewed before mutation: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- Relevant worker heads observed in current handoffs: Error `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`; Spec/Core current lineage includes `daf618982b068557919b58a3e0e6935c9cf41afe`; UI current lineage includes `f09406daab9440ee77a06e907add84280b3ae936`.
- History-preserving NON-FORCE synchronization: `1adee89a9a551ee92220fd741640d4d79e1b1ff3`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving the existing range. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local provider HTTP error-body total deadline — VERIFIED

Product `eaa0c891d794529708917461b600ebe4584ae2a2` propagates the already validated request timeout into bounded `HTTPError` bodies. Focused regression `18710d1441206c8282f7c7dacae15f8116365c17` proves the monotonic total deadline also applies before provider-specific error parsing.

Exact Backend descendant `7b37f0629d3a137301ef04284524a8dfd78c36d3` passed canonical ATHENA Quality `34001608473 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local provider bounded-read size type stability — APPLIED / PENDING CANONICAL

The bounded local response accepted Python `bool` as an integer read amount and allowed other invalid runtime values to reach arithmetic/delegate behavior. This was a type-unstable boundary on the shared loopback-only provider transport. Product `e6ae4998b675d8ed83efc266fd7d73063e1df63c` now requires `read(amt)` to receive `None` or a true non-bool integer before deadline/accounting/delegate access. Negative integer semantics remain the existing bounded whole-body behavior.

Focused regression `629871ef5a2c1ff1daf03b4ec5520324ddeb94be` adds `tests/unit/test_local_http_read_size_validation.py`, covering `True`, float and string rejection before the delegate is called, plus retention of valid negative-integer bounded reads.

No exact canonical workflow run is currently bound to `629871ef5a2c1ff1daf03b4ec5520324ddeb94be`; no PASS/READY claim is made.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Persistent runtime / crash prevention invariants

- Frozen Windows packaging retains `pypdf` distribution metadata; historical `PackageNotFoundError`/supervisor relaunch must not recur.
- Unknown frozen child argv remains fail-closed; keep `pATHENA.exe` Desktop / `pATHENA-Worker.exe` Worker separation.
- Windows runtime retains exactly one Desktop process and bounded/non-growing Worker population.
- Direct Chat retains adaptive output reserve for small LM Studio contexts, including the 2048-context regression, without weakening safety/context guards.
- Preserve the Windows lane-lock/scheduler/startup crash cluster as Beta/release acceptance coverage: `PermissionError: [Errno 13] Permission denied` in `_lock_nonblocking`, subsequent `SchedulerLaneOwnershipError`, and packaged-worker `OSError: [Errno 22] Invalid argument`.
- Preserve startup prevention signatures: `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'`.
- Historical signatures reopen only on exact-SHA reproduction; prevention knowledge remains binding.

## Invariants retained

- Local model transport remains loopback-only, proxy-free and redirect-rejecting.
- Successful and HTTP-error response bodies remain byte-bounded and total-deadline-bounded.
- No new retries, provider routing behavior or cryptography.
- No silent Tor -> Direct fallback; Direct remains explicit-only.
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size bounds remain unchanged.
- Audit, provenance, fsync and transactional Source-finalization semantics remain unchanged.
- Emergency reserve / disk-pressure truth contracts remain intact.
- No SQLite/WAL, persistence-format, transaction or recovery-protocol mutation.
- No Skip/XFail, assertion weakening or guard relaxation.
- No merge to `main`, force-push or history rewrite.

## Error / collision handoff

- Error worker reports no current OPEN Backend blocker; historical `ERR-0014` remains stale absent exact recurrence.
- Spec/Core and UI current work are disjoint; no Core/UI-owned product file was mutated.
- Exact Develop changes were preserved during synchronization.
- Local checkout was retried once after the previous DNS class and again failed with `Could not resolve host: github.com`; GitHub-native complete-blob/tree/commit writes were used instead, so DNS did not block progress.

## Integrator handoff

READY:
- ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- StorageHealth ASCII-control-detail through `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- Disk-pressure reserve-release-state through `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- Disk-pressure released-volume-bound through `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- Disk-pressure threshold-consistency through `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- Disk-pressure assessment-state truth / reserve free-space bound through `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`, Quality `33984348331 = success`.
- Reserve-provision EMERGENCY-boundary truth through `35a7ca4a31a86aa31cecc2d6140518071f1c7b71`, Quality `33987267648 = success`.
- Reserve canonical required-size truth through `876fcd4dcffbcca50ac6cf137b5299343135c0e8`, Quality `33990310049 = success`.
- Deterministic safe-allocation truth through `90084f68bab8b8ec55aefe0edfb30bfa55c23dde`, Quality `33993264724 = success`.
- Canonical assessment-threshold truth through `8d07a57809507ada1ae5a87cd1fb6e360b66f74d`, Quality `33996189939 = success`.
- Canonical reserve-release-size truth through `02707d295e31e8d321ba6f2ed1bd6f50197eeb81`, Quality `33999117392 = success`.
- Local-provider HTTP error-body total-deadline hardening through `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.

NOT READY:
- Local-provider bounded-read size type stability product `e6ae4998b675d8ed83efc266fd7d73063e1df63c` + focused regression `629871ef5a2c1ff1daf03b4ec5520324ddeb94be` until exact canonical verification is green.

## Next backend slice

Consume the first exact canonical Quality run containing `629871ef5a2c1ff1daf03b4ec5520324ddeb94be` or its documentation-only descendant. If green, promote bounded-read size type stability to VERIFIED/READY and immediately take the highest current unclaimed disjoint Storage/Recovery/Provider/Packaging/Runtime P0/P1/P2 gap. If no run binds, use another executable verification path or a different real disjoint Backend/System slice rather than repeating runner state. If red, inspect exact diagnostics and minimally repair only Backend-owned failure while preserving ExternalAccessGateway and persistent Windows release/crash invariants.
