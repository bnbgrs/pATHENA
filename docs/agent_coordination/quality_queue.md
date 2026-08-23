# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2677-UI-PALLAS-SEGFAULT | P0 | Eliminate native Qt/PySide crash in PALLAS target binding | Linux run #2677: pytest collected 3897 tests, reached ~66%, then SIGSEGV/-11 in `ascii_panel._bind_pallas_target()` during `test_pathena_command_palette_presentation.py`; log `docs/quality-gate/2026-08-23-run-2677-ui-pallas-segfault.md` | UI | BLOCKED | 2026-08-23; executed fatal crash, current crash path re-read |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve two mypy errors in `research/models.py` | Run #2677 reconfirmed 2 errors: `int` vs `object` comparison and loop-variable assignment type conflict | BACKEND | BLOCKED | 2026-08-23; executed FAIL in #2677 |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve three mypy unreachable errors in `research/idempotency.py` | Run #2677 reconfirmed 3 unreachable checks for typed `Sequence` vs str/bytes/bytearray | BACKEND | BLOCKED | 2026-08-23; executed FAIL in #2677 |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve two `_persisted_int()` mypy errors | Run #2677 reconfirmed `int(object)` call-overload plus `no-any-return` | BACKEND | BLOCKED | 2026-08-23; executed FAIL in #2677 |
| QG-2677-MYPY-MODEL-REGISTRY | P1 | Resolve ModelResourceProfile mypy narrowing errors | Run #2677: assignment type conflict plus `Real`/`int` unreachable diagnostics in `src/athena/model/registry.py` | BACKEND | BLOCKED | 2026-08-23; executed FAIL and current code re-read |
| QG-2677-MYPY-MIGRATION-RECOVERY | P1 | Remove/reshape unreachable exhaustive recovery branch | Run #2677: unreachable final `else` in `migration_recovery.py`; current enum-exhaustive branch still present | BACKEND | BLOCKED | 2026-08-23; executed FAIL and current code re-read |
| QG-2677-MYPY-GROUNDED-CONTEXT | P1 | Propagate required model revision while reconstructing context signature | Run #2677: missing `model_revision` argument in `ContextModelSignature` construction | BACKEND | BLOCKED | 2026-08-23; executed FAIL and current constructor re-read |
| QG-WIN-2677-MIGRATION-CLONE-FSYNC | P1 | Fix Windows migration-clone durable file flush | Run #2677 Windows: `_fsync_file()` on `O_RDONLY` descriptor -> `OSError [Errno 9] Bad file descriptor`; log `docs/quality-gate/2026-08-23-run-2677-windows-path-safety.md` | BACKEND | BLOCKED | 2026-08-23; executed FAIL on Windows Server 2025 |
| QG-DB-PREFLIGHT-REPARSE-ANCESTOR | P1 | Reject Windows junction/reparse ancestors before active DB preflight/open | `recovery.py::_reject_symlink_ancestors()` uses `Path.is_symlink()` only while hardened storage primitives use `is_link_boundary()`; affects writer/read-only/safe-mode startup. Log: `docs/quality-gate/2026-08-23-database-preflight-windows-reparse-ancestor.md` | BACKEND | BLOCKED | 2026-08-23; static defect confirmed on HEAD `d6b90f16...` |
| QG-SEC-011-API-RUNTIME-REPARSE | P1 | Verify Core API runtime rejects Windows junction/reparse boundaries | Security fix `124fe5d0...` replaced symlink-only runtime-root/ancestor checks with shared `is_link_boundary()`; test `f1f7e60d...` adds deterministic reparse-boundary simulation. Security queue SEC-011 remains FIXED, not VERIFIED. | SECURITY + QUALITY/VERIFY | READY | 2026-08-23; static post-fix review only, no executed test claimed |
| QG-FG-015-RESERVE-HEADROOM | P1 | Prevent reserve provisioning from creating EMERGENCY pressure | 100 GiB / 2.5 GiB free permits 1 GiB reserve allocation and projects ~1.5 GiB free below 2 GiB EMERGENCY threshold; log `docs/quality-gate/2026-08-23-disk-pressure-reserve-provisioning-headroom.md` | BACKEND | BLOCKED | 2026-08-23; current implementation re-read and defect remains |
| QG-WIN-2677-RESERVE-TEST-CONTRACT | P1 | Reconcile wrong-size reserve test with current error contract | Run #2677: expected `does not match`, actual exact-size invariant message | BACKEND/TEST | BLOCKED | 2026-08-23; executed Windows failure |
| QG-STORAGE-BOOTSTRAP-PREFLIGHT-ORDER | P1 | Restore read-only preflight before mutating runtime layout | `StorageBootstrapService.start()` runs `layout.start()` and creates migration root before `inspect_database_read_only()`; log `docs/quality-gate/2026-08-23-storage-bootstrap-preflight-order.md` | BACKEND | BLOCKED | 2026-08-23; current code statically verified |
| QG-MIGRATION-JOURNAL-ANCESTOR-BOUNDARY | P1 | Verify Backend journal ancestor fix | Current code validates ancestors before I/O, uses link-boundary checks, no-follow where available, and handle/path identity | BACKEND + QUALITY/VERIFY | IN_PROGRESS | 2026-08-23; #2677 Linux journal suite PASS; focused Windows rerun pending |
| QG-MIGRATION-CLONE-REPARSE-BOUNDARY | P1 | Verify reparse-boundary fix independently of Windows fsync defect | Linux #2677 clone tests PASS; Windows ordinary snapshot path fails earlier/later at fsync | BACKEND + QUALITY/VERIFY | IN_PROGRESS | 2026-08-23; Windows reparse execution still entangled with fsync defect |
| QG-CI-SUPERSEDED-RUNS | P1 | Preserve useful active CI under continuous branch writes | `cancel-in-progress: false`; #2677 completed while newer pending runs were superseded | QUALITY/GATE | DONE | 2026-08-23; active-run survival proven by completed #2677 |
| QG-CI-FAILFAST-COVERAGE | P1 | Prove keep-going reaches later checks after earlier failures | #2677: Ruff FAIL -> mypy executed and FAIL -> pytest executed and reached 66% before native crash | QUALITY/GATE | DONE | 2026-08-23; executed behavior verified |
| QG-WIN-LOCALITY-SELECTION | P1 | Keep Linux mountinfo-only cases out of native Windows lane | #2677 produced two false Windows failures; workflow now runs `test_storage_locality.py -k windows` separately | QUALITY/GATE | IN_PROGRESS | 2026-08-23; harness fix landed, executed rerun pending |
| QG-STORAGE-FOCUSED-LINUX-LANE | P1 | Decouple FG-013/FG-015 diagnostics from UI-native crashes | Dedicated Linux storage job now covers migration, reserve, pressure DB, read-only DB, safe mode and bootstrap tests | QUALITY/GATE | IN_PROGRESS | 2026-08-23; workflow/contract implemented, first executed run pending |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Protect keep-going, concurrency, smoke and focused storage lanes | Workflow-contract tests cover Linux storage lane and Windows storage/locality selection including pressure/read-only/safe-mode tests | QUALITY/GATE | IN_PROGRESS | 2026-08-23; Quality-owned I001 from #2677 fixed; current execution pending |
| QG-FG-002-REGRESSION | P1 | Verify ModelRegistry / active-primary-model layer | Runtime tests passed in #2677, but mypy for registry is red | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; functional tests seen PASS, typing slice BLOCKED separately |
| QG-FG-004-REGRESSION | P1 | Verify capability UNKNOWN vs UNSUPPORTED semantics | Relevant capability tests passed before #2677 crash | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; full-suite completion still blocked by UI crash |
| QG-FG-005-REGRESSION | P1 | Verify Context Builder source diversity | `test_context_builder_diversity.py` PASS in #2677 | QUALITY/READ-ONLY | DONE | 2026-08-23; executed PASS |
| QG-FG-007-REGRESSION | P1 | Verify model-load ownership before auto-unload | `test_model_load_ownership.py` PASS in #2677 | QUALITY/READ-ONLY | DONE | 2026-08-23; executed PASS |
| QG-FG-012-EXECUTION-GUARD | P1 | Verify protected-runtime execution guard | Static guard/test audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; targeted runtime evidence still pending |
| QG-FG-013-MIGRATION-SAFETY | P1 | Regression-watch clone-first migration stack | #2677 Linux: activation/clone/coordinator/journal/lock/plan/recovery/safety passed; executor had one failure. Windows clone has fsync failure. | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; focused Linux/Windows lanes expanded |
| QG-FG-014-REGRESSION | P1 | Verify active SQLite root locality | #2677 native Windows locality probe PASS; Linux preflight/locality tests ran before crash; separate local reparse-ancestor gap now tracked | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; deterministic Windows rerun pending |
| QG-FG-015-REGRESSION | P1 | Regression-watch emergency reserve/disk-pressure/write-gating/safe-mode policy | #2677 disk-pressure tests PASS; reserve suite one stale-contract FAIL. `PressureGuardedSQLiteDatabase`, read-only DB and `StorageSafeModeService` tests are now in focused Linux/Windows lanes. | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; projected reserve-headroom P1 remains open |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of newest Backend/UI/Feature commits | Found reserve-headroom, bootstrap-order and database-preflight reparse P1s; migration-recovery ancestor issue was fixed in parallel before handoff | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; no foreign product code mutated |
| QG-WINDOWS-GATE-PARITY | P2 | Focus native Windows execution on platform-specific storage boundaries | #2677 established real Windows baseline; lane now includes migration, reserve, pressure DB, read-only DB and safe-mode tests | QUALITY/GATE | IN_PROGRESS | 2026-08-23; rerun pending |
| QG-PACKAGING-START-PATH | P2 | Verify install/start/restart/persistence path | #2677 `Local install smoke` PASS | QUALITY/GATE | DONE | 2026-08-23; job `97251316671` |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify 10-minute keep-going gate headroom | #2677 quality step ran ~7m33s but pytest crashed at ~66%; cannot prove full-suite headroom | QUALITY/GATE | READY | 2026-08-23; retain 10m until complete-run timing exists |
| QG-FG-003-REGRESSION | P2 | Verify normative provider health states | Relevant model-domain/provider tests passed before #2677 crash | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; full-suite completion unavailable |

## Current execution baseline

Run #2677 (`32662756936`) is the latest fully decoded multi-job baseline for a concrete branch head:

- Specification validator: **PASS — 63/63**.
- Ruff: **FAIL — 14 errors**; one was Quality-owned and has been fixed, the remaining reported errors are UI-owned.
- mypy: **FAIL — 24 errors in 15 files**; Backend and UI slices are separated above/in the incident log.
- pytest: **FAIL — native SIGSEGV / exit -11 after ~66% of 3897 collected tests**.
- Keep-going behavior: **VERIFIED**; pytest ran after both Ruff and mypy failures.
- Local install smoke: **PASS**.
- Windows native locality probe: **PASS**.
- Windows selected regressions: **FAIL — 4 failed, 50 passed, 2 warnings**, with two Quality-owned test-selection false failures now fixed and two Backend-owned failures remaining.

Permanent logs:

- `docs/quality-gate/2026-08-23-run-2677-linux-full-gate.md`
- `docs/quality-gate/2026-08-23-run-2677-ui-pallas-segfault.md`
- `docs/quality-gate/2026-08-23-run-2677-windows-path-safety.md`
- `docs/quality-gate/2026-08-23-disk-pressure-reserve-provisioning-headroom.md`
- `docs/quality-gate/2026-08-23-storage-bootstrap-preflight-order.md`
- `docs/quality-gate/2026-08-23-database-preflight-windows-reparse-ancestor.md`

## Ready slices

1. `QG-SEC-011-API-RUNTIME-REPARSE` — run focused `test_api_runtime_boundaries.py` on Linux and native Windows; confirm junction/reparse behavior before SEC-011 moves to VERIFIED.
2. `QG-CI-TIMEOUT-HEADROOM` — evaluate only after a full pytest run reaches normal completion.
3. `QG-STORAGE-FOCUSED-LINUX-LANE` — inspect first completed focused-storage job for migration/reserve/pressure/safe-mode failures without UI-crash interference.
4. `QG-WIN-LOCALITY-SELECTION` / `QG-WINDOWS-GATE-PARITY` — inspect first completed Windows rerun after lane split; do not mask Backend fsync failures.
5. Continue `QG-RECENT-REGRESSION-SCAN` as FG-013/FG-015 storage code lands.
