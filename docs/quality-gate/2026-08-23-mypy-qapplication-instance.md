# Quality Gate Incident: QApplication instance narrowing

Date: 2026-08-23

## Failing gate

Current branch at diagnosis: `agent/pathena` at `33a86337c6adc4e1700185911c9ff43ac4b8bdcb`.

GitHub Actions run: `32611335714`, job `97124808085`.

The specification validator passed 63/63 checks and Ruff passed. The first failing stage was mypy:

```text
src/athena/desktop/ascii_panel.py:150: error: "QCoreApplication" has no attribute "allWidgets"  [attr-defined]
            for widget in app.allWidgets():
                          ^~~~~~~~~~~~~~
Found 1 error in 1 file (checked 234 source files)
[FAIL] mypy returned 1.
```

## Root cause

`QApplication.instance()` is typed by the PySide6 stubs as a `QCoreApplication | None`. A null check proves only that an application object exists; it does not prove to mypy that the object is a `QApplication`. `allWidgets()` belongs to `QApplication`, so the prior code was runtime-plausible but not statically type-safe.

## Fix

Commit `43a81e16032b0d7959e8e41cb601533f8cbbf6dc` changes `_bind_pallas_target()` to require `isinstance(app, QApplication)` before calling `allWidgets()`. This is a runtime-safe narrowing rather than a cast or type-ignore, so the static contract now matches the actual API requirement.

## Verification plan

The pushed branch must be rechecked by the same fail-fast quality workflow. Expected progression is: specification validator pass, Ruff pass, mypy pass, then pytest. Any newly exposed failure is a separate gate incident and must be handled independently.
