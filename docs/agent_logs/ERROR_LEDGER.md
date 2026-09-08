# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@e9c931f5ae00e2db70e8a42ac6110b78cf35b789`.
- Error branch mutation lineage remains `postmerge/errors` only.
- History-preserving NON-FORCE synchronization merge: `196360097cbb0e6b457231862b64972b4fde9629`, parents `921940cc2c5b76b24f3622201da473421a065c9a` and `e9c931f5ae00e2db70e8a42ac6110b78cf35b789`.
- Current Spec/Core head reviewed: `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`.
- Current Backend head reviewed: `c964506791611da78dd3959aa64c12b2614e253b`.
- Current UI head reviewed: `352b4c72c39d5cafe866c604a050a1b93df71940`.
- Required handoffs and current canonical workflow state were reviewed before mutation.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0020`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0021`, `ERR-0022`.
- OPEN: none.
- BLOCKED: none.

## ERR-0022 — Spec/Core exact-SHA Ruff-only failure with full pytest green

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: canonical ATHENA Quality Gate `34173373152` on exact Spec/Core SHA `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823` completed `failure`.
- Gate split: Local install smoke PASS; Windows path safety PASS; Linux storage regressions PASS; specification Validator PASS; mypy PASS; full pytest PASS; Ruff FAIL; canonical result enforcement FAIL.
- Diagnostics artifact: `canonical-quality-diagnostics-0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`, artifact id `10037037421`, retained/unexpired when reviewed.
- Exact changed file at head: `tests/unit/test_exhaustive_research_large_archive.py`; head commit only changes `source_count=12` to `40` and the matching expected artifact count. The immediately preceding commit `527ee5e1b23247b8babbb9c5aa86e572d8eea505` also modified the same harness and its Quality run `34173325137` was cancelled, so no green parent isolates the precise lint-introducing line.
- Root cause: exact Ruff rule/diagnostic remains pending because the connector exposes artifact metadata but not the zip payload. Do not guess a Ruff code or mutate the harness without the exact diagnostic or an owner successor that concretely demonstrates the correction.
- Product-vs-harness classification: harness-owned by changed-file evidence; full pytest is green, so no product regression is established by this signal.
- Integrator handoff: hold Spec/Core `0d0fe488...` from READY. The Spec/Core owner should minimally correct the exact Ruff diagnostic in `tests/unit/test_exhaustive_research_large_archive.py`, then verify Ruff plus focused large-archive test and canonical Quality before ERR-0022 can be marked FIXED.

## ERR-0021 — shared-baseline exact-SHA full-pytest failure

- Severity: P1 until the exact failing assertion is classified.
- Status: `IN_PROGRESS`.
- Primary exact evidence: canonical ATHENA Quality Gate `34170211496` on exact Develop SHA `d40dc421585193db7bda039d113d7d81ccfb9c03` completed `failure` with Local install smoke PASS, Windows path safety PASS, Linux storage regressions PASS, specification Validator PASS, Ruff PASS, mypy PASS and full pytest FAIL.
- Earlier lineage evidence: Develop SHA `4e18f75beeaa1c5b57bca28dcad5a062ac498051` already reproduced the same gate split in Quality `34166952158`: Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest FAIL. Therefore UI-GAP-0071 is not established as the primary cause and the issue predates that integration.
- Cross-worker reproduction: Backend SHA `d6fd803cae4e444f6cdc193d49c93197b457604e` reproduced the same full-pytest-only failure in Quality `34170446906`; UI SHA `aa9a705bac548753be4adc0ee27a998c981dc93e` also completed Quality `34170876155 = failure`. These worker failures inherit the shared baseline signal and are not opened as separate Backend/UI errors absent distinct traceback evidence.
- Diagnostics artifact: `canonical-quality-diagnostics-d40dc421585193db7bda039d113d7d81ccfb9c03`, artifact id `10035722162`, size 10080 bytes, retained and unexpired when reviewed. The connector exposes artifact metadata but does not expose the zip traceback payload, so no assertion/test path is fabricated.
- Root-cause scope: narrowed to a shared Develop/full-suite failure introduced no later than `4e18f75beeaa1c5b57bca28dcad5a062ac498051`; neither UI-GAP-0071 nor the contemporaneous Backend/UI owned slices are supported as primary causes by current evidence. Exact test/assertion and product-vs-harness classification remain pending.
- Current-head relation: current Develop `e9c931f5ae00e2db70e8a42ac6110b78cf35b789` descends from the failed Develop lineage but has no exact completed canonical workflow run established. Therefore ERR-0021 is not marked FIXED or STALE.
- Active verification: current Backend `c964506791611da78dd3959aa64c12b2614e253b` Quality `34173582002` and UI `352b4c72c39d5cafe866c604a050a1b93df71940` Quality `34174030199` remain in progress. Current Spec/Core `0d0fe488...` is not a clean ERR-0021 verifier because its full pytest passed but Quality failed independently on new Ruff error ERR-0022.
- Files: exact failing pytest file remains unevidenced; do not mutate product or harness code until traceback evidence or a concrete corrective successor identifies the responsible path.
- Integrator handoff: hold promotion-ready claims for Develop while ERR-0021 remains unresolved. The next run must consume current Backend/UI exact completions and either finalize the failing assertion/root cause or verify a concrete corrective successor.

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

- Develop `4e18f75beeaa1c5b57bca28dcad5a062ac498051`: Quality `34166952158 = failure`, isolated to full pytest.
- Develop `d40dc421585193db7bda039d113d7d81ccfb9c03`: Quality `34170211496 = failure`, isolated to full pytest.
- Backend `d6fd803cae4e444f6cdc193d49c93197b457604e`: Quality `34170446906 = failure`, same full-pytest-only gate split.
- UI `aa9a705bac548753be4adc0ee27a998c981dc93e`: Quality `34170876155 = failure`.
- Spec/Core `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`: Quality `34173373152 = failure`; Ruff FAIL while full pytest PASS, opened separately as ERR-0022.
- Current Backend `c964506791611da78dd3959aa64c12b2614e253b`: Quality `34173582002` in progress.
- Current UI `352b4c72c39d5cafe866c604a050a1b93df71940`: Quality `34174030199` in progress.
- Current Develop `e9c931f5ae00e2db70e8a42ac6110b78cf35b789`: no exact completed canonical run established.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.
- `ERR-0004` remains FIXED; ERR-0022 is a distinct new Ruff signal, not a recurrence of the historical startup/readiness B010/I001 failure absent exact matching rule evidence.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
