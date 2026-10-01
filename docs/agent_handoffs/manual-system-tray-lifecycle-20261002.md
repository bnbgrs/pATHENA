# Manual handoff — System tray lifecycle — 2026-10-02

## Ausgangslage

`src/athena/desktop/pathena_system_tray.py` existed on current Develop, but its controller only created a tray icon/menu. It did not own the main-window close lifecycle. A normal window close therefore had no controller-level path to become "hide to tray", even though Beta 18 requires configurable close-to-tray behavior and a persistent tray session.

The current desktop bootstrap also does not call `install_system_tray()`. That final bootstrap wiring is intentionally not changed in this slice because active PR #334 currently owns `src/athena/desktop/app.py`.

## Root cause

The tray object and the top-level Qt window had no lifecycle contract. No event filter intercepted `QEvent.Type.Close`, there was no runtime switch for close-to-tray, and tray teardown was not automatically tied to `QApplication.aboutToQuit`.

## Änderungen

- `PathenaSystemTrayController` now installs a main-window event filter.
- With close-to-tray enabled, a real window Close event is consumed and the window is hidden instead of being closed.
- Added `set_close_to_tray_enabled(bool)` and `close_to_tray_enabled` so Settings can later bind a real persisted preference without inventing UI-only state.
- Mirrors the active state on `pathenaCloseToTrayEnabled` for truthful Qt/UI inspection.
- `shutdown()` is idempotent, removes the event filter, disables close interception, hides the tray, and closes its menu.
- `aboutToQuit` now always invokes tray cleanup when a controller is installed.
- Added focused Qt tests proving interception, reopen, disable, and teardown behavior.

## Dateien

- `src/athena/desktop/pathena_system_tray.py`
- `tests/unit/test_pathena_system_tray.py`

## Verhalten danach

Once the controller is installed by the desktop bootstrap, closing the main window can keep the Qt session alive in the tray without delivering the close event to the main window. "Open pATHENA" restores that same window. Disabling the setting or shutting down the controller restores ordinary close delivery.

This slice does **not** claim the shipped desktop is already tray-enabled because `app.py` still does not install the controller.

## Validierung

Repository mutation was performed on branch `fix/tray-lifecycle-20261002` from exact base `67174198e1494fd4c8678aad60756c39ef5c160b`.

Focused validation to require from CI:
- Ruff for the changed source/test files
- mypy/canonical Quality
- `tests/unit/test_pathena_system_tray.py`

No local PASS is claimed because this execution environment has repository access through the GitHub connector rather than a runnable checkout.

## Bekannte Restprobleme

1. **Bootstrap wiring remains open:** `src/athena/desktop/app.py` currently never calls `install_system_tray()`.
2. **Collision:** active PR #334 changes `src/athena/desktop/app.py`; do not add competing app bootstrap edits until #334 is integrated or reconciled.
3. Spec-required tray operations for model load/unload, Internet toggle, and background-job pause remain visibly disabled because this controller still has no trustworthy command path for them. Do not fake-enable them.
4. The persisted Settings preference for close-to-tray is not wired yet. The controller now exposes the real runtime switch required for that future narrow integration.

## Konfliktrisiko / Parallelität

No fresh PR inspected at run start modifies `src/athena/desktop/pathena_system_tray.py` or `tests/unit/test_pathena_system_tray.py`.

Do not touch active #334's `app.py` from this branch. After #334 lands, a narrow follow-up can install the tray controller and bind the existing/persisted close-to-tray preference if one exists.

## Nächste sinnvolle Schritte

1. Qualify this exact head through focused/system-tray + canonical Quality.
2. After #334 integration, create a fresh branch from Develop and wire `install_system_tray(window, app=app, ...)` into `desktop/app.py`.
3. Add an application-bootstrap acceptance test proving: launch → close main window → process remains alive → tray Open restores window → tray Quit performs controlled supervisor shutdown.
4. Only then mark Beta 18 §47/49/75 as implemented.

## Branch / base

- Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
- Branch: `fix/tray-lifecycle-20261002`
