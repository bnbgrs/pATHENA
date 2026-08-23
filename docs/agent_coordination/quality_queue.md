# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve/verify historical mypy errors in `research/models.py` | Historical run #2097; current helper pattern still warrants executed recheck | BACKEND | BLOCKED | 2026-08-23; current code re-read, newer Linux result pending |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve/verify historical mypy unreachable errors in `research/idempotency.py` | Historical run #2097; current typed-sequence/runtime-guard pattern still present | BACKEND | BLOCKED | 2026-08-23; newer Linux result pending |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve/verify historical `_persisted_int()` mypy errors | Historical run #2097; direct `int(object)` pattern remains | BACKEND | BLOCKED | 2026-08-23; newer Linux result pending |
| QG-WIN-2677-MIGRATION-CLONE-FSYNC | P1 | Fix Windows migration-clone durable file flush | Run #2677: `_fsync_file()` -> `os.fsync()` on `O_RDONLY` descriptor fails with `OSError [Errno 9] Bad file descriptor`; permanent log `docs/quality-gate/2026-08-23-run-2677-windows-path-safety.md` | BACKEND | BLOCKED | 2026-08-23; executed failure on Windows Server 2025, job `97251316567` |
| QG-FG-015-RESERVE-HEADROOM | P1 | Prevent reserve provisioning from creating EMERGENCY pressure | At 100 GiB total / 2.5 GiB free, current CRITICAL state permits 1 GiB allocation, projecting 1.5 GiB free below 2 GiB EMERGENCY threshold. Log: `docs/quality-gate/2026-08-23-disk-pressure-reserve-provisioning-headroom.md` | BACKEND | BLOCKED | 2026-08-23, defect statically revalidated at HEAD `67e15f78...` |
| QG-WIN-2677-RESERVE-TEST-CONTRACT | P1 | Reconcile wrong-size reserve test with current error contract | Run #2677: expected `does not match`, actual `file size must exactly match required bytes`; current Backend test still contains stale regex | BACKEND/TEST | BLOCKED | 2026-08-23; executed Windows failure, current test re-read |
| QG-MIGRATION-JOURNAL-ANCESTOR-BOUNDARY | P1 | Verify Backend journal ancestor fix | Current code validates ancestors before I/O, uses `is_link_boundary`, `O_NOFOLLOW`, and handle/path identity checks | BACKEND + QUALITY/VERIFY | IN_PROGRESS | 2026-08-23; #2677 selected journal suite produced no journal failure; Linux/full rerun still pending |
| QG-MIGRATION-CLONE-REPARSE-BOUNDARY | P1 | Verify reparse-boundary fix independently of new Windows fsync defect | Reparse tests are in Windows lane; #2677 failed clone's ordinary snapshot path at fsync rather than reparse rejection | BACKEND + QUALITY/VERIFY | IN_PROGRESS | 2026-08-23; Windows clone overall FAIL due separate fsync defect |
| QG-CI-SUPERSEDED-RUNS | P1 | Keep CI useful under continuous branch writes | `cancel-in-progress: false`; run #2677 reached active execution despite rapid pending supersession | QUALITY/GATE | IN_PROGRESS | 2026-08-23; active-run survival now evidenced, completion of Linux job pending |
| QG-CI-FAILFAST-COVERAGE | P1 | Prove `--keep-going` exposes pytest after earlier failures | Linux quality job #2677 is currently executing `scripts/quality.py --keep-going` | QUALITY/GATE | IN_PROGRESS | 2026-08-23; final Linux log pending |
| QG-WIN-LOCALITY-SELECTION | P1 | Keep Linux mountinfo-only tests out of real Windows lane | #2677 exposed two false Windows failures from Linux mountinfo tests; workflow now splits `test_storage_locality.py -k windows` from remaining Windows storage tests; contract updated | QUALITY/GATE | IN_PROGRESS | 2026-08-23; fixed by `0ffbcf0e...` + `e9630faa...`, re-run pending |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Protect keep-going, concurrency, local smoke and Windows lane contracts | Contract includes Windows-only locality selection plus migration journal/emergency reserve coverage | QUALITY/GATE | IN_PROGRESS | 2026-08-23; local-smoke execution PASS in #2677; Windows re-run pending |
| QG-FG-002-REGRESSION | P1 | Verify ModelRegistry / active-primary-model layer | Static audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; execution pending |
| QG-FG-004-REGRESSION | P1 | Verify capability UNKNOWN vs UNSUPPORTED semantics | Static audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; execution pending |
| QG-FG-005-REGRESSION | P1 | Verify Context Builder source diversity | Static audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; execution pending |
| QG-FG-007-REGRESSION | P1 | Verify model-load ownership before auto-unload | Static audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; execution pending |
| QG-FG-012-EXECUTION-GUARD | P1 | Verify protected-runtime execution guard | Static guard/test audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; runtime verification pending |
| QG-FG-013-MIGRATION-SAFETY | P1 | Regression-watch clone-first migration stack | Journal and recovery ancestor issues were fixed in parallel; #2677 exposed a distinct Windows clone fsync defect | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; Windows execution now provides concrete failure evidence |
| QG-FG-014-REGRESSION | P1 | Verify active SQLite root locality | #2677 native Windows locality probe PASS; deterministic Windows cases retained in focused lane | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; native probe PASS, lane rerun pending after selection fix |
| QG-FG-015-REGRESSION | P1 | Regression-watch emergency reserve/disk-pressure policy | #2677 exposed one stale reserve-test expectation; independent static audit found projected-pressure provisioning defect | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; two explicit child slices now tracked |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of newest commits | Migration recovery ancestor issue was found then fixed in parallel; reserve headroom P1 found and logged | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; no foreign product code mutated |
| QG-WINDOWS-GATE-PARITY | P2 | Focus Windows execution on platform-specific storage boundaries | Run #2677 executed on Windows Server 2025: native locality PASS, regression suite FAIL with 4 classified issues | QUALITY/GATE | IN_PROGRESS | 2026-08-23; concrete Windows baseline now established |
| QG-PACKAGING-START-PATH | P2 | Verify `athena-local-smoke` install/start/restart/persistence path | Run #2677 `Local install smoke` completed successfully including dependency lock and disposable Core/API restart smoke | QUALITY/GATE | DONE | 2026-08-23; run #2677 job `97251316671` PASS |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify 10-minute keep-going gate headroom | Linux quality job #2677 remains in progress; no timeout evidence yet | QUALITY/GATE | READY | 2026-08-23; await completed timing evidence |
| QG-FG-003-REGRESSION | P2 | Verify normative provider health states | Static audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; execution pending |

## Current execution baseline

Run #2677 is the first current multi-job run to provide durable new evidence:

- Local install smoke: **PASS**.
- Windows native active-state locality probe: **PASS**.
- Windows selected regressions: **FAIL — 4 failed, 50 passed, 2 warnings**.
- Linux keep-going full quality: **IN PROGRESS** at last verification.

The Windows failures are classified in `docs/quality-gate/2026-08-23-run-2677-windows-path-safety.md`. Two Linux-only locality failures were a Quality-owned lane-selection error and have been fixed in the workflow. The remaining executed failures are Backend-owned: Windows migration-clone fsync and a stale emergency-reserve test expectation.

## Ready slices

1. `QG-CI-TIMEOUT-HEADROOM` — classify real duration after #2677 Linux completes.
2. Continue `QG-RECENT-REGRESSION-SCAN` on newly landed FG-013/FG-015 storage changes.
3. Re-run/inspect the Windows lane after Quality selection fix; do not mask Backend failures.
