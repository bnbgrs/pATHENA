# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@b5d888b09774e70a389457f568a8079faf130b5e`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `90084f68bab8b8ec55aefe0edfb30bfa55c23dde`.
- Required worker heads reviewed before mutation: Error `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`, Spec/Core `38d83997e5fb183570f277385dbff85525ab99dc`, UI `5604ee6bdf4783a096bd08cbbf2e08b9fb5ae303`.
- History-preserving NON-FORCE synchronization: `46d96d4333dcce3b4bd01ab18ee1ac8d3e9cc30d`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` require true integers and reject bool; `timeout_seconds` accepts finite numeric values only, rejects bool/NaN/Inf, and preserves the existing `(0, 300]` range. No silent Tor-to-Direct fallback, proxy leak, redirect bypass, HTTPS/default-port relaxation, compressed-response acceptance, response-size relaxation, retry addition, audit weakening, provenance weakening, or Source-finalization change was introduced.

Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` remains backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure deterministic safe-allocation result truth — VERIFIED

Product `e99563a778373ca60ad7f31124a595ca2fb12566` requires externally constructed `EmergencyReserveProvisionResult.provisioned_bytes` to match the controller's deterministic allocation policy: zero under EMERGENCY, otherwise `min(required_bytes, max(0, free_bytes - emergency_free_bytes))`. Test `3b5cbb739bbabe7c7699735b94e57ed62121ee1f` covers an under-provisioned safe allocation.

Exact Backend descendant `90084f68bab8b8ec55aefe0edfb30bfa55c23dde` passed canonical ATHENA Quality `33993264724 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure canonical assessment thresholds — APPLIED / PENDING CANONICAL

`DiskPressureAssessment` previously accepted any monotonic `DiskPressureThresholds` as long as the declared state matched those caller-supplied values. That allowed externally constructed recovery telemetry to redefine WARNING/CRITICAL/EMERGENCY boundaries independently of the canonical Beta policy even though controller-generated assessments always derive thresholds from `total_bytes`.

Product `5121c16a93b53f12f021cc779530fdc7bbc3635e` now derives `disk_pressure_thresholds(total_bytes)` during `DiskPressureAssessment.__post_init__` and fails closed unless the supplied thresholds exactly match the canonical policy before state truth is evaluated.

Test commit `8701d15b795147370f5558f7eb36da31070998c5` adds `test_disk_pressure_assessment_rejects_noncanonical_thresholds`. The pre-existing `DiskPressureCheckResult` threshold-change defense remains intact and is still exercised by intentionally corrupting a valid assessment only inside its regression test, preserving defense-in-depth coverage without weakening the new constructor boundary.

No exact canonical workflow run or commit status is currently bound to `8701d15b795147370f5558f7eb36da31070998c5`, so no PASS/READY claim is made for this new slice.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Persistent runtime / crash prevention invariants

- Windows frozen packaging must retain `pypdf` distribution metadata; the historical `PackageNotFoundError`/supervisor-relaunch failure must not recur.
- Frozen unknown child argv remains fail-closed and must never fall back to Desktop; production `pATHENA.exe` Desktop / `pATHENA-Worker.exe` Worker separation remains intact.
- Windows process-tree stability proven by PR #77 / workflow `33991413008` remains a runtime invariant: one Desktop instance and bounded/non-growing Worker population.
- Direct Chat context budgeting must retain the R5 small-context fix: effective output reserve adapts to loaded LM Studio context while safety/context guards remain enforced; specifically preserve the 2048-token-context regression.
- Preserve the Windows lane-lock/scheduler/startup crash class as release-acceptance coverage: `PermissionError: [Errno 13] Permission denied` in `athena/jobs/lane_lock.py::_lock_nonblocking`, subsequent `SchedulerLaneOwnershipError`, and secondary packaged-worker `OSError: [Errno 22] Invalid argument` must be covered by Windows lane-lock/scheduler/startup/process-tree smokes before Beta/Release when a new Windows candidate exists.
- Preserve startup prevention signatures and their root-cause guards: `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, and `Failed to start service 'storage-bootstrap'`.
- Historical failures reopen only on exact-SHA reproduction; prevention invariants remain binding regardless of current stale/fixed status.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- reserve provisioning remains canonical-size, free-space, EMERGENCY-threshold and deterministic-safe-allocation bounded;
- disk-pressure assessments must use canonical thresholds for their exact volume size;
- read-only safe-mode latching and noncritical-write gating remain unchanged;
- storage telemetry does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source-finalization semantics changed;
- valid Windows/Linux storage behavior remains unchanged;
- local model transport remains loopback-only, proxy-free and redirect-rejecting;
- response-size and total-deadline enforcement remain fail-closed;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy and compressed-response rejection unchanged;
- audit and provenance semantics unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Error / collision handoff

- Error worker `0017b4d83481ba46e020d12492eb5c1d0a5fca7a` remains disjoint; historical `ERR-0014` is not reopened without exact-SHA reproduction.
- Spec/Core head `38d83997e5fb183570f277385dbff85525ab99dc` owns Local+Web candidate-freeze work and remains disjoint.
- UI head `5604ee6bdf4783a096bd08cbbf2e08b9fb5ae303` remains disjoint.
- Current Develop UI send-focus changes were preserved from exact Develop during synchronization; Backend did not overwrite them.
- No UI/Core-owned file was mutated.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state through `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- READY: Disk-pressure released-volume-bound through `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- READY: Disk-pressure threshold-consistency through `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- READY: Disk-pressure assessment-state truth and reserve-provision free-space-bound through exact Backend descendant `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`, Quality `33984348331 = success`.
- READY: reserve-provision EMERGENCY-boundary truth through exact Backend descendant `35a7ca4a31a86aa31cecc2d6140518071f1c7b71`, Quality `33987267648 = success`.
- READY: reserve canonical required-size truth through exact Backend descendant `876fcd4dcffbcca50ac6cf137b5299343135c0e8`, Quality `33990310049 = success`.
- READY: deterministic safe-allocation result truth through exact Backend descendant `90084f68bab8b8ec55aefe0edfb30bfa55c23dde`, Quality `33993264724 = success`.
- NOT READY: canonical assessment-threshold truth product `5121c16a93b53f12f021cc779530fdc7bbc3635e` + test `8701d15b795147370f5558f7eb36da31070998c5` until executable canonical verification is green.

## Next backend slice

Consume the first exact canonical Quality run containing `8701d15b795147370f5558f7eb36da31070998c5` or its documentation-only descendant. If green, promote canonical assessment-threshold truth to VERIFIED/READY and immediately take the highest current unclaimed disjoint Storage/Recovery/Provider/Packaging/Runtime P0/P1/P2 gap. If no run binds, use an alternate executable verification path or another real disjoint Backend/System slice instead of repeating runner state. If red, inspect exact diagnostics and repair only a Backend-owned failure while preserving the persistent packaging/process-tree/Direct-Chat/lane-lock/startup invariants above.
