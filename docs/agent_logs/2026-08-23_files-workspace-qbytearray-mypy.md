# Quality Gate: files workspace QByteArray mypy failure

## Scope

Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Affected file: `src/athena/desktop/files_workspace.py`

## First failing CI

Workflow: `ATHENA Quality Gate`
Run: `32626619203`
Job: `97162823916`
Head before first fix: `798e9b51b63c3dec8167f544b458e431bda37c2e`

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

`QProcess.readAllStandardOutput()` returns `PySide6.QtCore.QByteArray`. Runtime conversion through `bytes(QByteArray)` works, but the PySide6 typing surface does not expose `QByteArray` as satisfying the accepted `bytes()` overloads, so strict mypy rejects it.

The first correction used `QByteArray.data()` directly. CI run `32626686373`, job `97162983201`, then exposed the precise PySide6 stub type for `.data()`:

```text
src/athena/desktop/files_workspace.py:118: error: Item "memoryview[int]" of
"bytes | bytearray | memoryview[int]" has no attribute "decode"  [union-attr]
    chunk = self._process.readAllStandardOutput().data().decode(
            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Found 1 error in 1 file (checked 238 source files)
[FAIL] mypy returned 1.
```

So `.data()` is the correct extraction boundary, but its declared return type is the union `bytes | bytearray | memoryview[int]`; only part of that union exposes `.decode()` directly.

## Final fix

Normalize the typed buffer union to `bytes` before decoding:

```python
bytes(self._process.readAllStandardOutput().data()).decode(
    "utf-8", errors="replace"
)
```

This is accepted by the `bytes()` overloads because each member of the `.data()` union is byte-buffer compatible. It preserves the original UTF-8 replacement behavior and changes no process, persistence, or UI semantics.

Initial fix commit: `4d5a433aeb9a505bdad9efc56a4689f3d2e59572`
Final fix commit: `d2505fadebe7d9d05397da6122e0394451b9c0d3`

## Verification strategy

The authoritative verification is the next pull-request-triggered `ATHENA Quality Gate` for `agent/pathena`:

1. Specification validator remains green.
2. Ruff remains green.
3. mypy passes the `QByteArray` conversion site.
4. pytest runs or exposes the next genuine blocker.
