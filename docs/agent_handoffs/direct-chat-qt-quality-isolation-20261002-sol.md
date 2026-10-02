# pATHENA handoff — direct-chat Qt quality isolation — 2026-10-02

BASE: current develop/pathena-next when branch was created
BRANCH: ci/isolate-desktop-direct-chat-20261002-sol

## Reproduction

Research comparison PR #357 passed:
- UI Focused
- 11-Surface Visual Regression
- Specification validator
- Ruff
- mypy
- Windows path safety
- Linux storage regressions
- local install smoke

Canonical pytest then crashed the Python process with a native PySide segmentation fault in:
tests/unit/test_desktop_direct_chat.py::test_controller_creates_stable_chat_and_sends_off_ui_thread

The same Quality lane already isolates test_desktop_api_controller.py and
test_desktop_chat_selection_state.py in fresh interpreters because Qt/PySide owns
process-global native state.

## Fix

- keep test_desktop_direct_chat.py fully mandatory;
- run it in a third fresh interpreter;
- exclude it only from the final remaining-suite process so it runs exactly once;
- track its exit code independently;
- mirror the exact command graph in scripts/quality.py;
- update local runner, quality script and workflow contract tests;
- remove an accidental duplicate local chat_selection test variable while touching the contract.

No test is skipped, xfailed, weakened, or deleted.

## Validation

Exact-head canonical Quality on this CI branch is required before integration.
