# Quality Gate Incident: research result selection branches marked unreachable

Date: 2026-08-23

## Failing gate

GitHub Actions run `32631752029` (run number `941`), job `97175503119`, reached mypy after the specification validator and Ruff both passed.

Mypy reported two unreachable branches in `src/athena/desktop/research_results_extension.py`:

```text
src/athena/desktop/research_results_extension.py:144: error: Statement is unreachable  [unreachable]
            return ""
            ^~~~~~~~~
src/athena/desktop/research_results_extension.py:175: error: Statement is unreachable  [unreachable]
            pending = False
            ^~~~~~~~~~~~~~~
```

## Root cause

The code used `QListWidget.currentItem()` and then guarded for `None` to represent no current selection. Qt can have no selected row at runtime, but the installed PySide6 type stubs expose `currentItem()` as a non-optional `QListWidgetItem`. Under the project's strict mypy configuration, the `None` branches are therefore considered unreachable.

The runtime state is valid; the static representation was the problem.

## Fix

Commit `b62c474f8b8bd83a3f09f4478c413e5d06c686c4` expresses the same no-selection state through `QListWidget.currentRow()`, whose `-1` sentinel is both the Qt runtime contract and statically representable.

- `_selected_job_state()` now returns an empty state when `currentRow() < 0`.
- `_sync_proposal_actions()` now disables actions when `currentRow() < 0` and only dereferences an item for a valid row.

No behavior, action eligibility, job-state interpretation, proposal semantics, or UI copy changed. No mypy suppression was added.

## Verification plan

Re-run the fail-fast quality workflow. The two `unreachable` diagnostics above must disappear while specification validation and Ruff remain green. Any remaining mypy diagnostics are separate incidents and are handled independently.
