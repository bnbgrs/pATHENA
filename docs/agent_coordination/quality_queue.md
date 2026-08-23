# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve/verify two mypy errors in `src/athena/research/models.py` | CI run #2097: line 71 operator error after helper call; line 239 assignment inference conflict | BACKEND | BLOCKED | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132`; no Backend fix verified yet |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve/verify three mypy unreachable errors in `src/athena/research/idempotency.py` | CI run #2097: line 56 `Sequence[...]` combined with `str`/`bytes`/`bytearray` runtime guard | BACKEND | BLOCKED | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132`; no Backend fix verified yet |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve/verify two mypy errors in `_persisted_int()` | CI run #2097: `int(object)` overload and resulting `Any` return | BACKEND | BLOCKED | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132`; no Backend fix verified yet |
| QG-CI-FAILFAST-COVERAGE | P1 | Ensure CI exposes downstream pytest regressions even when an earlier check is red, without changing local default fail-fast behavior | `scripts/quality.py --keep-going` implemented; CI wired to it; runs #2105/#2107 still executing | QUALITY/GATE | IN_PROGRESS | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132` |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Regression-cover default fail-fast and keep-going execution semantics | `tests/unit/test_quality_script.py` added; targeted CI/full-gate verification pending | QUALITY/GATE | IN_PROGRESS | 2026-08-23, commit `a2a310f21477d7dca071183a4dbef3600d888132` |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of recent commits for newly introduced lint/type/test regressions, prioritizing files changed after last verified green slice | #2097 established current mypy baseline; keep-going gate should expose pytest baseline | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132` |
| QG-WINDOWS-GATE-PARITY | P2 | Inspect test/gate infrastructure for Windows-specific path, locking, subprocess, and Qt/offscreen parity risks | `.github/workflows/quality.yml` and `ui-snapshot.yml` both use `ubuntu-latest`; no Windows CI lane found | QUALITY/GATE | READY | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132` |
| QG-PACKAGING-START-PATH | P2 | Verify packaging/install/start path coverage and identify missing smoke checks | `pyproject.toml` exposes `athena-local-smoke`; `src/athena/local_smoke.py` exercises integrated DB/retrieval/jobs/backup/recovery/doctor flow; no workflow invocation found | QUALITY/GATE | READY | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132` |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify that keep-going full gate fits the current 10-minute workflow timeout; adjust only on observed timeout evidence | quality workflow has `timeout-minutes: 10`; #2105/#2107 are long-running after enabling downstream pytest | QUALITY/GATE | READY | 2026-08-23, HEAD `a2a310f21477d7dca071183a4dbef3600d888132` |

## Current primary failure

Run #2097 (`ATHENA Quality Gate`) on PR merge commit `95871cc0f598d893da918d39399aeefd1cebcedb`, branch head `cf0ef334216ccbcb066c34188f4bdba47271a192`:

- Specification validator: PASS (63/63)
- Ruff: PASS
- mypy: FAIL (7 errors / 3 files)
- pytest and subsequent checks: NOT REACHED

The three Backend-owned failures remain `BLOCKED` for this verifier until the owning bot changes those files. Quality-owned work now makes downstream pytest observable in CI via `--keep-going`; runs #2105/#2107 are the first verification runs for that behavior and must be fully evaluated before `QG-CI-FAILFAST-COVERAGE` becomes `DONE`.
