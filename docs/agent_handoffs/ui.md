# pATHENA UI Handoff

## Current baseline
- Integration target: `develop/pathena-next@e98c88e0d3b41b81de7efa70873729f873038080`.
- Worker: `postmerge/ui`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## UI-GAP-0004 — Startup/readiness infrastructure copy
Status: `FIXED`. Canonical Quality run `33804193396` passed. The bounded UI-GAP-0004 lineage is already integrated into Develop; ERR-0004 may remain closed.

## UI-GAP-0005 — Persistent desktop system tray
Status: `IMPLEMENTED_PENDING_VERIFY`, P1, Screen 06 / desktop shell adjunct.

Spec anchor: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires a persistent tray icon and access to Open, model load/unload, Internet toggle, background-task pause, System status and Quit.

Implemented bounded slice:
- `faabeb42fc7d13e04f660c3be1222a95e1f47836`: new `PathenaSystemTrayController` owns one `QSystemTrayIcon`.
- `47d4473d80fc61660674a96feeb0ba93c28c3d1e`: focused Qt tests for enabled real paths and explicit unavailable states.
- `441c9ee3889b2927332ecd9cc4b33abd89b8b88f`: `SystemWorkspace` installs exactly one tray controller for the desktop window.

Real enabled paths:
- Open pATHENA -> restore/show/raise/activate the existing window.
- System status -> reuse existing navigation row 5, then restore the window.
- Quit pATHENA -> `QApplication.quit`; existing `aboutToQuit` supervisor stop wiring remains authoritative.

Spec-required actions without a trustworthy current desktop command path are visible but disabled and tagged `pathenaUnavailable=True`: primary-model load, primary-model unload, Internet toggle, background-task pause. No backend command, side effect or success state is fabricated.

Branch synchronization was history-preserving and NON-FORCE in merge `df3cfaad21848f6105cf84ddcf3dcc5827af19af`; Develop product code remained authoritative while UI-only manifest/ledger/handoff state was retained.

## Verification
Draft PR #53 is validation-only and targets `develop/pathena-next`; no auto-merge. Quality run `33814551829` was queued for product head `441c9ee...`; documentation commits subsequently advanced the PR head, so consume the latest exact-head canonical Quality run before marking READY.

## Handoffs
- Integrator: do not integrate UI-GAP-0005 until exact current-head Quality is green. When green, independently review the bounded tray module/test/SystemWorkspace wiring only.
- Backend/Core: expose trustworthy model load/unload, normal-chat Internet toggle and background-pause commands before UI enables those tray actions.
- Error: no new confirmed defect; treat any Quality failure by exact signature only.

## Next UI work
First consume exact current-head Quality for UI-GAP-0005. If green, mark the gap `FIXED` technically but keep Screen 06 `IMPLEMENTED_PENDING_VISUAL_REVIEW` until original pixels are available. Then trace the next explicit Alpha/Beta/UI mismatch; do not manufacture visual gaps.
