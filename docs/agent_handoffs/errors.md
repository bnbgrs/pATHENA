# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`.
- Baseline SHA observed this run: `c3d72d3d745033f7382f99a3a717dc1f246d727a`.
- Worker branch: `postmerge/errors`.
- Error branch pre-run head: `9ae3ff7f6c021ea153b7a6a51cb59b6663365c01`.
- Error and Develop remain diverged; no force ref update, rebase or history rewrite was attempted.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0014`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`.
- BLOCKED: none.

## Fresh evidence

- Current UI head `97b051612ca1199907a47d7e3f6938e3f1f8ca37` completed canonical Quality `33975657049 = failure`.
- Exact UI jobs: Windows path safety PASS, Linux storage regressions PASS, local install smoke PASS, specification validator PASS, Ruff PASS, mypy PASS; full pytest FAIL and canonical enforcement FAIL.
- Exact primary signature: Python process terminated with `SIGSEGV` / exit code `139` while executing `tests/unit/test_desktop_api_controller.py::test_controller_refresh_runs_gateway_off_ui_thread`; faulthandler points to line 109 in that test.
- The failing test blob is `0dc03576d71766c5a2ae45bc30f9fdcbb04f7fa9`, byte-identical to the same test on previously exact-green UI head `5a4bf9116524fcc4ed93aa89c3fefde15ba1023b` / Quality `33972487131 = success`.
- Compare `5a4bf911...97b051612` shows no changes to `tests/unit/test_desktop_api_controller.py` or `src/athena/desktop/api_controller.py`; the only product changes are a small `pathena_window.py` accessibility/navigation delta plus unrelated Research changes. The final `97b0516` commit itself changes only `docs/agent_handoffs/ui.md`.
- Therefore `ERR-0014` is bounded to the Qt/Desktop test-runtime/lifecycle path rather than a demonstrated `DesktopApiController` product regression. Product mutation is not justified from this evidence alone.
- Current Backend head `be13865f8ab863809a7da28a38e5c5df35b3fa29` has Quality `33974947204` still `in_progress`; it is neither PASS nor failure evidence.
- Current Develop `c3d72d3d745033f7382f99a3a717dc1f246d727a` has no exact-head canonical Quality result; no repository-wide green claim is made.

## Collision avoidance

- UI owns the affected Qt/Desktop harness and current worker tree. Error does not mutate `tests/unit/test_desktop_api_controller.py` while UI ownership is active.
- UI diagnostic target: reproduce `test_controller_refresh_runs_gateway_off_ui_thread` repeatedly with `QT_QPA_PLATFORM=offscreen`, preserving the real `QThreadPool`/`QSignalSpy` behavior; inspect QApplication/QObject/QThreadPool lifetime and queued-signal teardown. Do not replace with mocks or weaken the off-UI-thread assertion.
- If UI supplies a correction, require exact focused test plus full canonical Quality on the corrective UI SHA before closing `ERR-0014`.
- If one full subsequent UI worker cycle passes unchanged, retain the event as a nondeterministic harness/runtime failure and do not invent a product defect; require another exact recurrence before product mutation.
- Preserve `test_storage_health_snapshot_requires_path_for_unavailable_state`, Ruff rules, provider-state assertions, direct total-deadline, cumulative byte-budget, delegated body-handle/file-descriptor restrictions, loopback-only/proxy-free transport, Security, Storage and Recovery guards.
- No skip/XFail, assertion weakening, dummy success, force-push, history rewrite or merge to main.

## Integrator handoff

- `ERR-0001` through `ERR-0013` remain error-cleared on recorded exact evidence.
- Reject UI `97b051612ca1199907a47d7e3f6938e3f1f8ca37` / Quality `33975657049` as READY because canonical full pytest terminated with `SIGSEGV` in `test_controller_refresh_runs_gateway_off_ui_thread`.
- Do not attribute the crash to `DesktopApiController` product code without a reproducing product delta: the affected test/controller blobs were unchanged from the previous exact-green UI lineage.
- Require UI owner diagnostic/corrective evidence or an exact clean successor run before reclassifying `ERR-0014`.
- Do not substitute in-progress Backend `be13865f...` / `33974947204` for completed evidence.
- Current Develop requires exact-head canonical Quality before any repository-wide global-green claim.

## Next scan

1. Consume the next exact UI Quality after `97b051612ca1199907a47d7e3f6938e3f1f8ca37`; if the same SIGSEGV recurs, finalize the Qt lifecycle root cause and require/minimally apply a harness fix only when UI ownership is clear.
2. Consume Backend Quality `33974947204@be13865f8ab863809a7da28a38e5c5df35b3fa29` when complete.
3. Re-read current UI/Backend/Core worker heads and current Develop; allocate a later ERR only on a concrete, deduplicated new primary failure.
4. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, Windows path safety, Linux storage and local install/start scanning.