# pATHENA UI Handoff

## Current baseline
- Integration target: `develop/pathena-next@a76537a1002e323a97d18a0a95a4d39ce5f298ee`.
- Worker: `postmerge/ui`.
- Worker synchronization: NON-FORCE merge `29613f40741428a97d07d93110fcfd4087ef74e1` from current Develop into UI; `main` unchanged.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## UI-GAP-0004 — Startup/readiness infrastructure copy
Status: `FIXED`. Canonical Quality run `33804193396` passed. The bounded UI-GAP-0004 lineage is already integrated into Develop; ERR-0004 may remain closed.

## UI-GAP-0005 — Persistent desktop system tray
Status: `FIXED`, P1, Screen 06 / desktop shell adjunct.

Spec anchor: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires a persistent tray icon and access to Open, model load/unload, Internet toggle, background-task pause, System status and Quit.

Verified bounded slice:
- `faabeb42fc7d13e04f660c3be1222a95e1f47836`: `PathenaSystemTrayController` owns one `QSystemTrayIcon`.
- `47d4473d80fc61660674a96feeb0ba93c28c3d1e`: focused Qt tests for enabled real paths and explicit unavailable states.
- `441c9ee3889b2927332ecd9cc4b33abd89b8b88f`: `SystemWorkspace` installs exactly one tray controller for the desktop window.
- exact UI head `acc156a8538e83ffec4e3eba4b9bef3e9c2fdb37` passed canonical ATHENA Quality Gate `33814651800` with conclusion `success`.

Real enabled paths remain Open pATHENA, System status and Quit. Primary-model load/unload, Internet toggle and background-task pause remain visible but disabled with `pathenaUnavailable=True` until Core/Backend exposes trustworthy commands; no side effect or success state is fabricated.

Integrator handoff for UI-GAP-0005: READY for independent bounded review/integration of the three product/test commits above. Screen 06 remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`, never `MATCH` without original pixels.

## UI-GAP-0006 — Tray runtime-state visibility
Status: `IMPLEMENTED_PENDING_VERIFY`, P1, Screen 06 / tray adjunct.

Spec anchor: the same Alpha desktop spec requires the tray symbol to expose simple system states such as normal, warning and unavailable conditions.

Bounded candidate:
- `ea027e44a30e335459a9449bb95879700b905551`: tray presentation accepts only an explicit runtime-state value, restores the app icon for `success`, uses warning/critical standard icons for stale/unavailable/error, and maps unknown values fail-closed to `unavailable`.
- `64927940daca2d36dc52616f9d412ff0025cea06`: existing `SystemWorkspace._apply_overview()` forwards the real `SystemRuntimeOverview.state`; no new telemetry source is invented.
- `4be2ac9e69e8a60f2f98fc32ac636017961583c6`: focused Qt test covers success/stale/error/unavailable and unknown fallback, including non-null icon and exact truthful tooltip state.

Canonical Quality run `33818773088` is pending on exact product/test head `4be2ac9e69e8a60f2f98fc32ac636017961583c6`; no PASS is claimed yet.

## Handoffs
- Integrator: UI-GAP-0005 is READY from exact green run `33814651800`. Do not integrate UI-GAP-0006 until its exact product/test Quality is green.
- Backend/Core: expose trustworthy model load/unload, normal-chat Internet toggle and background-pause commands before UI enables those tray actions.
- Error: no new confirmed defect; classify any `33818773088` failure by exact signature only.

## Next UI work
Consume Quality `33818773088`. If green, mark UI-GAP-0006 `FIXED` technically and Screen 06 `IMPLEMENTED_PENDING_VISUAL_REVIEW`; then trace the next explicit Alpha/Beta/UI mismatch. If red, fix only the exact root cause without weakening tests, Ruff, Qt, platform or product guards.
