# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@62aa4e9ff20919f32d5147d183521fbf98f49535`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba`.
- Required handoffs/worker heads reviewed: Error `118f3b2c182de43d1876c7c369a00282800018fa`; Spec/Core `93bd90539ce052cf5359d358cc27aec2cb781806`; UI `856d9f56fac059f257451c2e31fd35b4e554e55f`; Integrator baseline `62aa4e9ff20919f32d5147d183521fbf98f49535`.
- History-preserving NON-FORCE synchronization after canonical pytest failure: `aed7296fd0ca173daaca41da1f2f64e575b8c5b4`, parents prior Backend head + exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving the existing range. Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync and transactional Source-finalization invariants remain unchanged.

Exact green lineage: `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local provider HTTP error-body total deadline — VERIFIED

Product `eaa0c891d794529708917461b600ebe4584ae2a2` propagates the already validated request timeout into bounded `HTTPError` bodies. Focused regression `18710d1441206c8282f7c7dacae15f8116365c17` proves the monotonic total deadline also applies before provider-specific error parsing.

Exact Backend descendant `7b37f0629d3a137301ef04284524a8dfd78c36d3` passed canonical ATHENA Quality `34001608473 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local provider bounded-read size type stability — APPLIED / CANONICAL RED ON STALE BASE / RESYNCED

Product `e6ae4998b675d8ed83efc266fd7d73063e1df63c` requires `_BoundedLocalResponse.read(amt)` to receive `None` or a true non-bool integer before deadline/accounting/delegate access. Focused regression `629871ef5a2c1ff1daf03b4ec5520324ddeb94be` covers bool/float/string rejection before delegate access and preserves negative-integer bounded whole-body semantics.

Canonical ATHENA Quality `34004101347` on documentation descendant `e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba` completed `failure`: Windows path safety, Local install smoke, Linux storage regressions, spec validator, Ruff and mypy passed; only canonical pytest failed. That run used Develop base `da493c1390192425d50caddc451c1a497027027a`. Develop subsequently advanced with disjoint Personal Memory exact-scope priority product/test fixes through `62aa4e9ff20919f32d5147d183521fbf98f49535`.

Backend therefore synchronized NON-FORCE/history-preserving to exact current Develop using only complete Backend-owned blobs. Sync commit: `aed7296fd0ca173daaca41da1f2f64e575b8c5b4`. No exact workflow run was bound to that sync commit at handoff-write time; no PASS/READY claim is made for the bounded-read slice.

Status: `BACKEND_APPLIED / CANONICAL_REVERIFY_REQUIRED`.

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

- Error worker head `118f3b2c182de43d1876c7c369a00282800018fa` retains the release crash regression matrix; no exact-SHA Backend crash signature was reopened.
- Spec/Core `93bd90539ce052cf5359d358cc27aec2cb781806` and UI `856d9f56fac059f257451c2e31fd35b4e554e55f` are disjoint from this Provider transport slice.
- Current Develop Personal Memory changes were preserved during synchronization; no foreign product/test file was overwritten.

## Integrator handoff

READY:
- ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- Local-provider HTTP error-body total-deadline hardening through `7b37f0629d3a137301ef04284524a8dfd78c36d3`, Quality `34001608473 = success`.
- All previously recorded green Storage/DiskPressure Backend slices remain READY under their exact green lineages.

NOT READY:
- Local-provider bounded-read size type stability product `e6ae4998b675d8ed83efc266fd7d73063e1df63c` + focused regression `629871ef5a2c1ff1daf03b4ec5520324ddeb94be`; stale-base canonical run `34004101347` failed only pytest, and current-Develop sync `aed7296fd0ca173daaca41da1f2f64e575b8c5b4` requires exact re-verification.

## Next backend slice

Consume the first exact canonical Quality run containing `aed7296fd0ca173daaca41da1f2f64e575b8c5b4` or this documentation-only descendant. If green, promote bounded-read size type stability VERIFIED/READY and immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If red, inspect exact pytest diagnostics and minimally repair only Backend-owned failures; if no executable run binds, use an alternate executable verification route or a different real disjoint slice rather than repeating the same runner state.
