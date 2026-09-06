# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@859e1a68e8d9a207a5094462aefe189f6f276c9d`.
- Worker branch: `postmerge/backend`.
- Pre-run worker head: `3d61f4ed646ceda00785928320bfefa12b6fb257`.
- Worker heads reviewed: Error `46fb660d7980d83e1b22c061187bae2b99832610`; Spec/Core `396a66302d0e4e96deb2d69076fdaa340bb395c5`; UI `062440397c9330ac23e9f8b3293d822f2451c902`; Integrator baseline `859e1a68e8d9a207a5094462aefe189f6f276c9d`.
- History-preserving NON-FORCE synchronization to current Develop: `64b8077fa15f870e0fdd5b4a2a5ce5c4e3f887ed`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving the existing range. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local provider HTTP error-body total deadline — VERIFIED

Product `eaa0c891d794529708917461b600ebe4584ae2a2` propagates the already validated request timeout into bounded `HTTPError` bodies. Focused regression `18710d1441206c8282f7c7dacae15f8116365c17` proves the monotonic total deadline also applies before provider-specific error parsing.

Exact Backend descendant `7b37f0629d3a137301ef04284524a8dfd78c36d3` passed canonical ATHENA Quality `34001608473 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local provider bounded-read size type stability — PRODUCT PRESERVED / HARNESS FIX APPLIED

Product `e6ae4998b675d8ed83efc266fd7d73063e1df63c` requires `_BoundedLocalResponse.read(amt)` to receive `None` or a true non-bool integer before deadline/accounting/delegate access. The product `remaining + 1` whole-body probe remains unchanged because it is the overflow-detection mechanism.

Canonical Quality `34006623230@3d61f4ed646ceda00785928320bfefa12b6fb257` reproduced the sole pytest failure while Windows path safety, Local install smoke, Linux storage regressions, specification validator, Ruff and mypy passed. Error handoff `ERR-0015` correctly identified the root cause as the focused test harness: `_TrackingResponse.read(size)` fabricated exactly `size` bytes, so the wrapper's intentional 5-byte probe against a nominal four-byte body created a fake oversized response.

Backend synchronized to current Develop through `64b8077fa15f870e0fdd5b4a2a5ce5c4e3f887ed`, then applied the minimal test-only correction at `5abee1fb3cf9aa639a2600796036302ef63a773d`: `_TrackingResponse` now models a finite remaining-aware byte body. Invalid bool/float/string read sizes still fail before delegate access; a true negative integer now exercises a real finite four-byte whole-body response rather than an infinite byte generator.

Canonical Quality `34009015142` is bound to exact test-fix SHA `5abee1fb3cf9aa639a2600796036302ef63a773d` and is pending at handoff-write time. No PASS or READY claim is made until that exact run succeeds.

Status: `BACKEND_FIXED_PENDING_CANONICAL_VERIFY`.

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

- Error worker `46fb660d7980d83e1b22c061187bae2b99832610` owns `ERR-0015` verification and explicitly required this finite-body harness correction without product-guard weakening.
- Spec/Core `396a66302d0e4e96deb2d69076fdaa340bb395c5` and UI `062440397c9330ac23e9f8b3293d822f2451c902` are disjoint from this Provider test correction.
- Current Develop Personal Memory acceptance additions were preserved during synchronization; no foreign product/test file was overwritten.

## Integrator handoff

READY:
- ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- Local-provider HTTP error-body total-deadline hardening through `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.
- All previously recorded green Storage/DiskPressure Backend slices remain READY under their exact green lineages.

NOT READY:
- Local-provider bounded-read size type stability product `e6ae4998b675d8ed83efc266fd7d73063e1df63c` + harness-fix `5abee1fb3cf9aa639a2600796036302ef63a773d`; exact canonical Quality `34009015142` is pending.

## Next backend slice

Consume exact canonical Quality `34009015142@5abee1fb3cf9aa639a2600796036302ef63a773d`. If green, promote `ERR-0015` bounded-read type stability/harness correction VERIFIED/READY and immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If red, inspect exact pytest diagnostics and minimally repair only Backend-owned failure without weakening the true-int read guard, overflow probe, byte/deadline limits or ExternalAccessGateway/security/runtime invariants. If no executable result becomes available, take a distinct real Backend/System slice rather than repeating runner state.