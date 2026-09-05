# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@415debaae20fd84cd12fa0613dc063dc48dd134f`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`.
- Required worker heads reviewed before mutation: Error `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`, Spec/Core `eaa43526398c2e5abb6efb2ec2ae58c53178e878`, UI `38793f4e116900d4d06db0aff9a8e42c69272141`.
- History-preserving NON-FORCE synchronization: `09fc228f8afa50624b9379c38c2088b408dd4ee5`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` reject bool/non-int values; `timeout_seconds` rejects bool and non-finite values while preserving valid numeric ranges. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure assessment-state truth boundary — VERIFIED

Product `deb69f03a5aa40e655e83bea1f69d6aeaa2b2af8` derives the expected state from supplied free-space/threshold values and rejects contradictory externally constructed `DiskPressureAssessment` telemetry. Test `918c742e86c0567260f2fbc588efd8febd2114ea` covers the contradiction.

A later exact Backend descendant containing this product/test lineage, `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`, passed canonical ATHENA Quality `33984348331 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve provisioning free-space boundary — VERIFIED

Product `f4bc4057880eeeafb621eea9fcc93ba597f7ec37` rejects `provisioned_bytes > assessment.free_bytes`. Focused test `11113d8f3f649089b5ba24ba504b6a7595ea98ec` covers the impossible telemetry state.

Exact Backend descendant `94c6e37d2d6b1d1993703dbaef351fffbc734f6d` passed canonical ATHENA Quality `33984348331 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve provisioning emergency-boundary truth — APPLIED / PENDING CANONICAL

`EmergencyReserveProvisionResult` previously allowed an externally constructed result whose `provisioned_bytes` remained below `assessment.free_bytes` but would itself push projected free space below the strict EMERGENCY threshold. That contradicts `ensure_reserve_if_safe()` and could make recovery telemetry claim a safe reserve allocation that the controller is forbidden to perform.

Product `92c3636726249c42de50a60a9e339f463b717009` now derives the maximum safe allocation as `max(0, free_bytes - emergency_free_bytes)` and rejects larger provisioned values before status acceptance. Focused test `4922b8597b9d454a494d9abcd16acd29d9cd3281` covers a CRITICAL assessment with 3 GiB free / 2 GiB emergency threshold and rejects a 2 GiB provision that would leave 1 GiB.

No exact workflow run is currently bound to the test head, therefore no PASS or READY claim is made.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- reserve provisioning remains bounded by required bytes, assessed free bytes and the strict EMERGENCY threshold;
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

- Error worker `0017b4d83481ba46e020d12492eb5c1d0a5fca7a` marks prior foreign `ERR-0014` stale after repeated exact clean evidence.
- Spec/Core Local+Web Research work and UI focus/accessibility work remain disjoint from this Storage slice.
- No UI/Core-owned files were mutated.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state through `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- READY: Disk-pressure released-volume-bound through `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- READY: Disk-pressure threshold-consistency through `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- READY: Disk-pressure assessment-state truth and reserve-provision free-space-bound through exact Backend descendant `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`, Quality `33984348331 = success`.
- NOT READY: reserve-provision EMERGENCY-boundary truth product `92c3636726249c42de50a60a9e339f463b717009` + test `4922b8597b9d454a494d9abcd16acd29d9cd3281` until executable verification is green.

## Next backend slice

Consume the first exact canonical Quality run containing `4922b8597b9d454a494d9abcd16acd29d9cd3281` or its documentation-only descendant. If green, promote reserve-provision EMERGENCY-boundary truth to VERIFIED/READY and immediately take the highest current unclaimed disjoint Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or another real disjoint Backend/System slice instead of repeating runner state. If red, inspect exact diagnostics and repair only a Backend-owned failure.
