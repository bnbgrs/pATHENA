# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`.
- Baseline SHA observed this run: `f630b27ddb7a40f2982f50f79d9f7d9f1322d1b1`.
- Worker branch: `postmerge/errors`.
- Error branch pre-run head: `e0d009c4ecc2e0db3000acdb4b0dc726e64005de`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0014`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`.
- BLOCKED: none.

## Fresh evidence

- `ERR-0014` reproduced a second time in canonical UI Quality `33978563758@8adcc65f394c556b2783b5da070a52c9afc27d0d`, matching prior Quality `33975657049@97b051612ca1199907a47d7e3f6938e3f1f8ca37`: full pytest terminated with `SIGSEGV` / exit `139` at `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`; Windows path safety, Linux storage, local install smoke, Validator, Ruff and mypy passed.
- Exact-green successor UI `fb98e47fde410137b971a303678d4e63f66e1d6d` passed canonical Quality `33978582156 = success`; the crash did not recur.
- The affected test and `src/athena/desktop/api_controller.py` remain unchanged across the red/green lineage. This rules out a deterministic controller product regression and bounds the active root cause to nondeterministic Qt/QObject/QThreadPool/queued-signal/application-lifecycle teardown behavior in the real test runtime.
- Current UI head `074c7b9a4ccf9271a91dd1e56784601f749ac020` has Quality `33981877292` in progress. Recent UI commits are accessibility/manifest/handoff work and do not constitute a demonstrated Qt lifecycle fix.
- Current Develop is `f630b27ddb7a40f2982f50f79d9f7d9f1322d1b1`; no exact-head repository-wide green claim is made.

## Collision avoidance

- UI still owns the affected Qt/Desktop harness. Error does not concurrently mutate `tests/unit/test_desktop_api_controller.py` while the active UI cycle is running.
- UI diagnostic/fix target remains the real lifecycle boundary: QApplication/QObject ownership, QThreadPool worker completion, queued signal delivery and teardown. Focused verification must retain the real `QThreadPool`/`QSignalSpy` off-UI-thread assertion.
- No mocks, Skip/XFail, dummy success path, weaker assertions, Ruff/mypy relaxation, Security/Storage/Recovery/Windows guard weakening or product-code mutation without a reproducing product delta.
- A single green run without a lifecycle change is not enough to mark `ERR-0014` fixed because the same exact signature has now recurred twice.

## Integrator handoff

- `ERR-0001` through `ERR-0013` remain error-cleared on recorded exact evidence; `ERR-0004` remains closed and current Ruff evidence is green.
- Reject recurrent red UI `8adcc65f394c556b2783b5da070a52c9afc27d0d` / Quality `33978563758` as READY.
- UI `fb98e47fde410137b971a303678d4e63f66e1d6d` / Quality `33978582156` is exact canonical green, but that pass alone does not close `ERR-0014` because no relevant lifecycle correction is established.
- Do not close `ERR-0014` until a real Qt lifecycle correction receives focused verification plus canonical green, or stronger repeated clean evidence explicitly resolves the lifecycle condition.
- Preserve StorageHealth unavailable-path/NUL guards, provider truthfulness, total deadline, cumulative byte budget, body-handle/file-descriptor restrictions, loopback-only/proxy-free transport, Security, Storage and Recovery invariants.

## Next scan

1. Consume canonical UI Quality `33981877292@074c7b9a4ccf9271a91dd1e56784601f749ac020` when complete.
2. If SIGSEGV recurs and UI has still not supplied an active colliding lifecycle fix, Error may take the minimal harness/root-cause fix under the hard progress rule.
3. If UI is green again without a relevant Qt change, retain `ERR-0014` as recurrent nondeterministic lifecycle instability rather than falsely closing it.
4. Continue scanning Backend/Core/Develop exact evidence for the next concrete deduplicated primary failure after `ERR-0014` is dispositioned.