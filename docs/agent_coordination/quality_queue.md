# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve/verify two mypy errors in `src/athena/research/models.py` | CI run #2097: operator error after `_nonnegative_int()` plus assignment inference conflict; current helper still returns `None`, so callers cannot rely on it for static narrowing of `object` | BACKEND | BLOCKED | 2026-08-23, HEAD `025ca1ab6657e08748cbe96c148f021c97b0c3d2`; narrowing helper pattern re-read and still present |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve/verify three mypy unreachable errors in `src/athena/research/idempotency.py` | CI run #2097: typed `Sequence[tuple[...]]` is combined with runtime guards whose branches are statically unreachable under the declared type | BACKEND | BLOCKED | 2026-08-23, HEAD `025ca1ab6657e08748cbe96c148f021c97b0c3d2`; typed Sequence plus tuple/sequence runtime validation re-read, no executed fix verification |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve/verify two mypy errors in `_persisted_int()` | CI run #2097: `int(object)` overload and resulting `Any` return; current implementation still calls `int(value)` while `value` is typed `object` | BACKEND | BLOCKED | 2026-08-23, HEAD `025ca1ab6657e08748cbe96c148f021c97b0c3d2`; problematic conversion re-read and still present |
| QG-CI-SUPERSEDED-RUNS | P1 | Prevent stale quality runs from consuming runner capacity ahead of the newest branch state | Rapid `agent/pathena` commits produced queued PR runs #2475 and #2477 while workflow had no `concurrency` cancellation. Commit `03e373d49d5832a2aac6fbfa6eb04a3bbca88326` adds event-scoped supersession cancellation without changing product code | QUALITY/GATE | IN_PROGRESS | 2026-08-23; implementation committed, next current-head workflow behavior still requires CI observation |
| QG-CI-FAILFAST-COVERAGE | P1 | Ensure CI exposes downstream pytest regressions even when an earlier check is red, without changing local default fail-fast behavior | `scripts/quality.py --keep-going` is implemented and `.github/workflows/quality.yml` invokes it; conclusive completed-run log still required | QUALITY/GATE | IN_PROGRESS | 2026-08-23; current runs had been stuck queued, superseded-run cancellation is now implemented to unblock fresh evidence |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Regression-cover default fail-fast and keep-going execution semantics | `tests/unit/test_quality_script.py` covers default short-circuit and keep-going execution; full CI confirmation pending | QUALITY/GATE | IN_PROGRESS | 2026-08-23; static test coverage re-read, execution evidence pending |
| QG-FG-002-REGRESSION | P1 | Verify newly implemented ModelRegistry / active-primary-model layer without changing Backend-owned code | Feature backlog FG-002 is IMPLEMENTED but explicitly has no executed targeted test result; current `src/athena/model/registry.py` requires CI regression confirmation | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |
| QG-FG-004-REGRESSION | P1 | Verify provider capability normalization and unknown-vs-unsupported behavior | Feature backlog FG-004 is IMPLEMENTED with targeted tests added but not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |
| QG-FG-005-REGRESSION | P1 | Verify Context Builder source-diversity behavior, rank-1 preservation, duplicate deferral and contradiction exemption | Feature backlog FG-005 is IMPLEMENTED with targeted tests added but not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |
| QG-FG-007-REGRESSION | P1 | Verify model-load ownership prevents automatic unload of external/unknown loads | `tests/unit/test_model_load_ownership.py` statically covers fail-closed unknown/external ownership, ATHENA-owned auto-unload permission, and refresh clearing ownership even while `loaded=True`; no executed PASS is available yet | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23, static test audit completed; runtime verification pending |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of recent commits for newly introduced lint/type/test regressions, prioritizing files changed after last verified baseline | 93 commits landed between `b8c79ce3...` and `025ca1ab...`; recent changes include chat, model/session/failure/provenance, durable FS, and many UI refinements/tests | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; compare completed, no foreign code mutated |
| QG-WINDOWS-GATE-PARITY | P2 | Inspect test/gate infrastructure for Windows-specific path, locking, subprocess, and Qt/offscreen parity risks | Both `.github/workflows/quality.yml` and `.github/workflows/ui-snapshot.yml` are Linux-only (`ubuntu-latest`) and install `libegl1` with `apt-get`; `scripts/quality.py` itself uses `sys.executable`/Python subprocesses and is not intrinsically Linux-only | QUALITY/GATE | READY | 2026-08-23, current workflows re-read; confirmed coverage gap, not a proven Windows failure; no speculative matrix added |
| QG-PACKAGING-START-PATH | P2 | Verify packaging/install/start path coverage and identify missing smoke checks | `pyproject.toml` exposes `athena-local-smoke = athena.local_smoke:main`; `run_local_smoke()` performs real Core/API start-stop, durable chat recovery, schema and bootstrap-cleanup checks. Quality CI does not invoke the entry point; direct smoke coverage remains absent from CI | QUALITY/GATE | IN_PROGRESS | 2026-08-23; coverage gap established, execution/fix design pending |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify that keep-going full gate fits the current 10-minute workflow timeout; adjust only on observed timeout evidence | Current quality workflow retains `timeout-minutes: 10`; queued runs have not produced timeout evidence supporting a change | QUALITY/GATE | READY | 2026-08-23; no speculative timeout increase |
| QG-FG-003-REGRESSION | P2 | Verify all normative provider health states remain represented and stable | Feature backlog FG-003 is IMPLEMENTED but targeted tests were not executed in connector runtime | QUALITY/READ-ONLY | READY | 2026-08-23, feature backlog re-read; execution evidence pending |

## Current primary failure

The latest fully classified failure baseline remains CI run #2097:

- Specification validator: PASS (63/63)
- Ruff: PASS
- mypy: FAIL (7 errors / 3 Backend-owned files)
- pytest: NOT REACHED in that historical fail-fast run

The three Backend-owned mypy patterns were freshly re-read on 2026-08-23 at HEAD `025ca1ab6657e08748cbe96c148f021c97b0c3d2` and remain structurally present. They stay `BLOCKED`; this verifier will not modify Backend-owned production code or tests. Runtime/CI supersession remains pending because newer runs had been queued rather than completed.

The quality harness uses `--keep-going`, so the next completed current-head CI log must establish the new Specification/Ruff/mypy/pytest baseline and either close or refine `QG-CI-FAILFAST-COVERAGE`. To reduce stale-run starvation, commit `03e373d49d5832a2aac6fbfa6eb04a3bbca88326` adds GitHub Actions concurrency cancellation for superseded runs of the same workflow event/ref.

## Coverage findings awaiting execution or design

- Windows: current Quality and UI Snapshot CI are Linux-only. This is a real platform-coverage gap, not evidence that pATHENA fails on Windows.
- Packaging/start path: `athena-local-smoke` is a meaningful integrated persistence/restart check, but current Quality CI does not execute it. Treat as coverage risk until a low-cost, deterministic gate strategy is selected and executed.
