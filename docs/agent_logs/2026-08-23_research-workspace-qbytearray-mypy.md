# Quality Gate: research workspace QByteArray mypy failure

## Scope

Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Affected file: `src/athena/desktop/research_workspace.py`

## Failing CI

Workflow: `ATHENA Quality Gate`
Run: `32626768104`
Job: `97163179994`
Head before fix: `3cb250c1f2afe7f620ecd00ff08b46a51bf1b833`

Before this failure, the gate confirmed:

```text
TOTAL 63/63 PASS
All checks passed!
```

The remaining mypy blocker was:

```text
src/athena/desktop/research_workspace.py:172: error: No overload variant of
"bytes" matches argument type "QByteArray"  [call-overload]
    chunk = bytes(self._process.readAllStandardOutput()).decode(
            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Found 1 error in 1 file (checked 240 source files)
[FAIL] mypy returned 1.
```

## Root cause

This was the same PySide6 typing mismatch already isolated in `files_workspace.py`: `QProcess.readAllStandardOutput()` returns `QByteArray`, while strict mypy does not accept `QByteArray` directly as an input to the declared `bytes()` overloads.

`QByteArray.data()` exposes `bytes | bytearray | memoryview[int]`, all of which can be normalized through `bytes(...)` before UTF-8 decoding.

## Fix

Changed only the output conversion to:

```python
bytes(self._process.readAllStandardOutput().data()).decode(
    "utf-8", errors="replace"
)
```

The existing process control, buffering, UI rendering, UTF-8 decoding and replacement semantics remain unchanged.

Fix commit: `4ef09e27c87858460fbcc75edee3bd6d0d1b1ae0`

## Verification strategy

The next pull-request-triggered `ATHENA Quality Gate` must confirm:

1. Specification validator remains green.
2. Ruff remains green.
3. mypy proceeds beyond `research_workspace.py:172`.
4. pytest runs or the next genuine blocker is exposed.
