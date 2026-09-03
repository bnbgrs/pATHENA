# pATHENA Visual Gap Ledger

Baseline: `647ea036329280378a7e573aca0df905f48ac3b1`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. The original 11 reference screenshots remain unavailable for direct visual comparison; therefore no pixel-level mismatch or `MATCH` claim is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED`
- Product commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- Test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Verification evidence: exact UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate `33720745475`; lineage is integrated in Develop.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED`
- Product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`
- Test-contract commit: `1685221150c724deceb5d150a4d2dcff2bdd867b`
- Verification evidence: exact corrected worker head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426`; exact verified blobs were integrated into Develop in `93a9344d3902c920da5ff283eb51bbb1f0d815b8`.

## UI-GAP-0003 — PALLAS full-view transition can hit a transient missing tab-order document binding

- Category: `INTERACTION`
- Screen: `08 — PALLAS`
- Severity: `P1`
- Evidence: canonical Backend run `33744816398` exposed `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface` failing through `MessageActionTabOrderController.eventFilter()` when `document` was transiently absent during Qt lifecycle churn.
- UI candidate product commit: `689da6c1dc2221f89825fffde947f792c7b503e7`
- Focused regression commit: `034cb8d923d48bea708b48cac0ef0f6343511051`
- Status: `FIXED`
- Verification evidence: exact UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` passed ATHENA Quality Gate `33751403354` with conclusion `success`.
- Integration evidence: bounded equivalent product/test changes landed on Develop as `d149f6bbfd367f2999c8ee54e52326695aeb9f55` and `df60ad0e0b3084da05a8b55d94a227798296a1ac`; Backend changes were disjoint.
- Acceptance: transient missing binding is an unhandled/no-op lifecycle state; existing ChildAdded resynchronization, action ordering, disabled-state preservation and composer return target remain unchanged.

## UI-GAP-0004 — Normal startup exposes local-Core infrastructure as foreground copy

- Category: `STATE`
- Screen: `11 — Startup / Empty / Disconnected state`
- Severity: `P1`
- Evidence: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires normal use to present pATHENA while daemon/workers/providers remain background infrastructure; prior startup/readiness presentation exposed `Local core offline`, `Waiting for the local core`, and Core-specific composer/tool-tip guidance.
- Affected widgets/files: `localStatus`, `promptInput`, `emptyStateTitle`; `src/athena/desktop/pathena_startup_experience_2900.py`; `src/athena/desktop/pathena_offline_comprehension_4700.py`; focused tests in `tests/unit/test_pathena_startup_experience_2900.py` and `tests/unit/test_pathena_offline_comprehension.py`.
- Product/test candidate: `99d6b31c78be2932154137a6527200759f349628`.
- Candidate behavior: disconnected normal-workspace copy says `pATHENA reconnecting` / `Getting pATHENA ready`, keeps detailed recovery direction in System, and preserves the real `core-offline` state property plus existing controller/service semantics.
- Ruff correction chain: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` closed B010; the initial I001 formatting attempt `ecbf44ddd0fb8c7428d4cca090834eca284b997e` was insufficient; final import-order correction `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` orders the SCREAMING_SNAKE_CASE QtWidgets symbol before CamelCase as Ruff/isort requires.
- Focused verification: run `33804104455` passed dependency-lock validation, Ruff on both affected harnesses, and both startup/offline focused pytest files.
- Canonical verification: Quality run `33804193396` completed `success` on the byte-identical cleanup tree `15cdecfd067f39fc2a96e84a83772a67fefb9760`; Python 3.12 quality, specification validator, Ruff, mypy, full pytest, Windows path safety, Linux storage regressions, local-install smoke and canonical enforcement all passed.
- Status: `FIXED`.
- Integrator-ready product/harness lineage: bounded UI-GAP-0004 changes through final harness commit `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`; temporary validation-workflow commits are not part of the retained product/test tree.
- Acceptance: no backend, transport, persistence, security, capability, focus, availability or product-state semantics changed; technical Core state remains represented internally and may remain visible in System diagnostics.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
