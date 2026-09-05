# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@d14aca9504021bdacadb89dc478ca41545ab4316`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `35a7ca4a31a86aa31cecc2d6140518071f1c7b71`.
- Required worker heads reviewed before mutation: Error `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`, Spec/Core `bab57ac560c3d0fd43f2beb7501b3d4160a09064`, UI `779b28a0845e80bb16feadca28f5eaba26124db9`.
- History-preserving NON-FORCE synchronization: `ce344d0023409adfa186b1cf53346fe4c447b7de`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` reject bool/non-int values; `timeout_seconds` rejects bool and non-finite values while preserving valid numeric ranges. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve provisioning emergency-boundary truth — VERIFIED

Product `92c3636726249c42de50a60a9e339f463b717009` derives the maximum safe allocation as `max(0, free_bytes - emergency_free_bytes)` and rejects larger provisioned values before status acceptance. Focused test `4922b8597b9d454a494d9abcd16acd29d9cd3281` covers a CRITICAL assessment whose proposed reserve write would create EMERGENCY pressure.

Exact Backend descendant `35a7ca4a31a86aa31cecc2d6140518071f1c7b71` passed canonical ATHENA Quality `33987267648 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve canonical required-size truth — APPLIED / PENDING CANONICAL

`EmergencyReserveProvisionResult` could previously be constructed with a positive but noncanonical `required_bytes` value even though runtime provisioning always derives the target from `emergency_reserve_size_bytes(assessment.total_bytes)`. That allowed durable/recovery-facing result telemetry to disagree with the canonical reserve sizing policy while still passing the other free-space and status checks.

Product `b480c501e76ad5063acd8fcc3bc755c4fd1934d5` now derives the canonical target from the assessed volume and fails closed if `required_bytes` differs. Test commit `c0234dc9f142dff0fa557fe52941e6064b7bd054` adds a direct noncanonical-size rejection and updates the free-space/emergency-boundary cases to use the actual 1 GiB canonical target for a 100 GiB volume.

No exact workflow run is currently bound to the test head, therefore no PASS or READY claim is made.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- reserve provisioning remains bounded by canonical target size, assessed free bytes and the strict EMERGENCY threshold;
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
- Spec/Core head `bab57ac560c3d0fd43f2beb7501b3d4160a09064` owns Local+Web Research candidate-freeze work and remains disjoint.
- UI head `779b28a0845e80bb16feadca28f5eaba26124db9` remains disjoint.
- No UI/Core-owned files were mutated.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state through `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- READY: Disk-pressure released-volume-bound through `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- READY: Disk-pressure threshold-consistency through `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- READY: Disk-pressure assessment-state truth and reserve-provision free-space-bound through exact Backend descendant `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`, Quality `33984348331 = success`.
- READY: reserve-provision EMERGENCY-boundary truth through exact Backend descendant `35a7ca4a31a86aa31cecc2d6140518071f1c7b71`, Quality `33987267648 = success`.
- NOT READY: reserve canonical required-size truth product `b480c501e76ad5063acd8fcc3bc755c4fd1934d5` + test `c0234dc9f142dff0fa557fe52941e6064b7bd054` until executable verification is green.

## Next backend slice

Consume the first exact canonical Quality run containing `c0234dc9f142dff0fa557fe52941e6064b7bd054` or its documentation-only descendant. If green, promote reserve canonical required-size truth to VERIFIED/READY and immediately take the highest current unclaimed disjoint Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or another real disjoint Backend/System slice instead of repeating runner state. If red, inspect exact diagnostics and repair only a Backend-owned failure.
