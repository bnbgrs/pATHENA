# ASCII panel mypy reachability failure

Date: 2026-08-23
Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Failing head: `58397e97d5ea4f6f75c50106cc35c86e47c88433`
GitHub Actions run: `32613955984`
Job: `97131399493` (`Python 3.12 quality`)

## Gate state before fix

The specification validator passed `63/63`, Ruff passed, and mypy failed before pytest could run.

Exact mypy findings from the GitHub Actions job log:

```text
src/athena/desktop/ascii_panel.py:196: error: Statement is unreachable [unreachable]
                return self._context
                ^~~~~~~~~~~~~~~~~~~~
src/athena/desktop/ascii_panel.py:218: error: Non-overlapping identity check
(left operand type: "QLineEdit", right operand type: "AsciiPanel") [comparison-overlap]
                if line_edit is self or not line_edit.isVisible():
                   ^~~~~~~~~~~~~~~~~
Found 2 errors in 1 file (checked 234 source files)
```

## Root cause

`QApplication.activeWindow()` is typed as `QWidget | None`. After the `None` case is replaced with `self.window()`, `root` is already a `QWidget`; a subsequent `isinstance(root, QWidget)` guard is therefore statically always true and its fallback return is unreachable.

`root.findChildren(QLineEdit)` returns `QLineEdit` instances, while `self` is an `AsciiPanel` derived from `QPlainTextEdit`. The identity comparison `line_edit is self` can never be true and mypy correctly reports the types as non-overlapping.

## Fix

Commit `d03eddd27ab2b7a9dfdf8b9981fc2df9098b3c22` removes only the two redundant checks:

- remove the unreachable `isinstance(root, QWidget)` fallback after `root` has been normalized to a widget;
- remove the impossible `line_edit is self` comparison while retaining the visibility filter.

No runtime behavior is intentionally changed. No new feature is introduced.

## Verification plan

The PR-triggered quality gate is the authoritative verification path for this branch. The next run must confirm, in order:

1. specification validator remains green;
2. Ruff remains green;
3. mypy passes all 234 source files;
4. pytest proceeds, exposing the next real failure if one exists.
