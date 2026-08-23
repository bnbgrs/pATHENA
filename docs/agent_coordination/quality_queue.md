# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve/verify two mypy errors in `src/athena/research/models.py` | Historical CI #2097; helper `_nonnegative_int()` still returns `None` while callers rely on post-validation arithmetic/narrowing | BACKEND | BLOCKED | 2026-08-23; current file re-read on active branch, static pattern still present; no newer completed mypy run |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve/verify three mypy unreachable errors in `src/athena/research/idempotency.py` | Historical CI #2097; typed `Sequence[tuple[...]]` is still combined with runtime guards that mypy can consider unreachable | BACKEND | BLOCKED | 2026-08-23; current file re-read; executed re-verification pending |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve/verify two mypy errors in `_persisted_int()` | Historical CI #2097; `_persisted_int(value: object)` still performs direct `int(value)` conversion | BACKEND | BLOCKED | 2026-08-23; current file re-read; executed re-verification pending |
| QG-MIGRATION-JOURNAL-ANCESTOR-BOUNDARY | P1 | Verify Backend fix for unsafe migration-journal ancestors | Current code now validates ancestors before read/write, uses `is_link_boundary`, `O_NOFOLLOW`, and handle/path identity checks; targeted tests prove no `os.open` before rejection. Error log updated. | BACKEND + QUALITY/VERIFY | IN_PROGRESS | 2026-08-23; static fix verified through HEAD `07fe4000...`; Windows lane now includes `test_migration_journal.py`; executed PASS pending |
| QG-MIGRATION-CLONE-REPARSE-BOUNDARY | P1 | Verify Backend fix for Windows junction/reparse migration clone boundaries | Shared `is_link_boundary` and repeated source/candidate boundary checks are present; Windows lane includes `test_migration_clone.py` | BACKEND + QUALITY/VERIFY | IN_PROGRESS | 2026-08-23; static fix verified; executed Windows/Linux PASS pending |
| QG-CI-SUPERSEDED-RUNS | P1 | Keep CI useful under continuous branch writes | Workflow uses one PR concurrency group with `cancel-in-progress: false`; pending runs continue to be superseded by rapid branch churn | QUALITY/GATE | IN_PROGRESS | 2026-08-23; runs #2656/#2657 cancelled while newer heads arrived; latest observed runs remain subject to pending supersession |
| QG-CI-FAILFAST-COVERAGE | P1 | Prove `--keep-going` exposes pytest after earlier failures | Workflow invokes `scripts/quality.py --keep-going`; completed final-policy run log still required | QUALITY/GATE | IN_PROGRESS | 2026-08-23; no completed current-head Linux gate available yet |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Protect fail-fast/keep-going, concurrency, local-smoke and Windows coverage | Contract tests cover workflow policy; Windows contract now additionally requires migration journal and emergency reserve tests | QUALITY/GATE | IN_PROGRESS | 2026-08-23; quality commits `835a0058...` and `eb78b643...`; execution pending |
| QG-FG-002-REGRESSION | P1 | Verify ModelRegistry / active-primary-model layer | Static implementation/test audit covers canonical IDs, duplicate/unknown rejection and active-model validation | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; executed PASS pending |
| QG-FG-004-REGRESSION | P1 | Verify capability UNKNOWN vs UNSUPPORTED semantics | Static domain/test audit preserves SUPPORTED/UNSUPPORTED/UNKNOWN distinctions | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; executed PASS pending |
| QG-FG-005-REGRESSION | P1 | Verify Context Builder source diversity | Static tests cover rank-1 preservation, duplicate deferral and contradiction exemption | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; executed PASS pending |
| QG-FG-007-REGRESSION | P1 | Verify model-load ownership before auto-unload | Tests statically cover unknown/external fail-closed and ATHENA-owned unload permission | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; executed PASS pending |
| QG-FG-012-EXECUTION-GUARD | P1 | Verify protected-runtime execution guard | Static guard/tests cover pre-provider recheck and metadata leakage boundaries | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; runtime verification pending |
| QG-FG-013-MIGRATION-SAFETY | P1 | Regression-watch clone-first migration stack | Free-space contracts clean; clone and journal trust-boundary fixes now statically present; new migration-plan layer is under active Backend development | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; `migration_plan.py` and tests statically reviewed; full execution pending |
| QG-FG-014-REGRESSION | P1 | Verify active SQLite root locality | Static tests cover UNC/mapped drives/Linux network FS and pre-SQLite rejection; Windows lane probes native locality | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; executed Windows PASS pending |
| QG-FG-015-REGRESSION | P1 | Regression-watch emergency reserve and disk-pressure policy | `emergency_reserve.py` and `disk_pressure.py` statically audited; tests cover exact sizing, non-sparse allocation, persistent normal shutdown, EMERGENCY-only release and reassessment. Windows lane now executes emergency-reserve tests. | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; new slice accepted from Feature-Gap backlog; no product mutation; executed PASS pending |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of recent Backend/UI/Feature commits | Current scan covered migration journal, migration plan, emergency reserve/disk pressure and recent backup-details UI changes read-only | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; no foreign product code mutated |
| QG-WINDOWS-GATE-PARITY | P2 | Focus Windows execution on platform-specific storage boundaries | Windows lane covers locality, preflight, runtime paths, migration clone, migration journal and emergency reserve | QUALITY/GATE | IN_PROGRESS | 2026-08-23; extended at `835a0058...`, contract at `eb78b643...`; execution pending |
| QG-PACKAGING-START-PATH | P2 | Execute published `athena-local-smoke` start/restart/persistence path | Dedicated 5-minute Linux job runs `athena-local-smoke --restart-cycles 1` | QUALITY/GATE | IN_PROGRESS | 2026-08-23; completed-run evidence pending |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify 10-minute keep-going gate headroom | Linux full gate 10m; local-smoke and Windows lanes 5m; no timeout evidence yet | QUALITY/GATE | READY | 2026-08-23; do not increase timeout speculatively |
| QG-FG-003-REGRESSION | P2 | Verify all normative provider health states | Static domain/tests include unavailable/starting/ready/busy/degraded/error | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; executed PASS pending |

## Current primary failure baseline

The latest fully classified execution baseline remains historical run #2097:

- Specification validator: PASS (63/63)
- Ruff: PASS
- mypy: FAIL (7 errors / 3 Backend-owned files)
- pytest: NOT REACHED in that historical fail-fast run

The three P0 source patterns were re-read during the current run and remain statically present, but a newer completed keep-going run is required before claiming they still fail on the current HEAD.

## Current safety/coverage state

- Migration journal ancestor defect: **statically fixed, execution pending**; incident log updated.
- Migration clone reparse defect: **statically fixed, execution pending**.
- FG-015 reserve/disk-pressure primitives: **static regression audit completed, execution pending**.
- Windows path-safety lane: now covers locality, runtime paths, migration clone, migration journal and emergency reserve.
- Local install smoke: configured, completed-run evidence pending.
- Rapid branch churn continues to supersede pending PR runs; no PASS/FAIL is inferred from cancelled runs.

## Ready slices if CI remains unavailable

1. `QG-CI-TIMEOUT-HEADROOM` — inspect first completed keep-going timing before any timeout change.
2. Continue `QG-RECENT-REGRESSION-SCAN` on newest FG-013/FG-015 Backend commits without mutating Backend ownership.
3. Review Windows-only storage boundary gaps and add only evidence-driven targeted tests to the Windows lane.
