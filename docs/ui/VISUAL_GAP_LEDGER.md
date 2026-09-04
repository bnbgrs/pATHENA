# pATHENA Visual Gap Ledger

Baseline: `4d36d5f13e1449973e74c48df5e2efb53d0e8aae`
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
- Product/test candidate: `99d6b31c78be2932154137a6527200759f349628`.
- Ruff correction chain: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` closed B010; final import-order correction `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` closed I001.
- Focused verification: run `33804104455` passed dependency-lock validation, Ruff on both affected harnesses, and both startup/offline focused pytest files.
- Canonical verification: Quality run `33804193396` completed `success`; Python 3.12 quality, specification validator, Ruff, mypy, full pytest, Windows path safety, Linux storage regressions, local-install smoke and canonical enforcement all passed.
- Status: `FIXED`.

## UI-GAP-0005 — Required desktop system-tray surface is absent from the current Develop tree

- Category: `CONTROL`
- Screen: `06 — System` / desktop shell lifecycle adjunct; no screenshot-level geometry is inferred.
- Severity: `P1`.
- Spec evidence: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires a persistent desktop tray icon, background-active behavior when the main window is minimized, and tray access to open pATHENA, load/unload the primary model, toggle Internet, pause background tasks, inspect system status and quit.
- Status: `FIXED`.
- Candidate module: `src/athena/desktop/pathena_system_tray.py` at `faabeb42fc7d13e04f660c3be1222a95e1f47836`.
- Focused tests: `tests/unit/test_pathena_system_tray.py` at `47d4473d80fc61660674a96feeb0ba93c28c3d1e`.
- Application wiring: `SystemWorkspace` owns one tray controller from `441c9ee3889b2927332ecd9cc4b33abd89b8b88f`.
- Real paths: `Open pATHENA` restores/raises/activates the existing window; `System status` selects the existing System navigation row; `Quit pATHENA` delegates to `QApplication.quit` and therefore preserves existing `aboutToQuit` supervisor shutdown wiring.
- Honest unavailable actions: model load, model unload, Internet toggle and background-task pause remain visible but disabled with `pathenaUnavailable=True`; no backend command or success state is fabricated.
- Canonical verification: exact UI head `acc156a8538e83ffec4e3eba4b9bef3e9c2fdb37` passed ATHENA Quality Gate `33814651800` with conclusion `success`.
- Acceptance: one persistent tray lifecycle; background activity remains alive while the window is minimized; all enabled actions delegate existing real paths; unsupported spec actions remain explicitly unavailable until Core/Backend exposes trustworthy commands.

## UI-GAP-0006 — Tray icon does not surface real system runtime state

- Category: `STATE`
- Screen: `06 — System` / desktop tray adjunct; no screenshot-level geometry is inferred.
- Severity: `P1`.
- Spec evidence: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires the tray symbol to expose simple system states such as normal, warning and unavailable conditions without opening the main window.
- Prior behavior: the tray icon and tooltip remained static even though `SystemWorkspace` already receives a real `SystemRuntimeOverview.state` derived from the desktop API snapshot.
- Status: `FIXED`.
- Product commits: `ea027e44a30e335459a9449bb95879700b905551` adds fail-closed tray state presentation; `64927940daca2d36dc52616f9d412ff0025cea06` wires the existing real `SystemRuntimeOverview.state` into the tray controller.
- Test commit: `4be2ac9e69e8a60f2f98fc32ac636017961583c6` covers `success`, `stale`, `error`, `unavailable`, and unexpected-state fallback without synthesising telemetry.
- Typing correction: `72e43bc18c28b5c92f6528919abf788f66924ba9` narrows QApplication ownership after the existing runtime guard; no runtime semantics changed.
- Presentation contract: success restores the application icon and `Ready`; stale/unavailable use a warning icon with explicit tooltip; error uses a critical icon with `Attention needed`; any unknown state fails closed to `unavailable`.
- Canonical verification: exact UI head `72e43bc18c28b5c92f6528919abf788f66924ba9` passed ATHENA Quality Gate `33822861477` with conclusion `success`.
- Acceptance: tray state is derived only from the existing real `SystemRuntimeOverview.state`; no telemetry, provider state or backend success condition is synthesized.

## UI-GAP-0007 — System subnavigation presents unavailable destinations as if interactive

- Category: `CONTROL`
- Screen: `06 — System`; no screenshot-level geometry is inferred.
- Severity: `P1`.
- Status: `OPEN`.
- Evidence: `_SystemSubnav` renders `Overview`, `Runtime`, `Storage`, `Network` and `Logs` with the same destination-like item treatment, but only the current Overview surface has a real product/navigation path. The other four labels are passive `QLabel` entries with no destination and no unavailable marker.
- Contract: visible destination-like controls must either route to a real product path or be clearly represented as unavailable; do not fabricate backend/system pages.
- Planned bounded fix: keep `Overview` as the real selected destination; mark `Runtime`, `Storage`, `Network` and `Logs` explicitly unavailable/disabled with an accessibility-visible unavailable state, plus a focused Qt contract test.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
