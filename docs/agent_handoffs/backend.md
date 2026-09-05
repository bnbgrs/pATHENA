# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@e25c483909881221aa1b42b868ce22993ec0f9b9`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `876fcd4dcffbcca50ac6cf137b5299343135c0e8`.
- Required worker heads reviewed before mutation: Error `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`, Spec/Core `372697dbbb356ac0bbedfbd4d27f917c38fcefac`, UI `5a5ba2681412c32c181e63026ce1b92574675d64`.
- History-preserving NON-FORCE synchronization: `6fe651057d68afedf0b4f3d4cf125800957eeedf`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` require true integers and reject bool; `timeout_seconds` accepts finite numeric values only, rejects bool/NaN/Inf, and preserves the existing `(0, 300]` range. No silent Tor-to-Direct fallback, proxy leak, redirect bypass, HTTPS/default-port relaxation, compressed-response acceptance, response-size relaxation, retry addition, audit weakening, provenance weakening, or Source-finalization change was introduced.

Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` remains backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve canonical required-size truth — VERIFIED

Product `b480c501e76ad5063acd8fcc3bc755c4fd1934d5` requires `EmergencyReserveProvisionResult.required_bytes` to match `emergency_reserve_size_bytes(assessment.total_bytes)`. Test `c0234dc9f142dff0fa557fe52941e6064b7bd054` covers noncanonical reserve sizing and retains the prior free-space/emergency-boundary regressions.

Exact Backend descendant `876fcd4dcffbcca50ac6cf137b5299343135c0e8` passed canonical ATHENA Quality `33990310049 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure deterministic safe-allocation result truth — APPLIED / PENDING CANONICAL

`DiskPressureController.ensure_reserve_if_safe()` deterministically computes the safe reserve allocation as zero under EMERGENCY, otherwise `min(required_bytes, max(0, free_bytes - emergency_free_bytes))`. `EmergencyReserveProvisionResult`, however, previously allowed externally constructed result telemetry to report a smaller non-negative `provisioned_bytes` value (including zero) even when the assessed volume safely required a larger deterministic allocation. Such telemetry could therefore disagree with the controller/recovery policy while satisfying the previous upper-bound checks.

Product `e99563a778373ca60ad7f31124a595ca2fb12566` now derives the same expected allocation in `EmergencyReserveProvisionResult.__post_init__` and fails closed when `provisioned_bytes` differs. Existing required-size, free-space, EMERGENCY-threshold and status checks remain in place.

Test commit `3b5cbb739bbabe7c7699735b94e57ed62121ee1f` adds `test_reserve_provision_result_rejects_underprovisioned_safe_allocation`, proving that a NORMAL 100 GiB assessment with 20 GiB free cannot truthfully report zero provisioning when the canonical target is 1 GiB and the full target is safe.

No exact canonical workflow run was bound to the test head when this handoff was written, so no PASS/READY claim is made for this new slice.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Persistent runtime / crash prevention invariants

- Windows frozen packaging must retain `pypdf` distribution metadata; the historical `PackageNotFoundError`/supervisor-relaunch failure must not recur.
- Frozen unknown child argv remains fail-closed and must never fall back to Desktop; production `pATHENA.exe` Desktop / `pATHENA-Worker.exe` Worker separation remains intact.
- Windows process-tree stability proven by PR #77 / workflow `33991413008` remains a runtime invariant: one Desktop instance and bounded/non-growing Worker population.
- Direct Chat context budgeting must retain the R5 fix for loaded 2048-token contexts: effective output reserve is adapted to loaded context while safety/context guards remain enforced. Do not restore the pre-provider-call failure caused by fixed `output_reserve=2048` plus `safety_margin=256` at `loaded_context_length=2048`.
- Preserve startup prevention signatures and their root-cause guards: `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, and `Failed to start service 'storage-bootstrap'`.
- Historical failures reopen only on exact-SHA reproduction; prevention invariants remain binding regardless of current stale/fixed status.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- reserve provisioning remains canonical-size, free-space, EMERGENCY-threshold and deterministic-safe-allocation bounded;
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

- Error worker `0017b4d83481ba46e020d12492eb5c1d0a5fca7a` reports no OPEN/IN_PROGRESS/BLOCKED defect; historical `ERR-0014` remains STALE.
- Spec/Core head `372697dbbb356ac0bbedfbd4d27f917c38fcefac` owns Local+Web candidate-freeze work and remains disjoint.
- UI head `5a5ba2681412c32c181e63026ce1b92574675d64` remains disjoint.
- Current Develop Local+Web changes, including `src/athena/external/gateway.py`, were preserved from exact Develop during synchronization; Backend did not overwrite them.
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
- NOT READY: deterministic safe-allocation result truth product `e99563a778373ca60ad7f31124a595ca2fb12566` + test `3b5cbb739bbabe7c7699735b94e57ed62121ee1f` until executable canonical verification is green.

## Next backend slice

Consume the first exact canonical Quality run containing `3b5cbb739bbabe7c7699735b94e57ed62121ee1f` or its documentation-only descendant. If green, promote deterministic safe-allocation result truth to VERIFIED/READY and immediately take the highest current unclaimed disjoint Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or another real disjoint Backend/System slice instead of repeating runner state. If red, inspect exact diagnostics and repair only a Backend-owned failure while preserving the persistent packaging/process-tree/Direct-Chat/startup invariants above.
