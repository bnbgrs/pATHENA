# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@f630b27ddb7a40f2982f50f79d9f7d9f1322d1b1`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `fea46376a3b3e642d394db4884501310cce155b8`.
- Required handoffs and worker heads were reviewed before mutation. Current observed Error worker carries recurrent foreign `ERR-0014`; Spec/Core is preparing Local+Web Research work; UI remains disjoint from this Storage slice.
- History-preserving NON-FORCE synchronization: `bef428430bc2147933e8b1ec57554cb0f2fa19ab`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` reject bool/non-int values; `timeout_seconds` rejects bool and non-finite values while preserving valid numeric ranges. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure assessment-state truth boundary — APPLIED / CANONICAL NOT GREEN

Product `deb69f03a5aa40e655e83bea1f69d6aeaa2b2af8` derives the expected state from supplied free-space/threshold values and rejects contradictory externally constructed `DiskPressureAssessment` telemetry. Test `918c742e86c0567260f2fbc588efd8febd2114ea` covers the contradiction.

Exact canonical Quality `33981243793` completed `cancelled`, therefore no PASS or READY claim is made for this slice.

Status: `BACKEND_APPLIED / CANONICAL_NOT_GREEN`.

## Disk-pressure reserve provisioning free-space boundary — APPLIED / PENDING CANONICAL

A malformed externally constructed `EmergencyReserveProvisionResult` could report more physically provisioned reserve bytes than the assessment reported as free on the volume. Controller-generated results never require this state, but the result contract did not fail closed.

Product `f4bc4057880eeeafb621eea9fcc93ba597f7ec37` now rejects `provisioned_bytes > assessment.free_bytes` before accepting reserve status semantics. Test `11113d8f3f649089b5ba24ba504b6a7595ea98ec` adds focused coverage for this impossible telemetry state.

No exact workflow run is currently associated with the test head, so no focused or canonical PASS is claimed.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- reserve provisioning remains bounded by existing required-byte and EMERGENCY safety rules;
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

- `ERR-0014` remains foreign Qt/Desktop lifecycle ownership; Backend did not mutate that path.
- Spec/Core Local+Web Research work and UI focus/accessibility work are disjoint from this Storage slice.
- No UI/Core-owned files were mutated.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state through `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- READY: Disk-pressure released-volume-bound through `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- READY: Disk-pressure threshold-consistency product `c0ee910a20fb396b0c20429f2da33873b407c641` + test `dde63f019c5ecd95d1805ff9c19fdd986fe4b436`, exact green descendant `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- NOT READY: Disk-pressure assessment-state truth product `deb69f03a5aa40e655e83bea1f69d6aeaa2b2af8` + test `918c742e86c0567260f2fbc588efd8febd2114ea`; exact Quality `33981243793 = cancelled`.
- NOT READY: reserve-provision free-space boundary product `f4bc4057880eeeafb621eea9fcc93ba597f7ec37` + focused test `11113d8f3f649089b5ba24ba504b6a7595ea98ec` until executable verification is green.

## Next backend slice

Consume the first exact canonical Quality run containing `11113d8f3f649089b5ba24ba504b6a7595ea98ec` or its documentation-only descendant. If green, promote reserve-provision free-space truth to VERIFIED/READY and then re-evaluate the older assessment-state slice on the same green descendant. If no run binds, use an alternate executable verification path or a different real disjoint Storage/Recovery/Provider/Packaging slice rather than repeating the runner state. If red, inspect exact diagnostics and repair only a Backend-owned failure.
