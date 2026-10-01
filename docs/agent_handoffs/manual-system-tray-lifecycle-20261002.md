# Manual handoff — System tray lifecycle — 2026-10-02

## Ausgangslage

`src/athena/desktop/pathena_system_tray.py` already existed on Develop and `install_system_workspace()` already installed that controller into the real main-window path. Runtime SYSTEM snapshots also already fed the tray icon state.

The missing lifecycle contract was narrower but user-visible: the installed tray controller did not intercept a main-window Close event. Closing the window therefore closed the window instead of implementing Beta 18 §49's close-to-tray behavior.

An earlier inspection looked only for a direct `install_system_tray()` call in `desktop/app.py` and incorrectly described bootstrap wiring as missing. Deeper integration inspection found the canonical indirect install in `src/athena/desktop/system_workspace.py`; this handoff supersedes that earlier statement.

## Root Cause

The tray object and top-level Qt window were connected for status/open actions but not for window lifecycle:

- no event filter intercepted `QEvent.Type.Close`;
- no runtime switch represented the close-to-tray preference;
- tray cleanup was not automatically tied to `QApplication.aboutToQuit`.

Because `install_system_workspace()` already owns tray installation, the fix belongs in the tray controller rather than adding a second installer in `app.py`.

## Änderungen

- `PathenaSystemTrayController` installs a main-window event filter.
- With close-to-tray enabled, a real window Close event is consumed and the same window is hidden instead of closed.
- Added `set_close_to_tray_enabled(bool)` and `close_to_tray_enabled` so a persisted Settings preference can bind to real runtime behavior later.
- Mirrors the active state on `pathenaCloseToTrayEnabled` for truthful Qt/UI inspection.
- `shutdown()` is idempotent, removes the event filter, disables interception, hides the tray and closes its menu.
- `QApplication.aboutToQuit` invokes tray cleanup.
- Focused tray tests cover interception, reopen, disable and teardown.
- System-workspace integration test now proves the real install path owns close-to-tray and can reopen the hidden main window.

## Dateien

- `src/athena/desktop/pathena_system_tray.py`
- `tests/unit/test_pathena_system_tray.py`
- `tests/unit/test_system_workspace.py`
- this handoff

## Verhalten danach

On the existing real desktop composition path:

`app.main → install_system_workspace(window, controller) → install_system_tray(window)`

the main-window Close action is now intercepted by the installed controller, the window hides while the tray session remains available, and "Open pATHENA" restores that same window.

Disabling close-to-tray or shutting down the controller restores ordinary close delivery. Tray Quit still routes through `QApplication.quit`; the existing `app.aboutToQuit` connections retain ownership of controlled Core and scheduler shutdown.

## Validierung

Repository mutation was performed on branch `fix/tray-lifecycle-20261002` from exact base `67174198e1494fd4c8678aad60756c39ef5c160b`.

Focused executable validation required from exact-head CI:
- Ruff / mypy / canonical Quality
- `tests/unit/test_pathena_system_tray.py`
- `tests/unit/test_system_workspace.py`
- UI-focused candidate gate

No local PASS is claimed because this execution environment has GitHub repository access rather than a runnable pATHENA checkout.

## Bekannte Restprobleme

1. Spec-required tray operations for model load/unload, Internet toggle and background-job pause remain visibly disabled because the tray has no trustworthy command path for them. Do not fake-enable them.
2. A persisted Settings preference for close-to-tray is not yet bound. The controller now exposes the real runtime switch needed for that narrow follow-up.
3. Beta §50's wording about asking whether independently service-owned background jobs should continue is only relevant if pATHENA later supports a Core that intentionally survives application Quit. The current desktop owns its child Core/scheduler and already stops them from `aboutToQuit`.
4. A native Windows interactive tray smoke remains valuable even after offscreen Qt tests are green.

## Abhängigkeiten / Konfliktrisiko

No fresh active PR inspected at run start modifies `pathena_system_tray.py` or its focused test. The added system-workspace test exercises existing integration without changing `system_workspace.py`.

Active #334 modifies `desktop/app.py` for LM Studio disposal only. No app.py change is needed for this tray slice, so there is no reason to collide with #334.

## Nächste sinnvolle Schritte

1. Qualify this exact head through canonical Quality and UI-focused CI.
2. Run a Windows packaged interactive smoke: launch → Close → tray remains → Open restores → Quit stops owned helpers.
3. Bind a persisted close-to-tray setting to `set_close_to_tray_enabled` once the Settings ownership lane is free.
4. Wire currently disabled tray actions only when corresponding model/network/job commands can report real success/failure.

## Branch / base

- Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
- Branch: `fix/tray-lifecycle-20261002`
- PR: #362
