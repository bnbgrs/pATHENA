# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`.
- Baseline SHA observed this run: `da493c1390192425d50caddc451c1a497027027a`.
- Worker branch: `postmerge/errors`.
- Error branch pre-run head: `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`.
- Relevant worker heads: UI `f09406daab9440ee77a06e907add84280b3ae936`; Backend `7b37f0629d3a137301ef04284524a8dfd78c36d3`; Core `daf618982b068557919b58a3e0e6935c9cf41afe`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Fresh evidence

- Historical `ERR-0004` remains `FIXED`. Its exact Ruff evidence is already closed by exact-head Quality `33804193396 = success`; no current Ruff recurrence exists.
- `ERR-0014` had two exact canonical recurrences: UI Quality `33975657049@97b051612ca1199907a47d7e3f6938e3f1f8ca37` and `33978563758@8adcc65f394c556b2783b5da070a52c9afc27d0d`, both terminating full pytest with `SIGSEGV` / exit `139` at `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`.
- Two later exact canonical UI successors on the unchanged affected controller/test lineage completed green: `33978582156@fb98e47fde410137b971a303678d4e63f66e1d6d = success` and `33981877292@074c7b9a4ccf9271a91dd1e56784601f749ac020 = success`.
- Current UI Quality `34001923188@f09406daab9440ee77a06e907add84280b3ae936` is still in progress. Windows path safety, Linux storage, Local install smoke, Validator, Ruff and mypy are already PASS; full pytest remains in progress at this handoff update.
- Current Backend Quality `34001608473@7b37f0629d3a137301ef04284524a8dfd78c36d3` is still in progress and therefore is not PASS/failure evidence yet.
- Latest completed exact Develop Quality remains `33989730675@d14aca9504021bdacadb89dc478ca41545ab4316 = success`. Current Develop head `da493c1390192425d50caddc451c1a497027027a` has no exact completed canonical Quality run yet.
- No new concrete deduplicated primary failure is established in this run, so no speculative product or harness mutation is justified.

## Root-cause disposition

- Bounded class for historical `ERR-0014`: Qt/QObject/QThreadPool/queued-signal/application-lifecycle runtime teardown around the real asynchronous controller harness.
- A `DesktopApiController` product regression remains unestablished because the affected source/test blobs were unchanged across both red and multiple green canonical executions.
- Do not create a speculative product or harness mutation while the failure is non-reproducing. Reopen the same stable ID immediately if the exact SIGSEGV signature recurs; then capture the exact Qt lifecycle delta or take the minimal lifecycle fix once no colliding UI owner mutation exists.
- No mocks, Skip/XFail, dummy success path, weaker off-UI-thread assertions, Ruff/mypy relaxation, or Security/Storage/Recovery/Windows guard weakening is permitted.

## Persistent Windows/runtime regression knowledge

The following signatures are retained as Beta/release acceptance knowledge only. They are not automatically OPEN without current exact-SHA reproduction, but a current reproduction must reopen/create the corresponding deduplicated error immediately.

- Windows R1/R2 packaging: `PackageNotFoundError` caused by missing `pypdf` distribution metadata plus supervisor relaunch behavior.
- Frozen-entrypoint routing: unknown child argv must fail closed and must never recursively multiply Desktop/Core/Scheduler. Preserve the two-EXE split.
- Process-tree invariant: exactly one Desktop instance and bounded/non-growing workers.
- 2048-context chat regression: fixed `2048` output reserve plus `256` safety against a 2048 LM-Studio context is invalid. Preserve adaptive reserve behavior and require explicit 2048-context regression coverage before release.
- Windows scheduler/lane-lock crash cluster observed 2026-09-05: `PermissionError: [Errno 13] Permission denied` in `athena/jobs/lane_lock.py::_lock_nonblocking`, followed by `SchedulerLaneOwnershipError: Scheduler control lane already has a live process owner.`, followed by `OSError: [Errno 22] Invalid argument` in the packaged-worker failure path. Before Beta/release this cluster must be deliberately reproduced/verified closed on the exact candidate SHA.
- Additional startup signatures retained for exact-SHA regression: `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'`.

## Release/Beta acceptance matrix

No Windows/Beta candidate is promotion-ready until the exact candidate SHA has explicit regression evidence for:

1. pypdf package metadata availability and no supervisor relaunch loop;
2. fail-closed frozen child argv routing and two-EXE separation;
3. exactly-one-Desktop / bounded-worker process tree;
4. adaptive 2048-context output budgeting;
5. lane-lock permission / scheduler ownership / packaged-worker error-path stability;
6. duplicate-column migration/startup safety;
7. Core and storage-bootstrap startup;
8. canonical Windows path safety, Linux storage, local install/start, Ruff, mypy, Validator and full pytest.

Any exact-SHA recurrence blocks promotion until root cause is closed with real verification.

## Integrator handoff

- `ERR-0001` through `ERR-0013` remain error-cleared on recorded exact evidence; `ERR-0004` remains closed and current Ruff evidence is green.
- Historical red UI `8adcc65f394c556b2783b5da070a52c9afc27d0d` / Quality `33978563758` remains rejected as READY.
- `ERR-0014` is `STALE`, not `FIXED`: later exact canonical green runs on the unchanged affected lineage establish current non-reproduction but no corrective SHA.
- Do not block otherwise-green UI integration solely on stale `ERR-0014`; reopen it if the exact exit-139/controller-refresh signature recurs.
- Current UI `f09406da...` and Backend `7b37f062...` must not be called READY until their running canonical Quality jobs complete successfully.
- Preserve StorageHealth unavailable-path/NUL guards, provider truthfulness, total deadline, cumulative byte budget, body-handle/file-descriptor restrictions, loopback-only/proxy-free transport, Security, Storage and Recovery invariants.
- Before Beta/release, run the persistent Windows/runtime regression matrix above on the exact candidate SHA; historical signatures alone do not create current OPEN errors.

## Next scan

1. Consume canonical UI Quality `34001923188@f09406daab9440ee77a06e907add84280b3ae936` and Backend Quality `34001608473@7b37f0629d3a137301ef04284524a8dfd78c36d3` when complete.
2. Reopen `ERR-0014` only if its exact SIGSEGV/controller-refresh signature recurs.
3. Allocate the next stable ID only for a new concrete deduplicated primary failure, then finalize root cause or apply the minimal non-colliding fix in that same cycle where evidence permits.
4. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, Windows path safety, Linux storage and local install/start scanning without manufacturing failures.
