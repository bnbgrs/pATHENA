# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@e16a4d14f367f29e29deb794d0e1581b41226a49`.
- Error branch mutation lineage remains `postmerge/errors` only.
- History-preserving NON-FORCE synchronization merge: `bfca8cbc3cb4abfda3858e5c23fc9095a7f90506`, parents `caccfcc8fdbd8add56d665ba0ef5e1e69d4b53f3` and `e16a4d14f367f29e29deb794d0e1581b41226a49`.
- Current Spec/Core head reviewed: `d64c9fdfafe026e272857d36bd7a8aa90b859f55`.
- Current Backend head reviewed: `d6fd803cae4e444f6cdc193d49c93197b457604e`.
- Current UI head reviewed: `aa9a705bac548753be4adc0ee27a998c981dc93e`.
- Required handoffs and current canonical workflow state were reviewed before mutation.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0020`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0021`.
- OPEN: none.
- BLOCKED: none.

## ERR-0021 — Develop exact-SHA full-pytest failure after UI-GAP-0071 integration

- Severity: P1 until exact failing assertion is classified.
- Status: `IN_PROGRESS`.
- Exact evidence: canonical ATHENA Quality Gate `34170211496` on exact Develop SHA `d40dc421585193db7bda039d113d7d81ccfb9c03` completed `failure`.
- Gate split: Local install smoke PASS; Windows path safety PASS; Linux storage regressions PASS; specification Validator PASS; Ruff PASS; mypy PASS; full pytest FAIL; canonical result enforcement FAIL.
- Diagnostics artifact: `canonical-quality-diagnostics-d40dc421585193db7bda039d113d7d81ccfb9c03`, artifact id `10035722162`, retained and unexpired when reviewed.
- Repro: exact canonical CI on `d40dc421585193db7bda039d113d7d81ccfb9c03`; failure is isolated to the full pytest step. The connector exposes the artifact metadata but not the traceback payload, so no assertion/test-path or product-vs-harness root cause is invented.
- Root cause: not finalized yet. This is a new exact Develop signal and is not deduplicated into a historical crash class without matching signature evidence.
- Current-head relation: current Develop `e16a4d14f367f29e29deb794d0e1581b41226a49` descends from the failed Develop lineage, but no exact completed canonical run on `e16a4d14f367f29e29deb794d0e1581b41226a49` has yet been established. Therefore ERR-0021 is not marked FIXED or STALE.
- Active-worker verification path: current UI head `aa9a705bac548753be4adc0ee27a998c981dc93e` runs Quality `34170876155`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy are already PASS and full pytest is in progress. Current Backend head `d6fd803cae4e444f6cdc193d49c93197b457604e` runs Quality `34170446906` with the same completed non-pytest gates green and full pytest in progress. These are concrete successor checks, not assumed fixes.
- Files: exact failing file is not yet evidenced; do not mutate product or harness code until traceback/diagnostic evidence or a byte-identical verified corrective successor identifies the cause.
- Integrator handoff: do not call Develop promotion-ready while ERR-0021 remains unresolved. Consume exact diagnostics or successor Quality results and finalize root cause on the next run rather than repeating an unknown hypothesis.

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

- Spec/Core `d64c9fdfafe026e272857d36bd7a8aa90b859f55`: canonical Quality `34169356670 = success` on the exact current worker head.
- Backend `d6fd803cae4e444f6cdc193d49c93197b457604e`: Quality `34170446906` in progress; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest in progress.
- UI `aa9a705bac548753be4adc0ee27a998c981dc93e`: Quality `34170876155` in progress; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest in progress.
- Develop exact SHA `d40dc421585193db7bda039d113d7d81ccfb9c03`: Quality `34170211496 = failure`, isolated to full pytest. Current Develop `e16a4d14f367f29e29deb794d0e1581b41226a49` has no exact completed canonical success established in this scan.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.
- `ERR-0004` remains FIXED; all observed current Ruff steps are green.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
