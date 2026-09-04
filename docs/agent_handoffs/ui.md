# pATHENA UI Handoff

## Current baseline
- Integration target: `develop/pathena-next@4d36d5f13e1449973e74c48df5e2efb53d0e8aae`.
- Worker: `postmerge/ui`.
- Worker synchronization: NON-FORCE merge `7594f85e16f3fb5529cf2c8bc9cde0111e919a65` incorporated current Develop while preserving the bounded tray-state UI files; `main` unchanged.
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

## UI-GAP-0006 — Tray runtime-state visibility
Status: `FIXED`, P1, Screen 06 / tray adjunct.

Spec anchor: the Alpha desktop spec requires the tray symbol to expose simple system states such as normal, warning and unavailable conditions.

Verified bounded slice:
- `ea027e44a30e335459a9449bb95879700b905551`: tray presentation accepts only an explicit runtime-state value, restores the app icon for `success`, uses warning/critical standard icons for stale/unavailable/error, and maps unknown values fail-closed to `unavailable`.
- `64927940daca2d36dc52616f9d412ff0025cea06`: existing `SystemWorkspace._apply_overview()` forwards the real `SystemRuntimeOverview.state`; no new telemetry source is invented.
- `4be2ac9e69e8a60f2f98fc32ac636017961583c6`: focused Qt test covers success/stale/error/unavailable and unknown fallback.
- `72e43bc18c28b5c92f6528919abf788f66924ba9`: mypy-only QApplication ownership narrowing after the existing runtime guard.
- exact UI head `72e43bc18c28b5c92f6528919abf788f66924ba9` passed canonical ATHENA Quality Gate `33822861477` with conclusion `success`.

Integrator handoff for UI-GAP-0006: READY for independent bounded review/integration of the runtime-state lineage above. Screen 06 is technically `IMPLEMENTED_PENDING_VISUAL_REVIEW`, never `MATCH` without the original reference pixels.

## Next evidence-backed UI gap
`UI-GAP-0007` P1 / Screen 06: `_SystemSubnav` currently renders `Runtime`, `Storage`, `Network` and `Logs` in the same destination-like treatment as `Overview`, but there is no navigation/product path behind those labels. This violates the UI rule that visible controls must either have a real product path or be clearly unavailable. The next bounded UI slice should mark those non-destinations explicitly unavailable (or wire them only if a real path exists) and add a focused Qt contract test. No backend semantics are required.

## Handoffs
- Integrator: UI-GAP-0006 is READY from exact green run `33822861477`; UI-GAP-0005 was already independently READY earlier.
- Backend/Core: expose trustworthy model load/unload, normal-chat Internet toggle and background-pause commands before UI enables those tray actions.
- Error: no new confirmed defect; ERR-0004 stays closed.

## Next UI work
Implement UI-GAP-0007 as a bounded System-subnav truthfulness slice with focused Qt verification, then canonical Quality on the exact candidate. Do not infer screenshot geometry while references remain unavailable.
