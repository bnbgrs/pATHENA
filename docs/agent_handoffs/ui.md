# pATHENA UI Handoff

## Current baseline
- Integration target: `develop/pathena-next@3cfef2c2ee67799066ceefaf9ea84287817f256a`.
- Worker: `postmerge/ui`.
- Worker head before verification docs: `40efd4f894aa07110de67c9260deaf4fb14e1c41`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.
- Current Develop has advanced independently; no force synchronization or main mutation is allowed.

## UI-GAP-0004 — Startup/readiness infrastructure copy
Status: `FIXED`. Canonical Quality run `33804193396` passed. The bounded UI-GAP-0004 lineage is already integrated into Develop; ERR-0004 remains closed.

## UI-GAP-0005 — Persistent desktop system tray
Status: `FIXED`, P1, Screen 06 / desktop shell adjunct.

Verified bounded slice:
- `faabeb42fc7d13e04f660c3be1222a95e1f47836`: `PathenaSystemTrayController` owns one `QSystemTrayIcon`.
- `47d4473d80fc61660674a96feeb0ba93c28c3d1e`: focused Qt tests for enabled real paths and explicit unavailable states.
- `441c9ee3889b2927332ecd9cc4b33abd89b8b88f`: `SystemWorkspace` installs exactly one tray controller for the desktop window.
- exact UI head `acc156a8538e83ffec4e3eba4b9bef3e9c2fdb37` passed canonical ATHENA Quality Gate `33814651800`.

Real enabled paths remain Open pATHENA, System status and Quit. Primary-model load/unload, Internet toggle and background-task pause remain visible but disabled until Core/Backend exposes trustworthy commands.

## UI-GAP-0006 — Tray runtime-state visibility
Status: `FIXED`, P1, Screen 06 / tray adjunct.

Verified bounded slice:
- `ea027e44a30e335459a9449bb95879700b905551`: fail-closed tray state presentation.
- `64927940daca2d36dc52616f9d412ff0025cea06`: forwards existing real `SystemRuntimeOverview.state`.
- `4be2ac9e69e8a60f2f98fc32ac636017961583c6`: focused Qt coverage.
- `72e43bc18c28b5c92f6528919abf788f66924ba9`: typing-only QApplication narrowing.
- exact UI head `72e43bc18c28b5c92f6528919abf788f66924ba9` passed Quality `33822861477`.

## UI-GAP-0007 — System subnavigation truthfulness
Status: `FIXED`, P1, Screen 06.

Verified bounded slice:
- `f32b64b5e3c3f0c91434b9a8e72d11c869512495`: Overview remains the sole real selected destination; Runtime/Storage/Network/Logs visibly state `Unavailable`, carry `pathenaUnavailable=True`, expose accessibility descriptions, and use the existing empty/unavailable presentation state.
- `40efd4f894aa07110de67c9260deaf4fb14e1c41`: focused Qt contract coverage for destination names and unavailable semantics.
- exact UI head `40efd4f894aa07110de67c9260deaf4fb14e1c41` passed canonical ATHENA Quality Gate `33830601076`; Python quality, Ruff, mypy, full pytest, Windows path safety, Linux storage regressions and local-install smoke all succeeded.

Integrator handoff for UI-GAP-0007: READY for independent bounded review/integration of `f32b64b5e3c3f0c91434b9a8e72d11c869512495 -> 40efd4f894aa07110de67c9260deaf4fb14e1c41`. No backend/system destination was fabricated.

## Next evidence-backed UI gap
The next slice should be selected from an explicit Alpha/Beta/UI contract after reviewing current Develop and worker ownership. The Alpha desktop contract still requires clearly visible user-facing Internet/privacy status and simple model-management controls, but UI must not expose fabricated actions until trustworthy Core/Backend commands exist. Prefer a bounded state/accessibility/control-truthfulness slice that does not change backend/storage/security semantics.

## Handoffs
- Integrator: UI-GAP-0007 is READY from exact green run `33830601076`.
- Backend/Core: expose trustworthy model load/unload, normal-chat Internet toggle and background-pause commands before UI enables those tray actions or equivalent controls.
- Error: no new confirmed defect; ERR-0004 remains closed.

## Next UI work
Trace the highest explicit Alpha/Beta/UI mismatch on current Develop, implement at most one bounded truthfulness/accessibility/state slice, add focused Qt coverage, and run canonical Quality on the exact candidate. Do not infer screenshot geometry while references remain unavailable.
