# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened.
- Cascades are deduplicated under the primary root cause.
- `FIXED` requires observed verification; unverified corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- Product defects are fixed in product code; harness defects are fixed in the harness.
- No Skip/XFail, dummy success path, weakened assertions, Ruff/mypy/Validator relaxation, or Security/Storage/Recovery/Windows guard weakening.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline branch: `develop/pathena-next`.
- Baseline SHA observed this run: `8236500a5ae0ae58e7dce5bb3cf0771eb534670d`.
- Worker branch: `postmerge/errors`.
- Pre-run Error branch head: `90904477f4810d0580ca42f4be3b9290b703c1a4`.
- Relevant Backend head: `a5904fc2078a8dec5eece17dd352436d14453d8f`; canonical Quality `34019237735` is in progress with Windows path safety, Linux storage, local install smoke, Validator, Ruff and mypy green while full pytest runs.
- Relevant UI head: `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4`; canonical Quality `34019891561` is in progress with Windows path safety, Linux storage, local install smoke, Validator, Ruff and mypy green while full pytest runs.
- Previous Backend Quality `34016515174@c991482a9f49dec50e69779f73e3a0939df5c73b` completed failure with two exact pytest failures in local HTTP overflow-poisoning coverage; this is `ERR-0016`.
- Previous UI Quality `34017125454@bf7fadf849140697dc63c92c6a5c6c69335e3278` completed success.
- No force update, rebase, history rewrite or merge to `main` was attempted.

## Current error state

- OPEN: `ERR-0016`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- root_cause: bool-safe runtime validation was missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`, `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: canonical Backend boundary evidence green.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0003 — Stale permanent-inspector harness contract
- severity: P1
- status: `FIXED`
- evidence: Backend `33755878184`; UI `33745885426` green on affected blobs.
- root_cause: test contract lagged contextual `Evidence & Activity` behavior.
- files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py`.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- severity: P2
- status: `FIXED`
- evidence: `33785726577` exact B010 diagnostic; `33792012599` I001; exact-head `33804193396 = success`.
- root_cause: bounded startup/readiness test-harness lint defects, not product startup failure.
- files: `tests/unit/test_pathena_startup_experience_2900.py` and related startup harness imports.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification: exact canonical Quality `33804193396 = success`; newer UI Quality `33972487131 = success`.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2
- status: `FIXED`
- evidence: UI `33822842314` mypy failure; corrected `33822861477 = success`.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- severity: P2
- status: `FIXED`
- evidence: Backend `33833499697`; repaired-lineage `33838658964 = success`.
- root_cause: missing explicit runtime container/element validation.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- severity: P1
- status: `FIXED`
- evidence: post-integration `33838377083`; repaired-lineage `33838658964 = success`.
- root_cause: Core integration omitted required contradiction-review dependency file.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- severity: P2
- status: `FIXED`
- evidence: `33845743958`, `33849890354`; exact fix Quality `33854660676 = success`.
- root_cause: harness contract drift after truthful loopback-only behavior changes.
- files: `tests/unit/test_pathena_settings_runtime.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.

### ERR-0009 — Local HTTP remaining-budget hardening leaves stale readline-size harness expectations
- severity: P2
- status: `FIXED`
- evidence: failing Quality `33900689788`; exact Backend Quality `33911612711 = success`.
- root_cause: correct product `remaining + 1` hardening left stale harness expectations.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.

### ERR-0010 — Direct total-deadline hardening invalidates stream timing harness
- first_seen: 2026-09-04
- severity: P2
- status: `FIXED`
- evidence: Backend `33916312429`; recurrent `33933291735` and UI `33936799048`; corrected Backend `33936396203 = success`, UI `33937005854 = success`.
- root_cause: obsolete timing fixture was reintroduced while product fail-closed deadline behavior was correct.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Backend `e62fcc2db49815e7d32579d0dc68a143f8af07b0`.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- severity: P2
- status: `FIXED`
- evidence: failing UI `33922277491`; exact fix-head UI Quality `33926653411 = success`.
- root_cause: provider/detail metadata reused snapshot freshness while provider was unavailable.
- files: `src/athena/desktop/pathena_settings_runtime.py`, `tests/unit/test_pathena_settings_provider_detail_state.py`.
- fix_sha: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.

### ERR-0012 — UI synchronization drops unavailable StorageHealth database-path invariant
- first_seen: 2026-09-05
- severity: P1
- status: `FIXED`
- evidence: failing UI `33961422115@9f24999c62b309e25ac512a110ef18011225a4cc`; corrected `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050 = success`.
- root_cause: UI synchronization retained stale `src/athena/storage/health.py`.
- files: `src/athena/storage/health.py`, `tests/unit/test_storage_health.py`.
- fix_sha: correction present by `cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5`, verified on `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0013 — UI provider-detail whitespace harness Ruff I001
- first_seen: 2026-09-05
- severity: P2
- status: `FIXED`
- evidence: failing UI `33964058090@cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5`; corrected `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050 = success`.
- root_cause: redundant whitespace harness had a non-canonical import block.
- files: `tests/unit/test_pathena_settings_provider_detail_whitespace.py`.
- fix_sha: `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0014 — Qt Desktop controller test process SIGSEGV
- first_seen: 2026-09-05
- severity: P1
- status: `STALE`
- evidence: canonical UI `33975657049@97b051612ca1199907a47d7e3f6938e3f1f8ca37` and `33978563758@8adcc65f394c556b2783b5da070a52c9afc27d0d` exited `139` at `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`; later exact successors `33978582156@fb98e47fde410137b971a303678d4e63f66e1d6d = success` and `33981877292@074c7b9a4ccf9271a91dd1e56784601f749ac020 = success` did not reproduce it.
- root_cause: nondeterministic Qt/Desktop lifecycle signal around real `QThreadPool`, queued delivery and QObject/QApplication teardown; deterministic product defect unestablished.
- files: `tests/unit/test_desktop_api_controller.py`; diagnostic product reference `src/athena/desktop/api_controller.py`.
- fix_sha: none.
- verification: repeated exact clean evidence supports `STALE`, not `FIXED`.

### ERR-0015 — Negative bounded local-response read harness fabricates overflow byte
- first_seen: 2026-09-06
- severity: P2
- area: Backend / Provider-Transport / local HTTP test harness
- status: `FIXED`
- evidence: canonical Backend Quality `34004101347@e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba` failed only `tests/unit/test_local_http_read_size_validation.py::test_bounded_local_response_still_accepts_negative_integer_read_size`; resync `34006604490@aed7296fd0ca173daaca41da1f2f64e575b8c5b4` reproduced the same sole failure with `1 failed, 4666 passed, 3 skipped`.
- repro: `_TrackingResponse.read(amt)` fabricated exactly the requested byte count, so the intentional `remaining + 1` overflow probe created an artificial fifth byte for a four-byte body.
- root_cause: harness defect. The fake response was unbounded; the product overflow probe was correct.
- files: `tests/unit/test_local_http_read_size_validation.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Backend `5abee1fb3cf9aa639a2600796036302ef63a773d`; verified descendant `a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`.
- fix: harness response made finite/remaining-aware; product `remaining + 1` overflow detection, byte accounting, type validation and deadline guards remain unchanged.
- verification: exact canonical Quality `34009044381@a9a267ec790ea4dd1c9cfc79d07fc1665f664e30 = success`; Windows path safety, Linux storage, local install smoke, Validator, Ruff, mypy and full pytest all completed successfully.
- risk: do not weaken the product overflow probe; reopen only on exact recurrence.
- integrator_handoff: bounded-read harness defect is closed and the verified descendant is acceptable evidence for this error.

### ERR-0016 — Local HTTP overflow no longer poisons the bounded response
- first_seen: 2026-09-06
- severity: P1
- area: Backend / Provider-Transport / local HTTP product safety
- status: `OPEN`
- evidence: canonical Backend Quality `34016515174@c991482a9f49dec50e69779f73e3a0939df5c73b`; Windows path safety PASS, Linux storage PASS, local install smoke PASS, Validator PASS, Ruff PASS, mypy PASS, full pytest FAIL with exactly two failures: `tests/unit/test_local_http_response_boundaries.py::test_size_overflow_poisoning_blocks_followup_read_before_underlying_io` and `tests/unit/test_local_http_response_boundaries.py::test_readline_overflow_poisoning_blocks_followup_io`; total `2 failed, 4690 passed, 3 skipped`.
- repro: first oversized `read(6)`/`readline()` correctly raises `LocalResponseTooLargeError`, but a subsequent bounded body access is allowed to perform underlying I/O instead of failing immediately.
- root_cause: product regression introduced by the oversize-before-accounting mutation (`5e6862fe9544465e3aed66840601a204d4d2cae5` lineage). It computes `next_bytes_read`, raises on overflow, and deliberately leaves `_bytes_read` unmodified. That removes the established poisoned-state marker (`_bytes_read > _max_bytes`) used by `_assert_within_byte_budget()` to block all follow-up body I/O after an overflow. The new harness requirement `_bytes_read == 0` after rejection conflicts with the older fail-closed poisoning invariant and weakens post-overflow containment.
- files: `src/athena/model/adapters/local_http.py`, `tests/unit/test_local_http_response_boundaries.py`, `tests/unit/test_local_http_oversize_accounting.py`.
- current_worker_verification: current Backend `a5904fc2078a8dec5eece17dd352436d14453d8f` still contains the non-poisoning `next_bytes_read` implementation; therefore the root cause is still present. Canonical Quality `34019237735` is in progress and is not fix evidence.
- required_fix: preserve fail-closed poisoning explicitly after any over-budget returned chunk while avoiding ambiguous successful-byte accounting. A dedicated poisoned flag is preferable to pretending rejected bytes were successfully consumed; `_assert_within_byte_budget()` must reject before any subsequent underlying body I/O. Update the new oversize-accounting test to assert the safe state contract rather than `_bytes_read == 0` as the sole invariant. Do not weaken `remaining + 1`, cumulative byte caps, type validation, deadlines, loopback/proxy/redirect controls, or the existing poisoning tests.
- fix_sha: none.
- verification_required: focused read/readline overflow + poisoning + exact-limit/EOF + ERR-0015 negative-read regressions, Ruff, mypy, then exact canonical Quality success.
- integrator_handoff: reject the oversize-before-accounting Backend slice and all descendants as READY until `ERR-0016` is corrected and exactly verified.

## Persistent release/runtime crash knowledge

These remain regression/release-acceptance classes only and are not current `OPEN` entries unless reproduced on the exact current candidate SHA.

- Windows R1/R2 packaging: `PackageNotFoundError` from missing `pypdf` distribution metadata and associated supervisor relaunch behavior.
- Frozen-entrypoint routing: unknown child argv must fail closed; preserve two-EXE separation and prevent recursive Desktop/Core/Scheduler multiplication.
- Process-tree invariant: exactly one Desktop instance; workers remain bounded/non-growing.
- 2048-context chat regression: preserve adaptive reserve behavior and exact 2048-context regression coverage before release.
- Windows scheduler/lane-lock crash cluster observed 2026-09-05: `PermissionError: [Errno 13] Permission denied` in `athena/jobs/lane_lock.py::_lock_nonblocking`, then `SchedulerLaneOwnershipError`, then packaged-worker `OSError: [Errno 22] Invalid argument`.
- Additional startup signatures: `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'`.

## Release/Beta regression matrix

Before any Windows/Beta promotion-ready claim, require exact-candidate evidence for pypdf package metadata/no relaunch loop, fail-closed frozen argv/two-EXE routing, exactly-one-Desktop bounded workers, adaptive 2048-context budgeting, lane-lock/scheduler/package-worker error-path stability, duplicate-column migration safety, Core/storage-bootstrap startup, Windows path safety, Linux storage, local install/start, Validator, Ruff, mypy and full pytest. Any exact-SHA recurrence blocks promotion until its root cause is closed with real verification.

## Current integrator handoff

- `ERR-0001` through `ERR-0013` and `ERR-0015` are `FIXED`; `ERR-0014` remains `STALE`; `ERR-0016` is `OPEN`.
- Reject Backend oversize-before-accounting lineage beginning at `5e6862fe9544465e3aed66840601a204d4d2cae5` as READY while the current descendant still removes post-overflow poisoning.
- Current Backend `a5904fc2078a8dec5eece17dd352436d14453d8f` has canonical Quality `34019237735` in progress; non-pytest jobs are green, but the code still contains the `ERR-0016` root cause.
- Current UI `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4` has canonical Quality `34019891561` in progress; previous UI `34017125454@bf7fadf849140697dc63c92c6a5c6c69335e3278 = success`.
- Current Develop `8236500a5ae0ae58e7dce5bb3cf0771eb534670d` has no exact completed canonical Quality observed this run; do not promote it based on older lineage alone.
