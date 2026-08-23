# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve/verify two mypy errors in `src/athena/research/models.py` | CI run #2097: operator error after `_nonnegative_int()` plus assignment inference conflict; current code still depends on a `None`-returning validator to narrow `object` before comparison | BACKEND | BLOCKED | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; problematic narrowing pattern still present, no Backend fix verified |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve/verify three mypy unreachable errors in `src/athena/research/idempotency.py` | CI run #2097: declared `Sequence[tuple[...]]` combined with runtime `str`/`bytes`/`bytearray` guard; current code retains the same statically unreachable branches | BACKEND | BLOCKED | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; no Backend fix verified |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve/verify two mypy errors in `_persisted_int()` | CI run #2097: `int(object)` overload and resulting `Any` return; current implementation still calls `int(value)` while `value` is typed `object` | BACKEND | BLOCKED | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; no Backend fix verified |
| QG-CI-FAILFAST-COVERAGE | P1 | Ensure CI exposes downstream pytest regressions even when an earlier check is red, without changing local default fail-fast behavior | `scripts/quality.py --keep-going` is implemented and `.github/workflows/quality.yml` invokes it; conclusive completed-run log still required | QUALITY/GATE | IN_PROGRESS | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; newest observed runs #2254/#2262 were queued |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Regression-cover default fail-fast and keep-going execution semantics | `tests/unit/test_quality_script.py` covers default short-circuit and keep-going execution; full CI confirmation pending | QUALITY/GATE | IN_PROGRESS | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; source/tests re-read |
| QG-FG-002-REGRESSION | P1 | Verify newly implemented ModelRegistry / active-primary-model layer without changing Backend-owned code | Feature backlog FG-002 is IMPLEMENTED but explicitly has no executed targeted test result; current `src/athena/model/registry.py` requires CI regression confirmation | QUALITY/READ-ONLY | READY | 2026-08-23, current feature backlog re-read; execution evidence pending |
| QG-FG-004-REGRESSION | P1 | Verify provider capability normalization and unknown-vs-unsupported behavior | Feature backlog FG-004 is IMPLEMENTED with targeted tests added but not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, current feature backlog re-read; execution evidence pending |
| QG-FG-005-REGRESSION | P1 | Verify Context Builder source-diversity behavior, rank-1 preservation, duplicate deferral and contradiction exemption | Feature backlog FG-005 is IMPLEMENTED with targeted tests added but not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, current feature backlog re-read; execution evidence pending |
| QG-FG-007-REGRESSION | P1 | Verify model-load ownership prevents automatic unload of external/unknown loads | Feature backlog FG-007 is IMPLEMENTED with `tests/unit/test_model_load_ownership.py`, but no executed test result is claimed | QUALITY/READ-ONLY | READY | 2026-08-23, current feature backlog re-read; execution evidence pending |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of recent commits for newly introduced lint/type/test regressions, prioritizing files changed after last verified baseline | Branch advanced from quality commit `a2a310f...` to at least `8f9f4e9...`; new model/provider/context changes require CI-backed verification | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7` |
| QG-WINDOWS-GATE-PARITY | P2 | Inspect test/gate infrastructure for Windows-specific path, locking, subprocess, and Qt/offscreen parity risks | Current `.github/workflows/quality.yml` still runs only `ubuntu-latest`; no Windows lane verified | QUALITY/GATE | READY | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7` |
| QG-PACKAGING-START-PATH | P2 | Verify packaging/install/start path coverage and identify missing smoke checks | `pyproject.toml` exposes `athena-local-smoke`; `src/athena/local_smoke.py` exercises integrated DB/retrieval/jobs/backup/recovery/doctor flow; current quality workflow invokes only `scripts/quality.py --keep-going`, no explicit smoke invocation found | QUALITY/GATE | READY | 2026-08-23, current workflow and smoke entry path re-read |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify that keep-going full gate fits the current 10-minute workflow timeout; adjust only on observed timeout evidence | Current quality workflow retains `timeout-minutes: 10`; newer runs are queued, so no timeout conclusion yet | QUALITY/GATE | READY | 2026-08-23, current workflow re-read |
| QG-FG-003-REGRESSION | P2 | Verify all normative provider health states remain represented and stable | Feature backlog FG-003 is IMPLEMENTED but targeted tests were not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, current feature backlog re-read; execution evidence pending |

## Current primary failure

The latest fully classified failure baseline remains CI run #2097:

- Specification validator: PASS (63/63)
- Ruff: PASS
- mypy: FAIL (7 errors / 3 Backend-owned files)
- pytest: NOT REACHED in that historical fail-fast run

All three Backend-owned mypy patterns were re-read on 2026-08-23 at HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7` and remain present. They stay `BLOCKED`; this verifier will not modify Backend-owned production code or tests.

The quality harness now uses `--keep-going`, so the next completed current-head CI log must be used to establish the new Ruff/mypy/pytest baseline and either close or refine `QG-CI-FAILFAST-COVERAGE`. Runs observed during this verification window (#2254 and #2262) were still queued, so no execution result is invented.
