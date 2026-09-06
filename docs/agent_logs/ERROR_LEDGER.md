# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened.
- Cascades are deduplicated under the primary root cause.
- `FIXED` requires observed verification; unverified corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline branch: `develop/pathena-next`.
- Baseline SHA observed this run: `da493c1390192425d50caddc451c1a497027027a`.
- Worker branch: `postmerge/errors`.
- Pre-run Error branch head: `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`.
- Relevant worker heads: UI `f09406daab9440ee77a06e907add84280b3ae936`; Backend `7b37f0629d3a137301ef04284524a8dfd78c36d3`; Core `daf618982b068557919b58a3e0e6935c9cf41afe`.
- No force update, rebase, history rewrite or merge to `main` was attempted.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Current scan

- Historical `ERR-0004` remains `FIXED`; exact-head Quality `33804193396 = success` closed the startup/readiness Ruff defect and no current Ruff recurrence is present.
- `ERR-0014` had two exact canonical recurrences: UI Quality `33975657049@97b051612ca1199907a47d7e3f6938e3f1f8ca37` and `33978563758@8adcc65f394c556b2783b5da070a52c9afc27d0d` both terminated full pytest with `SIGSEGV` / exit code `139` at `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread` while Windows path safety, Linux storage, local install smoke, Validator, Ruff and mypy passed.
- Two later exact canonical UI successors on the unchanged affected controller/test lineage completed green: `33978582156@fb98e47fde410137b971a303678d4e63f66e1d6d = success` and `33981877292@074c7b9a4ccf9271a91dd1e56784601f749ac020 = success`.
- Current UI Quality `34001923188@f09406daab9440ee77a06e907add84280b3ae936` is still in progress. Windows path safety, Linux storage, Local install smoke, Validator, Ruff and mypy are already PASS; full pytest is still in progress.
- Current Backend Quality `34001608473@7b37f0629d3a137301ef04284524a8dfd78c36d3` is still in progress and is not PASS/failure evidence yet.
- Latest completed exact Develop Quality remains `33989730675@d14aca9504021bdacadb89dc478ca41545ab4316 = success`. Current Develop `da493c1390192425d50caddc451c1a497027027a` has no exact completed canonical Quality run yet.
- No new concrete deduplicated primary failure is established in this run, so no speculative product or harness mutation is justified.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- repro: malformed/bool-like runtime values crossed deletion-ledger mutation/cursor boundaries before SQL validation.
- root_cause: bool-safe runtime validation missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`, `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: canonical Backend boundary evidence green for focused/system checks.
- risk: preserve fail-before-SQL semantics.
- integrator_handoff: no action required.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- repro: canonical Ruff on deletion-boundary harness.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
- files: `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: canonical Ruff PASS `33749788522`.
- risk: none absent recurrence.
- integrator_handoff: no action required.

### ERR-0003 — Stale permanent-inspector harness contract
- severity: P1
- status: `FIXED`
- evidence: Backend `33755878184`; UI `33745885426` green on affected blobs.
- repro: shell tests asserted permanently visible inspector while product contract is contextual.
- root_cause: test contract lagged contextual `Evidence & Activity` behavior.
- files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py`.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification: exact known-green UI lineage `33745885426`.
- risk: do not reintroduce permanent-inspector contract.
- integrator_handoff: preserve contextual state-transition coverage.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- severity: P2
- status: `FIXED`
- evidence: `33785726577` exact B010 diagnostic; `33792012599` I001; exact-head `33804193396 = success`.
- repro: Ruff on startup/readiness harness.
- root_cause: bounded startup/readiness test-harness lint defects, not product startup failure.
- files: `tests/unit/test_pathena_startup_experience_2900.py` and related startup harness imports.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification: canonical exact-head Quality `33804193396 = success`; newer UI exact-head Quality `33972487131 = success` also has Ruff and full pytest PASS.
- risk: none absent exact recurrence.
- integrator_handoff: remain closed unless exact signature recurs.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2
- status: `FIXED`
- evidence: UI `33822842314` mypy failure; corrected `33822861477 = success`.
- repro: mypy on tray application ownership path.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- files: system-tray/UI application ownership implementation and focused tests.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.
- verification: canonical corrected UI Quality `33822861477 = success`.
- risk: none absent recurrence.
- integrator_handoff: no action required.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- severity: P2
- status: `FIXED`
- evidence: Backend `33833499697`; repaired-lineage `33838658964 = success`.
- repro: malformed runtime filter container accepted because static annotation was trusted.
- root_cause: missing explicit runtime container/element validation.
- files: Research filter boundary implementation/tests.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.
- verification: canonical repaired lineage `33838658964 = success`.
- risk: preserve runtime-safe boundary checks.
- integrator_handoff: no action required.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- severity: P1
- status: `FIXED`
- evidence: post-integration `33838377083`; repaired-lineage `33838658964 = success`.
- repro: integrated `acceptance_service.py` imported missing contradiction-review gate.
- root_cause: Core integration omitted required dependency file.
- files: contradiction-review/acceptance Core module graph.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.
- verification: canonical repaired lineage `33838658964 = success`.
- risk: preserve import graph completeness.
- integrator_handoff: no action required.

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- severity: P2
- status: `FIXED`
- evidence: `33845743958`, `33849890354`; exact fix Quality `33854660676 = success`.
- repro: Settings harness expected stale runtime/comprehension copy/state after truthful loopback-only contract changes.
- root_cause: harness contract drift.
- files: `tests/unit/test_pathena_settings_runtime.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- verification: exact canonical Quality `33854660676 = success`.
- risk: do not weaken loopback-only/provider truthfulness.
- integrator_handoff: no action required.

### ERR-0009 — Local HTTP remaining-budget hardening leaves stale readline-size harness expectations
- severity: P2
- status: `FIXED`
- evidence: failing Quality `33900689788`; exact Backend Quality `33911612711 = success`.
- repro: tests expected constant readline request sizes instead of remaining-budget sizes.
- root_cause: correct product `remaining + 1` readline hardening left stale harness expectations.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; equivalent Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.
- verification: exact Backend Quality `33911612711 = success`.
- risk: never revert remaining-budget cap behavior.
- integrator_handoff: preserve strict remaining-budget semantics.

### ERR-0010 — Direct total-deadline hardening invalidates stream timing harness
- first_seen: 2026-09-04
- severity: P2
- area: Backend / Provider-Transport / local HTTP test harness
- status: `FIXED`
- evidence: Backend `33916312429`; recurrent `33933291735` and UI `33936799048`; corrected Backend `33936396203 = success`, UI `33937005854 = success`.
- repro: stale four-timestamp fixture is consumed by iterator plus direct `readline()` pre/post deadline checks before intended timeout.
- root_cause: worker/integration drift reintroduced obsolete timing fixture; product fail-closed deadline behavior is correct.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Backend `e62fcc2db49815e7d32579d0dc68a143f8af07b0`; owner head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0`; UI descendant `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0`.
- verification: corrected six-timestamp fixture preserved through canonical green lineages.
- risk: never weaken total-deadline, cumulative-byte, network, storage, recovery or security guards.
- integrator_handoff: preserve direct total-deadline fail-closed behavior.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- severity: P2
- status: `FIXED`
- evidence: failing UI `33922277491`; exact fix-head UI Quality `33926653411 = success`.
- repro: `provider=None` detail state exposed `fresh` metadata.
- root_cause: provider/detail metadata reused snapshot freshness even when provider was unavailable.
- files: `src/athena/desktop/pathena_settings_runtime.py`, `tests/unit/test_pathena_settings_provider_detail_state.py`.
- fix_sha: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- verification: exact fix-head UI Quality `33926653411 = success`.
- risk: preserve fail-closed unavailable/error presentation semantics.
- integrator_handoff: no action required.

### ERR-0012 — UI synchronization drops unavailable StorageHealth database-path invariant
- first_seen: 2026-09-05
- severity: P1
- area: UI worker synchronization / Storage / regression composition
- status: `FIXED`
- evidence: failing UI Quality `33961422115@9f24999c62b309e25ac512a110ef18011225a4cc`; corrected Quality `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050 = success`; newer current UI Quality `33972487131@5a4bf9116524fcc4ed93aa89c3fefde15ba1023b = success`.
- repro: `StorageHealthSnapshot(status="unavailable", database_open=False, database_path=None, ...)` was accepted on the stale UI tree and failed `test_storage_health_snapshot_requires_path_for_unavailable_state` with `DID NOT RAISE ValueError`.
- root_cause: UI synchronization retained stale `src/athena/storage/health.py`, dropping the unavailable `database_path` invariant while retaining its regression test.
- files: `src/athena/storage/health.py`, `tests/unit/test_storage_health.py`.
- fix_sha: correction present by `cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5`, canonically verified on descendant `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.
- verification: exact Quality `33966822035` SUCCESS; newer exact UI Quality `33972487131` also SUCCESS with Windows path safety, Linux storage, local install, validator, Ruff, mypy, full pytest and canonical enforcement PASS.
- risk: future UI/non-storage synchronization must preserve StorageHealth invariants and Storage/Recovery guards.
- integrator_handoff: old `9f24999c...` tree remains rejected; current exact-green reference `5a4bf911...` remains the prior error-clearance anchor.

### ERR-0013 — UI provider-detail whitespace harness Ruff I001
- first_seen: 2026-09-05
- severity: P2
- area: UI test harness / Ruff
- status: `FIXED`
- evidence: failing UI Quality `33964058090@cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5`; corrected Quality `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050 = success`; newer exact-green UI Quality `33972487131@5a4bf9116524fcc4ed93aa89c3fefde15ba1023b = success`.
- repro: Ruff `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_pathena_settings_provider_detail_whitespace.py:11:1`.
- root_cause: redundant UI provider-detail whitespace harness had an import block outside repository Ruff/isort format.
- files: `tests/unit/test_pathena_settings_provider_detail_whitespace.py`.
- fix_sha: `77b3f9582d4530dbe081e3c81b8768ad00d3f050` removes the redundant offending harness while retaining provider-state coverage elsewhere.
- verification: exact Quality `33966822035` SUCCESS; newer exact-green UI Quality `33972487131` also has Ruff PASS and full pytest PASS.
- risk: do not suppress Ruff I001, weaken assertions, or remove non-redundant provider-state coverage merely to make lint green.
- integrator_handoff: remains closed; unrelated later Qt SIGSEGV is tracked separately as `ERR-0014`.

### ERR-0014 — Qt Desktop controller test process SIGSEGV
- first_seen: 2026-09-05
- severity: P1
- area: UI / Qt Desktop / test runtime lifecycle
- status: `STALE`
- evidence: canonical UI Quality `33975657049@97b051612ca1199907a47d7e3f6938e3f1f8ca37` and recurrent canonical UI Quality `33978563758@8adcc65f394c556b2783b5da070a52c9afc27d0d` both exited `139` with `Fatal Python error: Segmentation fault` during `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`; later exact canonical successors `33978582156@fb98e47fde410137b971a303678d4e63f66e1d6d = success` and `33981877292@074c7b9a4ccf9271a91dd1e56784601f749ac020 = success` did not reproduce it.
- repro: two independent full canonical pytest executions reproduced the same SIGSEGV, followed by two exact canonical clean runs on an unchanged affected controller/test lineage.
- root_cause: historical signal is bounded to nondeterministic Qt/Desktop runtime lifecycle behavior involving real `QThreadPool` work, queued delivery and QObject/QApplication teardown. A deterministic `DesktopApiController` product defect is not established.
- files: `tests/unit/test_desktop_api_controller.py`; diagnostic product reference `src/athena/desktop/api_controller.py`.
- fix_sha: none; no corrective SHA is claimed.
- verification: repeated-clean exact canonical evidence `33978582156` and `33981877292` on the unchanged affected lineage establishes current non-reproduction. This supports `STALE`, not `FIXED`.
- risk: do not convert the real `QThreadPool`/`QSignalSpy` concurrency assertion into mocks, skips or weaker assertions; preserve off-UI-thread execution semantics and Qt object lifetime correctness.
- integrator_handoff: historical red UI `8adcc65f...` remains rejected. Do not block otherwise-green descendants solely on stale `ERR-0014`; reopen this same ID immediately if the exact exit-139/controller-refresh signature recurs and then require exact lifecycle evidence before mutation.

## Persistent release/runtime crash knowledge

These are retained as regression/release-acceptance classes only; they are not current `OPEN` entries unless reproduced on the exact current candidate SHA.

- Windows R1/R2 packaging: `PackageNotFoundError` from missing `pypdf` distribution metadata and associated supervisor relaunch behavior.
- Frozen-entrypoint routing: unknown child argv must fail closed; preserve two-EXE separation and prevent recursive Desktop/Core/Scheduler multiplication.
- Process-tree invariant: exactly one Desktop instance; workers remain bounded/non-growing.
- 2048-context chat regression: fixed `2048` output reserve plus `256` safety cannot be used against a 2048 LM-Studio context. Preserve adaptive reserve behavior and exact 2048-context regression coverage before release.
- Windows scheduler/lane-lock crash cluster observed 2026-09-05: `PermissionError: [Errno 13] Permission denied` in `athena/jobs/lane_lock.py::_lock_nonblocking`, then `SchedulerLaneOwnershipError: Scheduler control lane already has a live process owner.`, then `OSError: [Errno 22] Invalid argument` in the packaged-worker failure path. This cluster must be deliberately reproduced/verified closed on the exact Beta/release candidate SHA.
- Additional startup signatures retained for exact-SHA regression: `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'`.

## Release/Beta regression matrix

Before any Windows/Beta promotion-ready claim, require exact-candidate evidence for pypdf package metadata/no relaunch loop, fail-closed frozen argv/two-EXE routing, exactly-one-Desktop bounded workers, adaptive 2048-context budgeting, lane-lock/scheduler/package-worker error-path stability, duplicate-column migration safety, Core/storage-bootstrap startup, Windows path safety, Linux storage, local install/start, Validator, Ruff, mypy and full pytest. Any exact-SHA recurrence blocks promotion until its root cause is closed with real verification.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.