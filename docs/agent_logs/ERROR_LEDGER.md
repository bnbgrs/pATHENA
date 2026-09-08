# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`.
- Error branch mutation lineage remains `postmerge/errors` only.
- History-preserving NON-FORCE synchronization merge: `76d095bb747aa9f006174e66fa88423e9e7d309b`, parents `c487df792b0aaa6af9a4a48a848b07bfd20a8eef` and `eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`.
- Current Spec/Core head reviewed: `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`.
- Current Backend head reviewed: `076a0d1209fe1cb30c6cfe7f6735a39158036c28`.
- Current UI head reviewed: `dd7384f8f39cb9b61c0fa1a8d205492b584dd3de`.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- OPEN: none.
- IN_PROGRESS: none.
- BLOCKED: none.

## ERR-0022 — Spec/Core Ruff import-grouping failure

- Severity: P2.
- Status: `FIXED`.
- Failing evidence: canonical Quality `34173373152` on Spec/Core `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`; Local install, Windows path safety, Linux storage, Validator, mypy and full pytest passed; Ruff alone failed.
- Root cause: harness import grouping in `tests/unit/test_exhaustive_research_large_archive.py` violated Ruff formatting/import-order expectations.
- Fix SHA: `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5` (`fix(core): satisfy Ruff import grouping for large archive acceptance`).
- Verification: exact fix SHA passed canonical ATHENA Quality Gate `34176070442 = success`.
- Classification: harness-only; no product defect established.
- Integrator handoff: ERR-0022 hold cleared for exact Spec/Core `d97ffca...`; this does not imply global Develop promotion readiness.

## ERR-0021 — Jobs status-copy harness leaked constructor refresh suppression

- Severity: P1 during diagnosis; resolved harness-only.
- Status: `FIXED`.
- Failing evidence: Develop `4e18f75beeaa1c5b57bca28dcad5a062ac498051` Quality `34166952158`, Develop `d40dc421585193db7bda039d113d7d81ccfb9c03` Quality `34170211496`, Backend `d6fd803cae4e444f6cdc193d49c93197b457604e` Quality `34170446906`, and UI `aa9a705bac548753be4adc0ee27a998c981dc93e` Quality `34170876155` all exhibited a full-pytest-only failure pattern while non-pytest canonical gates passed.
- Final isolation: UI parent `dd052e7d3fcbbec80653d472b7870ef019a96502` failed canonical Quality `34174017940` specifically at full pytest while Validator, Ruff, mypy, Local install, Windows path safety and Linux storage passed. Its direct child `352b4c72c39d5cafe866c604a050a1b93df71940` changed only `tests/unit/test_pathena_jobs_status_copy.py` by saving `JobsWorkspace.refresh` before constructor suppression and restoring it immediately after `JobsWorkspace()` construction.
- Root cause: `_workspace()` used `monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)` to suppress constructor refresh but left that suppression active for the rest of each test. The helper therefore altered post-construction behavior beyond its intended setup boundary and contaminated full-suite semantics.
- Fix SHA: `352b4c72c39d5cafe866c604a050a1b93df71940` (`test(ui): restore Jobs refresh after constructor suppression`).
- Verification: exact direct successor passed canonical ATHENA Quality Gate `34174030199 = success`. Current Develop `eeaf49fa...` contains the corrected helper blob (`tests/unit/test_pathena_jobs_status_copy.py` blob `a1ba67fdf864f49945a7dd5c6e3bfe9b981d09bd`).
- Classification: harness defect, not product defect. No product guard, assertion, Security/Storage/Recovery/Windows behavior, or runtime semantics were weakened.
- Integrator handoff: ERR-0021 promotion hold cleared as a specific error. Current Develop still requires its own exact completed canonical success before any global promotion-ready claim.

## ERR-0020 — Exhaustive research resume harness erased per-source identity at synthesis

- Severity: P2.
- Status: `FIXED`.
- Root cause: fixture preserved source identity in MAP but collapsed reduce/final synthesis output to one generic Finding; production persistence/restart behavior was not implicated.
- Minimal fix: preserve real phase dispatch, extract `resume-source-\d+` anywhere in request text and carry source identity through synthesis without product or assertion changes.
- Error fix commit: `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9`.
- Verification: Spec/Core `80915e1e8c7dff42fc998e9035df41273bdb08ca` contained the byte-identical fixed test blob and passed canonical Quality `34166094972 = success`.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact green `33804193396`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; later exact runs succeeded; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift; exact canonical Quality `34110957854 = success`.
- All other `ERR-0001`..`ERR-0013`, `ERR-0015`..`ERR-0018` remain FIXED with prior evidence unchanged.

## Current scan evidence — 2026-09-08

- Spec/Core `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`: canonical Quality `34176070442 = success`; closes ERR-0022.
- UI `dd052e7d3fcbbec80653d472b7870ef019a96502`: Quality `34174017940 = failure`, full-pytest-only.
- UI direct successor `352b4c72c39d5cafe866c604a050a1b93df71940`: Quality `34174030199 = success`; only clearing delta is restoration of `JobsWorkspace.refresh` immediately after constructor suppression; closes ERR-0021.
- Current Develop `eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`: corrected Jobs helper is present, but no exact pull-request-triggered canonical workflow run is currently associated with this exact SHA; therefore no global promotion-ready claim.
- Backend previous `c964506791611da78dd3959aa64c12b2614e253b`: Quality `34173582002 = failure`, full-pytest-only and now explained as an ERR-0021 shared-harness reproduction rather than a separate Backend defect.
- Current Backend `076a0d1209fe1cb30c6cfe7f6735a39158036c28`: Quality `34177086068` in progress; no new primary failure allocated from an incomplete run.
- Current UI `dd7384f8f39cb9b61c0fa1a8d205492b584dd3de`: no new exact primary error established in this scan.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
