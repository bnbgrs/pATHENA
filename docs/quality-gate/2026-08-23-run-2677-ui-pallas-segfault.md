# Quality Gate Incident — Run #2677 native Qt/PySide segfault in PALLAS binding

Date: 2026-08-23

## Status

- Priority: P0 test-process crash / UI runtime safety
- Ownership: UI
- Quality status: BLOCKED on UI owner
- Product mutation by Quality: none
- Execution status: reproduced by Linux full CI run #2677

## Run / test

- Workflow run: `#2677` / `32662756936`
- Linux quality job: `97251316701`
- Tested PR head: `e09650b2e76043e1c1cf5c2eb60ba913762a9f10`
- Test active at crash: `tests/unit/test_pathena_command_palette_presentation.py::test_command_palette_uses_quiet_product_copy_without_losing_commands`
- pytest had collected 3897 tests and reached approximately 66% before termination.

## Fatal error

```text
Fatal Python error: Segmentation fault
pytest exit: -11
```

Top of native-facing Python stack:

```text
src/athena/desktop/ascii_panel.py:253 in _bind_pallas_target
src/athena/desktop/ascii_panel.py:166 in set_context
src/athena/desktop/window.py:2660 in _select_page
src/athena/desktop/pathena_window.py:566 in _select_page
src/athena/desktop/window.py:369 in __init__
src/athena/desktop/pathena_window.py:79 in __init__
tests/unit/test_pathena_command_palette_presentation.py:16
```

Loaded native extensions include shiboken6 and PySide6 QtCore/QtGui/QtWidgets/QtTest.

## Current code re-verification

On active branch HEAD `66ae047e7b917b568915ef2612a6622e47f30c62`, `_bind_pallas_target()` still performs:

```python
for widget in app.allWidgets():
    if widget.objectName() != "pallasVisualPlaceholder":
        continue
    self._pallas_target = widget
    widget.installEventFilter(self)
    ...
```

The fatal stack points at this binding loop during window construction. A Python exception is not raised; the interpreter is terminated by a native segmentation fault, so this must be treated as a P0 test/runtime stability boundary until isolated.

## Root-cause hypothesis to verify, not yet proven

The likely high-risk boundary is interaction with Qt object lifetime while iterating `QApplication.allWidgets()` after thousands of UI tests in one process. A stale/deleted C++ object wrapped by Shiboken, event-filter installation during construction, or re-entrant widget lifecycle could produce a native crash where normal Python guards are insufficient.

This hypothesis is intentionally not recorded as confirmed root cause until a targeted reproducer distinguishes:

- isolated test vs suite-order dependent crash;
- valid vs deleted Shiboken wrapper;
- event-filter installation vs `objectName()`/`update()`/signal connection;
- PALLAS target discovery vs unrelated prior UI corruption.

## Required UI verification

1. Run the single crashing test in isolation under `QT_QPA_PLATFORM=offscreen`.
2. Run the nearest preceding UI tests plus the crashing test to detect suite-order dependence.
3. Reproduce repeatedly to distinguish deterministic crash from flake.
4. Inspect Qt object validity/lifetime around `QApplication.allWidgets()` and event-filter binding.
5. Add a regression that can execute repeatedly without native process termination.
6. Re-run the full Linux keep-going gate; pytest must reach a normal summary instead of exit `-11`.

## Quality consequence

Until this is fixed, full pytest cannot provide a complete failure inventory: ordinary failures after 66% are invisible, and failures seen before the segfault lack a final detailed pytest summary. This crash therefore blocks reliable downstream regression triage and is higher priority than ordinary UI assertion failures from the same run.
