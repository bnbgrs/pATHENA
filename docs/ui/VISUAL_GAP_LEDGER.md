# pATHENA Visual Gap Ledger

Baseline: `dd4b623cc7bbc5b5a24c4427382f0b98ff50ad02`
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
- Candidate product/test commit: `99d6b31c78be2932154137a6527200759f349628`.
- Candidate behavior: disconnected normal-workspace copy says `pATHENA reconnecting` / `Getting pATHENA ready`, keeps detailed recovery direction in System, and preserves the real `core-offline` state property plus existing controller/service semantics.
- Verification history: canonical Quality run `33785726577` on synchronized candidate lineage `b76115748aed53e3502a71eef10a41b11f97f8ae` passed Windows path safety, Linux storage, local-install smoke, specification validator, mypy and full pytest, but failed Ruff B010 at `tests/unit/test_pathena_startup_experience_2900.py:61` because the harness called `setattr(window, "_core_transport_ready", False)` with a constant attribute name.
- Harness correction: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` replaces the B010-triggering dynamic assignment with a typed test-window subclass carrying the same disconnected-state contract; no product assertion, availability rule, backend behavior or guard is weakened.
- Current verification: ATHENA Quality Gate `33791855218` is SHA-bound to `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` and is pending/running. Do not promote before a successful exact-SHA result.
- Status: `FIXED_PENDING_VERIFY`.
- Acceptance: no backend, transport, persistence, security, capability, focus, or availability semantics changed; technical Core state remains represented internally and may remain visible in System diagnostics.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
