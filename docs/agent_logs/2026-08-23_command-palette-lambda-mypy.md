# Command palette lambda mypy failure

Date: 2026-08-23
Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Failing head: `84d5e8f6d3ad5ab9e62cb8b8a9767ab75176d6ba`
GitHub Actions run: `32616422526`
Job: `97137813143` (`Python 3.12 quality`)

## Gate state before fix

The specification validator passed `63/63`, Ruff passed, and the previous `ascii_panel.py` mypy errors were gone. mypy then exposed one new error:

```text
src/athena/desktop/command_palette.py:108: error: Cannot infer type of lambda [misc]
                        action=lambda row=row: self.window.navigation.setCurrentRow(row),
                               ^
Found 1 error in 1 file (checked 235 source files)
```

## Root cause

`_Command.action` is declared as `Callable[[], None]`, while the loop used a lambda with a defaulted capture parameter (`lambda row=row: ...`). Although the default makes the callable invocable without arguments at runtime, mypy cannot infer that lambda cleanly against the zero-argument callable contract in this context.

## Fix

Commit `ed122e5b72869541fe3c863fd726592b4af9ad35` replaces the default-argument lambda with a typed action factory:

- `_workspace_action(self, row: int) -> Callable[[], None]`;
- an inner zero-argument `action() -> None` captures the row;
- `_Command.action` receives that explicitly typed zero-argument callable.

The navigation behavior is unchanged. No feature work was added.

## Verification plan

Run the PR-triggered quality gate again and require:

1. specification validator green;
2. Ruff green;
3. mypy green across all source files;
4. pytest proceeds, exposing the next genuine failure if any.
