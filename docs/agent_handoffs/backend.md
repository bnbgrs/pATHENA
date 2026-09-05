# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@4ce70615cffcbf0e76ec404e7e58b34c7c5e308a`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `1cc0017d560a1534de1fc2c83989d26e05238236`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff; current worker branches were checked before mutation.
- History-preserving NON-FORCE synchronization: `aab9bd93a71e9055aab2b2ee73fac9643fd1581b`, with parents prior Backend head `1cc0017d560a1534de1fc2c83989d26e05238236` and exact Develop `4ce70615cffcbf0e76ec404e7e58b34c7c5e308a`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health ASCII-control detail invariant — VERIFIED

Product `09893113ec42337db2c590bac99263db393f75e4` rejects embedded C0/DEL controls in `StorageHealthSnapshot.detail`; focused tests `454ae52cae8baeaec82a787dabb588e8ecf2ff6a` cover TAB, backspace, vertical-tab, form-feed and DEL. Exact Backend head `1cc0017d560a1534de1fc2c83989d26e05238236` passed canonical ATHENA Quality `33966299076 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve-release state invariant — PRODUCT_FIXED / TESTS_ADDED_PENDING_VERIFY

`DiskPressureCheckResult` previously accepted a positive `released_reserve_bytes` value when `before_release.state` was NORMAL/WARNING/CRITICAL, contradicting the controller and Beta contract that the emergency reserve may be released only from EMERGENCY.

Product commit `79d6382f728fac2ca7bdae2306881327c82042ed` now fails closed when a positive release is paired with a non-EMERGENCY before-state. Existing controller behavior is unchanged because `DiskPressureController.check()` already calls `reserve_store.release()` only after an EMERGENCY assessment.

Focused test commit `02e9d210a946e9d782797cc5950902afd38a0781` adds `tests/unit/test_disk_pressure_result_boundaries.py`, covering rejection of a positive release from NORMAL and acceptance of a positive release from EMERGENCY into a reassessed CRITICAL state.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing descendant canonical Quality run is green.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- read-only safe-mode latching and noncritical-write gating remain unchanged;
- storage telemetry remains read-only and does not mutate SQLite/WAL state;
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

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail product `09893113ec42337db2c590bac99263db393f75e4` + tests `454ae52cae8baeaec82a787dabb588e8ecf2ff6a` through exact green Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- NOT READY: Disk-pressure reserve-release-state product `79d6382f728fac2ca7bdae2306881327c82042ed` + tests `02e9d210a946e9d782797cc5950902afd38a0781` until exact descendant canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `02e9d210a946e9d782797cc5950902afd38a0781` or a documentation-only descendant. If green, mark DiskPressure reserve-release-state hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If no run binds, use an alternate executable verification path or take a disjoint real Backend/System slice rather than repeating the runner blocker. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
