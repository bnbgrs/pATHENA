# System tray close lifecycle handoff — 2026-10-02

## Ausgangslage

Current `develop/pathena-next` exposed a tray controller, but the desktop did not implement the Beta tray acceptance path end to end:

- a normal main-window Close was not intercepted, so Qt's default last-window behavior could terminate the desktop instead of leaving the tray running;
- `PathenaSystemTrayController.shutdown()` existed but was not connected to `QApplication.aboutToQuit`;
- reopening from the tray always used `showNormal()`, discarding a hidden maximized window state;
- the Beta-required `Lock Protected Content` tray entry was absent rather than represented truthfully as unavailable.

Spec anchors:

- `docs/beta/18_Desktop-Anwendung_und_System_Tray.md` §49: Close button → minimize to tray;
- §50: Quit performs controlled shutdown;
- §75: closing the main window leaves the tray, while Quit shuts down cleanly.

## Root Cause

The tray controller only owned the icon/menu. It did not own the main-window Close event or QApplication last-window policy, and its cleanup path was callable only manually. Therefore the UI shell and tray lifecycle were not one coherent state machine.

The restore path also treated every reopen as a minimized-window restore, even when the window had merely been hidden from a maximized state.

## Änderungen

### Product

`src/athena/desktop/pathena_system_tray.py`

- detect whether a real system tray is available;
- when minimize-on-close is enabled **and** a tray is actually available:
  - disable Qt's automatic quit-on-last-window-close behavior;
  - install an event filter for the real main window;
  - intercept Close, ignore destruction, and hide the window so the tray can restore it;
- do not intercept Close when no system tray is available, avoiding an invisible/unrecoverable desktop;
- bind `QApplication.aboutToQuit` to idempotent tray shutdown;
- restore the previous `quitOnLastWindowClosed` value during shutdown;
- remove the window event filter during shutdown;
- only call `showNormal()` for a genuinely minimized window; hidden normal/maximized windows use `show()` so their state is preserved;
- add the Beta-required `Lock protected content · unavailable` action as an honest disabled control until a real lock command path exists;
- expose a `minimize_on_close` constructor/install hook so Settings can own future configuration without rewriting lifecycle logic.

### Tests

`tests/unit/test_pathena_system_tray.py`

Added regression coverage for:

- the new protected-content unavailable action;
- Close → hidden window when a tray can restore it;
- Close not being intercepted when the tray is unavailable;
- QApplication quit-signal cleanup and policy restoration;
- hidden maximized state preservation when reopening from the tray.

## Verhalten danach

With a supported system tray, closing the main pATHENA window keeps the process recoverable from the tray instead of silently exiting. Explicit Quit still exits the Qt event loop and now performs tray cleanup before teardown.

On systems without a tray, pATHENA keeps the ordinary close behavior instead of hiding itself with no recovery surface.

Reopening from the tray preserves a previously maximized hidden window while still normalizing an actually minimized window.

## Dateien

- `src/athena/desktop/pathena_system_tray.py`
- `tests/unit/test_pathena_system_tray.py`
- this handoff

## Validierung

Completed:

- collision check against the 31 commits that advanced `develop/pathena-next` during the run: none touched the product/test files above;
- branch rebuilt on current Develop `467ef434236c320e4afe9d21a39c20a4a2b75728`;
- diff scope review: only tray controller + focused tray tests before this handoff;
- line-length check: no modified product/test line exceeds Ruff's 100-character limit.

Not claimed:

- no local pytest PASS: this runner cannot resolve `github.com`, and its local Python environment does not contain PySide6;
- no manual native Windows tray verification yet;
- CI status is pending until the draft PR exact-head workflow runs.

## Bekannte Restprobleme

- Beta §49 says minimize-to-tray is configurable. This slice provides the real `minimize_on_close` control point and defaults it on, but deliberately does **not** modify Settings because Settings is under active parallel work (#333). A later non-conflicting Settings integration can persist and pass that flag.
- Model load/unload, Internet toggle, protected-content lock, and background-pause tray commands remain disabled where no trustworthy command path is currently wired. No fake action was introduced.
- Native Windows Explorer/taskbar tray behavior still needs exact Windows validation.

## Abhängigkeiten / Konfliktrisiko

At synchronization time, active PRs covered Chat cancellation/UI, Settings, LM Studio, Jobs, Sources, Knowledge, PALLAS QA, Security, Memory, Windows packaging helpers, logging, and model identity. None of the checked current PR file sets touched the tray controller or its focused test.

Do not fold stale PR #53 wholesale into this branch; it is historical source material with a broad old UI delta.

The first implementation branch `fix/system-tray-close-lifecycle-20261002-sol` was based on `67174198…`. Develop advanced by 31 commits during the run. Those commits did not touch the tray files, so the work was cleanly replayed onto the current branch rather than force-moving or rebasing anyone else's branch.

## Nächste sinnvolle Schritte

1. Require exact-head Quality/UI-focused CI on this branch.
2. Run native Windows smoke:
   - launch pATHENA;
   - maximize window;
   - click Close;
   - confirm process and tray remain;
   - choose Open pATHENA and confirm maximized state is retained;
   - choose System Status and confirm navigation;
   - choose Quit and confirm tray/Core/scheduler shutdown completes without orphan processes.
3. After #333 Settings work settles, wire the persisted minimize-to-tray preference into `install_system_tray(..., minimize_on_close=...)` instead of creating a second close-lifecycle implementation.
