# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve/verify two mypy errors in `src/athena/research/models.py` | CI run #2097: operator error after `_nonnegative_int()` plus assignment inference conflict; current code still depends on a `None`-returning validator to narrow `object` before comparison | BACKEND | BLOCKED | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; problematic narrowing pattern still present, no Backend fix verified |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve/verify three mypy unreachable errors in `src/athena/research/idempotency.py` | CI run #2097: declared `Sequence[tuple[...]]` combined with runtime `str`/`bytes`/`bytearray` guard; current code retains the same statically unreachable branches | BACKEND | BLOCKED | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; no Backend fix verified |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve/verify two mypy errors in `_persisted_int()` | CI run #2097: `int(object)` overload and resulting `Any` return; current implementation still calls `int(value)` while `value` is typed `object` | BACKEND | BLOCKED | 2026-08-23, HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7`; no Backend fix verified |
| QG-CI-FAILFAST-COVERAGE | P1 | Ensure CI exposes downstream pytest regressions even when an earlier check is red, without changing local default fail-fast behavior | `scripts/quality.py --keep-going` is implemented and `.github/workflows/quality.yml` invokes it; conclusive completed-run log still required | QUALITY/GATE | IN_PROGRESS | 2026-08-23, branch HEAD observed through `6262a2c93221d1fa3c1616e1789c5d2ea7b66ebb`; current-head runs remained queued, so no downstream pytest result is claimed |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Regression-cover default fail-fast and keep-going execution semantics | `tests/unit/test_quality_script.py` covers default short-circuit and keep-going execution; full CI confirmation pending | QUALITY/GATE | IN_PROGRESS | 2026-08-23; CI execution evidence still pending because current runs remained queued |
| QG-FG-002-REGRESSION | P1 | Verify newly implemented ModelRegistry / active-primary-model layer without changing Backend-owned code | Feature backlog FG-002 is IMPLEMENTED but explicitly has no executed targeted test result; current `src/athena/model/registry.py` requires CI regression confirmation | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |
| QG-FG-004-REGRESSION | P1 | Verify provider capability normalization and unknown-vs-unsupported behavior | Feature backlog FG-004 is IMPLEMENTED with targeted tests added but not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |
| QG-FG-005-REGRESSION | P1 | Verify Context Builder source-diversity behavior, rank-1 preservation, duplicate deferral and contradiction exemption | Feature backlog FG-005 is IMPLEMENTED with targeted tests added but not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |
| QG-FG-007-REGRESSION | P1 | Verify model-load ownership prevents automatic unload of external/unknown loads | `tests/unit/test_model_load_ownership.py` statically covers fail-closed unknown/external ownership, ATHENA-owned auto-unload permission, and refresh clearing ownership even while `loaded=True`; no executed PASS is available yet | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23, static test audit completed; runtime verification pending |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of recent commits for newly introduced lint/type/test regressions, prioritizing files changed after last verified baseline | Branch advanced rapidly during the verification window through at least `6262a2c93221d1fa3c1616e1789c5d2ea7b66ebb`; model/provider/context changes require CI-backed verification | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23, high concurrent branch activity observed; no foreign code mutated |
| QG-WINDOWS-GATE-PARITY | P2 | Inspect test/gate infrastructure for Windows-specific path, locking, subprocess, and Qt/offscreen parity risks | Both `.github/workflows/quality.yml` and `.github/workflows/ui-snapshot.yml` are Linux-only (`ubuntu-latest`) and install `libegl1` with `apt-get`; `scripts/quality.py` itself uses `sys.executable`/Python subprocesses and is not intrinsically Linux-only | QUALITY/GATE | READY | 2026-08-23, current workflows re-read; confirmed coverage gap, not a proven Windows failure; no speculative matrix added |
| QG-PACKAGING-START-PATH | P2 | Verify packaging/install/start path coverage and identify missing smoke checks | `pyproject.toml` exposes `athena-local-smoke = athena.local_smoke:main`; `run_local_smoke()` performs real Core/API start-stop, durable chat recovery, schema and bootstrap-cleanup checks. Quality CI does not invoke the entry point; `tests/unit/test_local_smoke.py` is absent; repository code search found no `run_local_smoke` references and no build/wheel/install verification query matches | QUALITY/GATE | IN_PROGRESS | 2026-08-23, current entry point, implementation and quality workflow re-read; coverage gap established, execution/fix design pending |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify that keep-going full gate fits the current 10-minute workflow timeout; adjust only on observed timeout evidence | Current quality workflow retains `timeout-minutes: 10`; current runs were queued, so there is no timeout evidence supporting a change | QUALITY/GATE | READY | 2026-08-23, current workflow re-read; no speculative timeout increase |
| QG-FG-003-REGRESSION | P2 | Verify all normative provider health states remain represented and stable | Feature backlog FG-003 is IMPLEMENTED but targeted tests were not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |

## Current primary failure

The latest fully classified failure baseline remains CI run #2097:

- Specification validator: PASS (63/63)
- Ruff: PASS
- mypy: FAIL (7 errors / 3 Backend-owned files)
- pytest: NOT REACHED in that historical fail-fast run

All three Backend-owned mypy patterns were re-read on 2026-08-23 at HEAD `8f9f4e992020cb382ba42b0cec5d284a9bf197c7` and remained present at that verified point. They stay `BLOCKED`; this verifier will not modify Backend-owned production code or tests. Later rapidly moving heads have not yet received a completed CI run or a fresh targeted re-read sufficient to supersede that exact evidence.

The quality harness now uses `--keep-going`, so the next completed current-head CI log must establish the new Specification/Ruff/mypy/pytest baseline and either close or refine `QG-CI-FAILFAST-COVERAGE`. Current-head and verifier-documentation runs observed during this window remained queued; no execution result is invented.

## Coverage findings awaiting execution or design

- Windows: current Quality and UI Snapshot CI are Linux-only. This is a real platform-coverage gap, not evidence that pATHENA fails on Windows.
- Packaging/start path: `athena-local-smoke` is a meaningful integrated persistence/restart check, but current Quality CI does not execute it and no direct unit-test/reference coverage was found. Treat as coverage risk until a low-cost, deterministic gate strategy is selected and executed.
