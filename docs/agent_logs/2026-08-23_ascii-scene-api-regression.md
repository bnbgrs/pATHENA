# ASCII scene API regression

Date: 2026-08-23

## Failure

After the QApplication typing fix, quality run `32611564740` passed the specification validator, Ruff, and mypy, then failed during pytest collection:

```text
ERROR collecting tests/unit/test_desktop_shell.py
tests/unit/test_desktop_shell.py:13: in <module>
    from athena.desktop.ascii_panel import ascii_scene
E   ImportError: cannot import name 'ascii_scene' from 'athena.desktop.ascii_panel'
collected 1464 items / 1 error
```

## Root cause

The reactive ASCII-panel rewrite removed the pre-existing `ascii_scene(context)` helper while `tests/unit/test_desktop_shell.py` still exercises its deterministic semantic-context contract. The PR diff confirms that the helper existed before the rewrite, so this is a production API regression rather than a stale test.

## Fix

Commit `19c820d27b79534bd852646d3550626bb36135da` restores `ascii_scene(context)` as a compatibility adapter over the new deterministic `_seed_grid()` and `_grid_text()` implementation. The reactive renderer remains unchanged.

## Verification

The next fail-fast quality run must pass specification validation, Ruff, mypy, and pytest collection. Any newly exposed pytest failure is treated as a separate incident.
