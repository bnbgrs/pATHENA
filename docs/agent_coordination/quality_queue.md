# pATHENA Quality Queue

Persistent queue for quality verification on `agent/pathena`.

Status values: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `STALE`.

| ID | Priority | Slice | Evidence | Ownership | Status | Last verification |
| --- | --- | --- | --- | --- | --- | --- |
| QG-2771-LOCAL-SMOKE-EXTRACTION-WIRING | P0 | Restore productive Core construction for Local install smoke | Run #2771 job `97258361925`: `athena-local-smoke --restart-cycles 1` fails in `AthenaApplication.__init__` because `ChatKnowledgeExtractionService` requires keyword-only `chat`, while application wiring omits `chat=self.chat`. Log: `docs/quality-gate/2026-08-23-run-2771-local-smoke-extraction-chat-integration.md` | BACKEND | BLOCKED | 2026-08-23; executed FAIL and current application/service constructors re-read |
| QG-2677-UI-PALLAS-SEGFAULT | P0 | Eliminate native Qt/PySide crash in PALLAS target binding | Linux #2677: pytest reached ~66% then SIGSEGV/-11 in `ascii_panel._bind_pallas_target()`; log `docs/quality-gate/2026-08-23-run-2677-ui-pallas-segfault.md` | UI | BLOCKED | 2026-08-23; executed fatal crash |
| QG-2097-MYPY-RESEARCH-MODELS | P0 | Resolve two mypy errors in `research/models.py` | #2677 reconfirmed `int` vs `object` comparison and loop-variable assignment conflict | BACKEND | BLOCKED | 2026-08-23; executed FAIL in #2677 |
| QG-2097-MYPY-RESEARCH-IDEMPOTENCY | P0 | Resolve three mypy unreachable errors in `research/idempotency.py` | #2677 reconfirmed unreachable checks for typed `Sequence` vs str/bytes/bytearray | BACKEND | BLOCKED | 2026-08-23; executed FAIL in #2677 |
| QG-2097-MYPY-SEMANTIC | P0 | Resolve two `_persisted_int()` mypy errors | #2677 reconfirmed `int(object)` overload plus `no-any-return` | BACKEND | BLOCKED | 2026-08-23; executed FAIL in #2677 |
| QG-2677-MYPY-MODEL-REGISTRY | P1 | Resolve ModelResourceProfile mypy narrowing errors | #2677: assignment conflict plus `Real`/`int` unreachable diagnostics | BACKEND | BLOCKED | 2026-08-23; executed FAIL |
| QG-2677-MYPY-MIGRATION-RECOVERY | P1 | Remove/reshape unreachable exhaustive recovery branch | #2677: unreachable final `else` in `migration_recovery.py` | BACKEND | BLOCKED | 2026-08-23; executed FAIL |
| QG-2677-MYPY-GROUNDED-CONTEXT | P1 | Propagate model revision while reconstructing context signature | #2677: missing `model_revision` in `ContextModelSignature` construction | BACKEND | BLOCKED | 2026-08-23; executed FAIL |
| QG-WIN-2677-MIGRATION-CLONE-FSYNC | P1 | Fix Windows migration-clone durable file flush | #2677 failed with EBADF on O_RDONLY fsync; current `_fsync_file()` uses O_RDWR. #2771 Windows storage regressions: 109 PASS including migration clone. | BACKEND + QUALITY/VERIFY | DONE | 2026-08-23; executed PASS in #2771 |
| QG-DB-PREFLIGHT-REPARSE-ANCESTOR | P1 | Reject Windows junction/reparse boundaries across active DB preflight | Current `recovery.py` still uses `Path.is_symlink()` for ancestors, DB and WAL/SHM while hardened storage uses `is_link_boundary()`; log `docs/quality-gate/2026-08-23-database-preflight-windows-reparse-ancestor.md` | BACKEND | BLOCKED | 2026-08-23; static defect reconfirmed on current lineage |
| QG-SEC-011-API-RUNTIME-REPARSE | P1 | Verify Core API runtime rejects Windows junction/reparse boundaries | #2771 Linux API runtime boundaries: 12 PASS; #2771 native Windows API runtime boundaries: 12 PASS | SECURITY + QUALITY/VERIFY | DONE | 2026-08-23; executed PASS on Linux and Windows |
| QG-FG-015-RESERVE-HEADROOM | P1 | Prevent reserve provisioning from creating EMERGENCY pressure | 100 GiB / 2.5 GiB free can provision 1 GiB and project ~1.5 GiB free below 2 GiB EMERGENCY threshold; current `ensure_reserve_if_safe()` still does not project post-allocation pressure; log `docs/quality-gate/2026-08-23-disk-pressure-reserve-provisioning-headroom.md` | BACKEND | BLOCKED | 2026-08-23; static defect reconfirmed |
| QG-WIN-2677-RESERVE-TEST-CONTRACT | P1 | Reconcile wrong-size reserve test with current error contract | #2677 expected `does not match`; later corrected tests are included in #2771 Windows storage suite | BACKEND/TEST + QUALITY/VERIFY | DONE | 2026-08-23; #2771 Windows storage 109 PASS |
| QG-STORAGE-BOOTSTRAP-PREFLIGHT-ORDER | P1 | Restore read-only preflight before mutating runtime layout | Current `StorageBootstrapService.start()` still calls `layout.start()` and creates migration root before `inspect_database_read_only()`; log `docs/quality-gate/2026-08-23-storage-bootstrap-preflight-order.md` | BACKEND | BLOCKED | 2026-08-23; current code re-read |
| QG-MIGRATION-JOURNAL-ANCESTOR-BOUNDARY | P1 | Verify Backend journal ancestor fix | #2771 Linux focused storage 157 PASS and Windows storage 109 PASS include migration journal | BACKEND + QUALITY/VERIFY | DONE | 2026-08-23; executed PASS Linux + Windows |
| QG-MIGRATION-CLONE-REPARSE-BOUNDARY | P1 | Verify clone reparse-boundary fix independently | #2771 Linux focused storage 157 PASS and Windows storage 109 PASS include migration clone after O_RDWR fsync fix | BACKEND + QUALITY/VERIFY | DONE | 2026-08-23; executed PASS Linux + Windows |
| QG-CI-SUPERSEDED-RUNS | P1 | Preserve useful active CI under continuous branch writes | `cancel-in-progress: false`; #2677 and #2771 demonstrate active runs survive newer pending heads | QUALITY/GATE | DONE | 2026-08-23 |
| QG-CI-FAILFAST-COVERAGE | P1 | Prove keep-going reaches later checks after earlier failures | #2677: Ruff FAIL -> mypy executed -> pytest executed | QUALITY/GATE | DONE | 2026-08-23 |
| QG-WIN-LOCALITY-SELECTION | P1 | Keep Linux mountinfo-only cases out of native Windows lane | #2771 native Windows `test_storage_locality.py -k windows`: 5 PASS, 3 deselected | QUALITY/GATE | DONE | 2026-08-23; executed PASS |
| QG-STORAGE-FOCUSED-LINUX-LANE | P1 | Decouple storage diagnostics from UI-native crashes | #2771 focused Linux storage regressions: 157 PASS; separate API runtime boundaries: 12 PASS | QUALITY/GATE | DONE | 2026-08-23; first executed lane PASS |
| QG-QUALITY-HARNESS-REGRESSION | P1 | Protect keep-going, concurrency, smoke and focused lanes | #2771 proves focused Linux and Windows lanes execute independently; Local smoke independently detected a real application composition regression. Full workflow-contract/full-gate result still pending. | QUALITY/GATE | IN_PROGRESS | 2026-08-23; partial executed verification |
| QG-FG-002-REGRESSION | P1 | Verify ModelRegistry / active-primary-model layer | Runtime tests passed in #2677; typing slice remains separately blocked | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23 |
| QG-FG-004-REGRESSION | P1 | Verify capability UNKNOWN vs UNSUPPORTED semantics | Relevant capability tests passed before #2677 crash | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23 |
| QG-FG-005-REGRESSION | P1 | Verify Context Builder source diversity | `test_context_builder_diversity.py` PASS in #2677 | QUALITY/READ-ONLY | DONE | 2026-08-23 |
| QG-FG-007-REGRESSION | P1 | Verify model-load ownership before auto-unload | `test_model_load_ownership.py` PASS in #2677 | QUALITY/READ-ONLY | DONE | 2026-08-23 |
| QG-FG-012-EXECUTION-GUARD | P1 | Verify protected-runtime execution guard | Static guard/test audit complete | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23; targeted runtime evidence pending |
| QG-FG-013-MIGRATION-SAFETY | P1 | Regression-watch clone-first migration stack | #2771 Linux focused storage 157 PASS and Windows storage 109 PASS, closing prior executor/fsync regressions; architectural Alembic-vs-custom decision remains outside gate verification | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23; executed storage stack PASS |
| QG-FG-014-REGRESSION | P1 | Verify active SQLite root locality | #2771 Linux locality/preflight tests PASS; native Windows locality probe PASS and Windows storage suite PASS. Separate DB-preflight reparse-boundary defect remains tracked. | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23 |
| QG-FG-015-REGRESSION | P1 | Regression-watch reserve/disk-pressure/write-gating/safe-mode policy | #2771 Linux focused storage and Windows storage suites PASS; projected reserve-headroom P1 remains a separate open product defect | QUALITY/READ-ONLY + GATE | IN_PROGRESS | 2026-08-23 |
| QG-RECENT-REGRESSION-SCAN | P1 | Risk-based scan of newest Backend/UI/Feature commits | #2771 surfaced productive extraction-service wiring regression; current newest storage durable-write commit reviewed read-only | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23 |
| QG-WINDOWS-GATE-PARITY | P2 | Native Windows platform-specific storage coverage | #2771 native locality probe PASS; locality selection 5 PASS; storage regressions 109 PASS; API runtime boundaries 12 PASS | QUALITY/GATE | DONE | 2026-08-23; executed on Windows Server 2025 |
| QG-PACKAGING-START-PATH | P2 | Verify install/start/restart/persistence path | #2677 smoke PASS, but #2771 regressed at productive Core construction due missing extraction `chat` dependency; packaging harness itself successfully built/installed and exposed the integration defect | QUALITY/GATE + BACKEND/BLOCKER | IN_PROGRESS | 2026-08-23; executed FAIL due QG-2771-LOCAL-SMOKE-EXTRACTION-WIRING |
| QG-CI-TIMEOUT-HEADROOM | P2 | Verify 10-minute keep-going gate headroom | #2677 quality ran ~7m33s but crashed before completion; #2771 full quality currently running | QUALITY/GATE | READY | 2026-08-23 |
| QG-STORAGE-LOCALITY-REGEX-WARNINGS | P2 | Remove Python invalid-escape SyntaxWarnings in storage locality tests | #2771 Linux and Windows both report invalid escape sequence `\(` at `tests/unit/test_storage_locality.py:53,74`; tests still pass | BACKEND/TEST | BLOCKED | 2026-08-23; executed warning on both OSes |
| QG-FG-003-REGRESSION | P2 | Verify normative provider health states | Relevant tests passed before #2677 crash | QUALITY/READ-ONLY | IN_PROGRESS | 2026-08-23 |

## Current execution baseline

Run #2771 (`32665417827`) on branch head `a683577c5e69b85308588b0b6b7b1675faae91ee` is the newest multi-job baseline with substantial executed evidence:

- Linux focused storage regressions: **PASS — 157 tests**, with 2 SyntaxWarnings in `test_storage_locality.py`.
- Linux API runtime path-boundary regressions: **PASS — 12 tests**.
- Native Windows locality probe: **PASS**.
- Windows deterministic locality regressions: **PASS — 5 tests, 3 deselected**, with the same 2 SyntaxWarnings.
- Windows selected storage regressions: **PASS — 109 tests**.
- Windows API runtime path-boundary regressions: **PASS — 12 tests**.
- Local install smoke: **FAIL** before Core start with missing `chat` argument in `ChatKnowledgeExtractionService` application wiring.
- Full Linux Spec/Ruff/mypy/pytest job: **IN PROGRESS** at the time of this queue refresh.

Permanent logs include:

- `docs/quality-gate/2026-08-23-run-2677-linux-full-gate.md`
- `docs/quality-gate/2026-08-23-run-2677-ui-pallas-segfault.md`
- `docs/quality-gate/2026-08-23-run-2677-windows-path-safety.md`
- `docs/quality-gate/2026-08-23-disk-pressure-reserve-provisioning-headroom.md`
- `docs/quality-gate/2026-08-23-storage-bootstrap-preflight-order.md`
- `docs/quality-gate/2026-08-23-database-preflight-windows-reparse-ancestor.md`
- `docs/quality-gate/2026-08-23-run-2771-local-smoke-extraction-chat-integration.md`

## Ready slices

1. `QG-2771-LOCAL-SMOKE-EXTRACTION-WIRING` — re-read application wiring after the Backend owner lands a fix; verify targeted construction/extraction tests and the next local-smoke execution.
2. Decode #2771 full Linux Quality job as soon as it finishes; split primary Ruff/mypy/pytest failures by ownership and update permanent logs.
3. `QG-CI-TIMEOUT-HEADROOM` — evaluate if #2771 full pytest reaches normal completion.
4. Continue `QG-RECENT-REGRESSION-SCAN` on new storage durable-publication/identity-hardening commits without mutating Backend product code.
5. Keep `QG-DB-PREFLIGHT-REPARSE-ANCESTOR`, `QG-FG-015-RESERVE-HEADROOM`, and `QG-STORAGE-BOOTSTRAP-PREFLIGHT-ORDER` blocked on Backend ownership while switching to independent verification work.
