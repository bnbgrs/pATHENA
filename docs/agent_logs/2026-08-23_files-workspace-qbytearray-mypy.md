# Quality Gate: files workspace QByteArray mypy failure

## Scope

Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Affected file: `src/athena/desktop/files_workspace.py`

## Failing CI

Workflow: `ATHENA Quality Gate`
Run: `32626619203`
Job: `97162823916`
Head before fix: `798e9b51b63c3dec8167f544b458e431bda37c2e`

The gate reached and passed both the specification validator and Ruff:

```text
TOTAL 63/63 PASS
All checks passed!
```

It then stopped at mypy with one error:

```text
src/athena/desktop/files_workspace.py:118: error: No overload variant of
"bytes" matches argument type "QByteArray"  [call-overload]
    chunk = bytes(self._process.readAllStandardOutput()).decode(
            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Found 1 error in 1 file (checked 238 source files)
[FAIL] mypy returned 1.
```

## Root cause

`QProcess.readAllStandardOutput()` returns `PySide6.QtCore.QByteArray`. Runtime conversion through `bytes(...)` works, but the PySide6 typing surface does not expose `QByteArray` as satisfying the accepted `bytes()` overloads, so strict mypy rejects it.

`QByteArray.data()` exposes the contained bytes directly and is the type-safe API for decoding process output.

## Fix

Changed only the output conversion from:

```python
bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
```

to:

```python
self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")
```

This preserves the existing UTF-8 decoding and replacement behavior and does not alter process control or UI semantics.

Fix commit: `4d5a433aeb9a505bdad9efc56a4689f3d2e59572`

## Verification strategy

The authoritative verification is the next pull-request-triggered `ATHENA Quality Gate` for `agent/pathena`. Expected progression:

1. Specification validator remains green.
2. Ruff remains green.
3. mypy passes the previous `QByteArray` conversion site.
4. pytest runs or exposes the next genuine blocker.
