# Quality Gate: files workspace Ruff import ordering

## Scope

Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Affected file: `src/athena/desktop/files_workspace.py`

## Failing CI

Workflow: `ATHENA Quality Gate`
Run: `32624139216`
Job: `97156757655`
Head before fix: `ecd3d1212226f9e197a04e8092d519eb9378055c`

The specification validator completed successfully with `TOTAL 63/63 PASS`.
The gate then stopped at Ruff with:

```text
I001 [*] Import block is un-sorted or un-formatted
  --> src/athena/desktop/files_workspace.py:8:1

Found 1 error.
[*] 1 fixable with the `--fix` option.

[FAIL] Ruff returned 1.
```

## Root cause

The `PySide6.QtCore` imported names were not in Ruff/isort's canonical case-insensitive ordering. The sequence was:

```python
from PySide6.QtCore import QProcess, QTimer, Qt
```

Ruff expects:

```python
from PySide6.QtCore import QProcess, Qt, QTimer
```

No runtime behavior is affected; this is a deterministic formatting failure in the repository quality gate.

## Fix

Reordered only the imported names in the existing `PySide6.QtCore` import. No functional code, public API, behavior, dependency, or test semantics were changed.

Fix commit: `69b0135b969dcca5851ee12a21a623680c3480a6`

## Verification strategy

The authoritative verification is the pull-request-triggered `ATHENA Quality Gate` for the new `agent/pathena` head. The expected progression is:

1. Specification validator remains green.
2. Ruff passes this previously failing file.
3. The gate proceeds to mypy and pytest, exposing the next genuine blocker if one remains.
