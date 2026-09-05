# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@c3d72d3d745033f7382f99a3a717dc1f246d727a`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `be13865f8ab863809a7da28a38e5c5df35b3fa29`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff; current worker branches were checked before mutation.
- Worker heads observed: errors `e0d009c4ecc2e0db3000acdb4b0dc726e64005de`; spec-core `2f62d2a26f9341e7ea8c84abe2ae48762bfe117c`; ui `97b051612ca1199907a47d7e3f6938e3f1f8ca37`.
- History-preserving NON-FORCE synchronization: `a209e733fab5192a57cb0f52a6be4ed9596edeba`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` reject bool/non-int values; `timeout_seconds` rejects bool and non-finite values while preserving valid numeric ranges. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve-release state invariant — VERIFIED

Product `79d6382f728fac2ca7bdae2306881327c82042ed` requires positive `released_reserve_bytes` to originate from an EMERGENCY before-state. Focused tests `02e9d210a946e9d782797cc5950902afd38a0781` cover rejection from NORMAL and acceptance of EMERGENCY -> CRITICAL reassessment. Exact Backend head `8be678b5fa3e19aa442e788d935436914a53452b` passed canonical ATHENA Quality `33972009715 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure released-volume bound — VERIFIED

Product/test commit `a6968852a8db404fdb52e5a157c8e6eb6d82a485` rejects physically impossible telemetry where `released_reserve_bytes` exceeds `before_release.total_bytes`. Existing EMERGENCY-only release and zero-release identity rules remain unchanged.

Exact descendant Backend head `be13865f8ab863809a7da28a38e5c5df35b3fa29` passed canonical ATHENA Quality `33974947204 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure threshold consistency — APPLIED / PENDING CANONICAL

A `DiskPressureCheckResult` represents one check against one stable volume size. Because thresholds are a deterministic function of that volume size, accepting different threshold objects before and after a reserve release creates contradictory recovery/audit telemetry even while `total_bytes` is unchanged.

Product commit `c0ee910a20fb396b0c20429f2da33873b407c641` now fails closed when `after_release.thresholds != before_release.thresholds`. Test commit `dde63f019c5ecd95d1805ff9c19fdd986fe4b436` adds focused rejection of a threshold change while preserving the valid EMERGENCY -> CRITICAL release path.

Canonical ATHENA Quality `33978138355` is pending on exact test head `dde63f019c5ecd95d1805ff9c19fdd986fe4b436`; no PASS/READY claim is made yet.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
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

- Current Error handoff has `ERR-0014` IN_PROGRESS for a Qt/Desktop SIGSEGV on the UI worker lineage; the affected DesktopApiController product/test blobs were unchanged from prior green evidence, so Backend does not mutate that foreign owner path.
- No Backend blocker is introduced by ERR-0014; current DiskPressure work is disjoint.
- No UI/Core-owned files were mutated in this Backend run.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state product `79d6382f728fac2ca7bdae2306881327c82042ed` + tests `02e9d210a946e9d782797cc5950902afd38a0781`, exact Backend head `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- READY: Disk-pressure released-volume-bound product/test `a6968852a8db404fdb52e5a157c8e6eb6d82a485`, exact descendant Backend head `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- NOT READY: Disk-pressure threshold-consistency product `c0ee910a20fb396b0c20429f2da33873b407c641` + test `dde63f019c5ecd95d1805ff9c19fdd986fe4b436` until exact canonical evidence is green.

## Next backend slice

Consume exact canonical Quality `33978138355` on `dde63f019c5ecd95d1805ff9c19fdd986fe4b436`. If green, promote threshold consistency to VERIFIED/READY and immediately take the highest unclaimed disjoint Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact diagnostics and repair only a Backend-owned failure. If no executable result is available next run, use an alternate executable verification path or a different real disjoint Backend/System slice rather than repeating the same runner state.