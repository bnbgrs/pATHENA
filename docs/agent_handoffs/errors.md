# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`.
- Baseline SHA observed this run: `415debaae20fd84cd12fa0613dc063dc48dd134f`.
- Worker branch: `postmerge/errors`.
- Error branch pre-run head: `3dd9b02aa30cd276f40ad197c0c527eb712e555c`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Fresh evidence

- `ERR-0014` had two exact canonical recurrences: UI Quality `33975657049@97b051612ca1199907a47d7e3f6938e3f1f8ca37` and `33978563758@8adcc65f394c556b2783b5da070a52c9afc27d0d`, both terminating full pytest with `SIGSEGV` / exit `139` at `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`.
- Two later exact canonical UI successors on the unchanged affected controller/test lineage completed green: `33978582156@fb98e47fde410137b971a303678d4e63f66e1d6d = success` and `33981877292@074c7b9a4ccf9271a91dd1e56784601f749ac020 = success`.
- Compare evidence from `074c7b9a...` through later green synchronized UI `0ec14faa...` changes only Integrator handoff and Historical Backfill test coverage; no `tests/unit/test_desktop_api_controller.py` or `src/athena/desktop/api_controller.py` delta exists. The subsequent `0ec14faa...38793f4e` UI delta is theme/focus work and also does not touch the controller/test lifecycle path.
- The repeated-red then repeated-clean unchanged lineage does not support a deterministic pATHENA product defect. `ERR-0014` is therefore dispositioned `STALE`, not `FIXED`: the exact runtime SIGSEGV signal is currently non-reproducing and no code fix is claimed.
- Current UI head `38793f4e116900d4d06db0aff9a8e42c69272141` has canonical Quality `33984881889` in progress; its parent `0ec14faa440319f5e9aa36fa52b86e48cc843bf0` passed `33984735336 = success`.
- Current Develop is `415debaae20fd84cd12fa0613dc063dc48dd134f`; no exact-head repository-wide green claim is made.

## Root-cause disposition

- Bounded class for historical `ERR-0014`: Qt/QObject/QThreadPool/queued-signal/application-lifecycle runtime teardown around the real asynchronous controller harness.
- A `DesktopApiController` product regression remains unestablished because the affected source/test blobs were unchanged across both red and multiple green canonical executions.
- Do not create a speculative product or harness mutation while the failure is non-reproducing. Reopen the same stable ID immediately if the exact SIGSEGV signature recurs; then capture the exact Qt lifecycle delta or take the minimal lifecycle fix once no colliding UI owner mutation exists.
- No mocks, Skip/XFail, dummy success path, weaker off-UI-thread assertions, Ruff/mypy relaxation, or Security/Storage/Recovery/Windows guard weakening is permitted.

## Integrator handoff

- `ERR-0001` through `ERR-0013` remain error-cleared on recorded exact evidence; `ERR-0004` remains closed and current Ruff evidence is green.
- Historical red UI `8adcc65f394c556b2783b5da070a52c9afc27d0d` / Quality `33978563758` remains rejected as READY.
- `ERR-0014` is `STALE`, not `FIXED`: two later exact canonical green runs on the unchanged affected lineage establish current non-reproduction but no corrective SHA.
- Do not block otherwise-green UI integration solely on stale `ERR-0014`; reopen it if the exact exit-139/controller-refresh signature recurs.
- Preserve StorageHealth unavailable-path/NUL guards, provider truthfulness, total deadline, cumulative byte budget, body-handle/file-descriptor restrictions, loopback-only/proxy-free transport, Security, Storage and Recovery invariants.

## Next scan

1. Consume canonical UI Quality `33984881889@38793f4e116900d4d06db0aff9a8e42c69272141` when complete and reopen `ERR-0014` only if its exact signature recurs.
2. Consume newest Backend/Core exact canonical evidence and allocate `ERR-0015` only for a concrete deduplicated primary failure.
3. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, Windows path safety, Linux storage and local install/start scanning without manufacturing failures.
