# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@49e51f29f3e3c1864a5e26a514b5c07e37c1f28f`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `4c9855df8e662e47a66cb2dcb9f66704c4d8f780`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff; current worker branches were checked before mutation.
- History-preserving NON-FORCE synchronization: `d15f14166dffa8030b366a3b155b4609d69e8adb`, with parents prior Backend head `4c9855df8e662e47a66cb2dcb9f66704c4d8f780` and exact Develop `49e51f29f3e3c1864a5e26a514b5c07e37c1f28f`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage remain present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage health ASCII-control detail invariant — VERIFIED

Product `09893113ec42337db2c590bac99263db393f75e4` rejects embedded C0/DEL controls in `StorageHealthSnapshot.detail`; focused tests `454ae52cae8baeaec82a787dabb588e8ecf2ff6a` cover TAB, backspace, vertical-tab, form-feed and DEL. Exact Backend head `1cc0017d560a1534de1fc2c83989d26e05238236` passed canonical ATHENA Quality `33966299076 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure reserve-release state invariant — FOCUSED VERIFIED / CANONICAL BLOCKED BY FOREIGN UI

`DiskPressureCheckResult` previously accepted a positive `released_reserve_bytes` value when `before_release.state` was NORMAL/WARNING/CRITICAL, contradicting the controller and Beta contract that the emergency reserve may be released only from EMERGENCY.

Product commit `79d6382f728fac2ca7bdae2306881327c82042ed` fails closed when a positive release is paired with a non-EMERGENCY before-state. Focused test commit `02e9d210a946e9d782797cc5950902afd38a0781` adds `tests/unit/test_disk_pressure_result_boundaries.py`, covering rejection from NORMAL and acceptance of EMERGENCY -> CRITICAL reassessment.

Exact canonical run `33969048339@4c9855df8e662e47a66cb2dcb9f66704c4d8f780` executed the full pytest suite. The new file `tests/unit/test_disk_pressure_result_boundaries.py` ran both cases successfully (`..`). Repository pytest finished `4657 passed, 3 skipped, 1 failed`; the sole failure was unrelated UI/PALLAS test `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`, caused by `MessageActionQuietController` lacking `document` inside its Qt event filter. Windows path safety, Linux storage regressions and local install smoke were successful; specification validator, Ruff and mypy were also successful.

No Backend assertion, skip/XFail, guard or invariant was weakened to hide the foreign UI failure. Because the canonical workflow conclusion is `failure`, repository-wide PASS and canonical READY are not claimed for this slice.

Status: `BACKEND_FOCUSED_VERIFIED / CANONICAL_FOREIGN_UI_FAILURE / NOT_CANONICAL_READY`.

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

## Error / collision handoff

- Backend-owned DiskPressure tests are green in the exact full pytest execution above.
- The canonical blocker is UI-owned: `src/athena/desktop/pathena_message_action_quiet_7000.py:41` accesses `self.document` from `eventFilter()` before that attribute is available for the failing PALLAS full-view lifecycle path.
- Backend does not mutate or work around that UI code.
- Current Error handoff observed before mutation reported no OPEN/BLOCKED signatures while Backend Quality was still in progress; this exact completed failure should be consumed by Error/UI ownership on their next scan.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail product `09893113ec42337db2c590bac99263db393f75e4` + tests `454ae52cae8baeaec82a787dabb588e8ecf2ff6a` through exact green Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- NOT CANONICAL READY: Disk-pressure reserve-release-state product `79d6382f728fac2ca7bdae2306881327c82042ed` + tests `02e9d210a946e9d782797cc5950902afd38a0781`; both focused cases passed in exact canonical run `33969048339`, but that run is globally red solely on the foreign UI/PALLAS failure described above.

## Next backend slice

Consume the first exact descendant canonical Quality after the UI/PALLAS lifecycle defect is corrected. If green, mark DiskPressure reserve-release-state hardening canonical VERIFIED/READY. If the foreign UI failure persists, do not change UI from Backend and do not repeat the same blocker; take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap with focused executable verification while preserving the exact DiskPressure evidence recorded here.
