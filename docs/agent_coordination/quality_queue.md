# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve/verify two mypy errors in `src/athena/research/models.py` | CI run #2097: line 71 operator error after helper call; line 239 assignment inference conflict | BACKEND | BLOCKED | 2026-08-23, HEAD `cf0ef334216ccbcb066c34188f4bdba47271a192` |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve/verify three mypy unreachable errors in `src/athena/research/idempotency.py` | CI run #2097: line 56 `Sequence[...]` combined with `str`/`bytes`/`bytearray` runtime guard | BACKEND | BLOCKED | 2026-08-23, HEAD `cf0ef334216ccbcb066c34188f4bdba47271a192` |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve/verify two mypy errors in `_persisted_int()` | CI run #2097: `int(object)` overload and resulting `Any` return | BACKEND | BLOCKED | 2026-08-23, HEAD `cf0ef334216ccbcb066c34188f4bdba47271a192` |
| QG-CI-FAILFAST-COVERAGE | P1 | Assess whether fail-fast full gate hides independent pytest regressions; define targeted verification policy without weakening gate semantics | #2097 stops at mypy, so pytest state is unknown | QUALITY/GATE | READY | 2026-08-23, HEAD `cf0ef334216ccbcb066c34188f4bdba47271a192` |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of recent commits for newly introduced lint/type/test regressions, prioritizing files changed after last verified green slice | Branch advanced substantially since prior run | QUALITY/READ-ONLY | READY | 2026-08-23, HEAD `cf0ef334216ccbcb066c34188f4bdba47271a192` |
| QG-WINDOWS-GATE-PARITY | P2 | Inspect test/gate infrastructure for Windows-specific path, locking, subprocess, and Qt/offscreen parity risks | Project target includes Windows desktop usage while CI evidence is Ubuntu | QUALITY/GATE | READY | 2026-08-23, HEAD `cf0ef334216ccbcb066c34188f4bdba47271a192` |
| QG-PACKAGING-START-PATH | P2 | Verify packaging/install/start path coverage after gate is unblocked; identify missing smoke checks | Quality gate currently does not reach all downstream checks while mypy is red | QUALITY/GATE | READY | 2026-08-23, HEAD `cf0ef334216ccbcb066c34188f4bdba47271a192` |

## Current primary failure

Run #2097 (`ATHENA Quality Gate`) on PR merge commit `95871cc0f598d893da918d39399aeefd1cebcedb`, branch head `cf0ef334216ccbcb066c34188f4bdba47271a192`:

- Specification validator: PASS (63/63)
- Ruff: PASS
- mypy: FAIL (7 errors / 3 files)
- pytest and subsequent checks: NOT REACHED

Backend-owned slices remain `BLOCKED` for this verifier until the owning bot changes those files. The verifier must re-read HEAD before reclassification and then run targeted verification before a full gate.
