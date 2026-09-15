# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`; exact canonical Quality `34954990041 = SUCCESS`.
- `postmerge/errors@1fcb524ec9346ca66ba31c699c3d79cb5538d8a1` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; previously exact green; no new current-SHA failure evidence.
- `postmerge/backend@649b735ca2cc891b28d3b599d28451bd551d1328`; exact Backend Focused `34969141337 = SUCCESS`; exact canonical Quality `34969141276 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no new current-SHA canonical/focused product assertion evidence established by the Error worker.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
No Error-worker closure evidence. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0072 — P1 — Backend durable-service canonical test uses nonexistent priority
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@649b735c...`, canonical Quality `34969141276`, Python pytest. `tests/unit/test_backup_verify_durable_service.py::test_deep_verify_persists_validated_payload_once` fails before exercising persistence because it requests `JobPriority.HIGH`; canonical `JobPriority` exposes `DATA_SAFETY`, `INTERACTIVE`, `TIME_CRITICAL`, `NORMAL`, `BACKGROUND`, `MAINTENANCE`, not `HIGH`. Backend Focused remains green, so this is a canonical-suite coverage gap exposed by the new test, not a release-guard regression. Minimal owner fix: use an existing priority appropriate to the test and assert that same canonical enum value; do not add an alias merely to satisfy the test.

### ERR-0073 — P1 — Backend durable-service delegation test supplies invalid backup.create payload
Status: `OPEN`
Owner: Backend.
Exact reproduction: same SHA/run. `tests/unit/test_backup_verify_durable_service.py::test_non_deep_verify_job_delegates_to_canonical_service_validation` calls `service.create(job_type="backup.create")` without the canonical `backup.create` requested-scope/configuration contract, so delegation correctly reaches canonical validation and raises `InvalidJobPayloadError: backup.create requested_scope has unexpected or missing fields.` Minimal owner fix: make the delegation test supply a valid canonical `backup.create` payload, preserving fail-closed validation; do not weaken `validate_builtin_job_payload` or service validation.

## IN_PROGRESS

### ERR-0067 — P2 — prior typography-token contract mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; reopen only if current exact canonical/focused evidence reproduces it.

### ERR-0068 — P2 — prior offline-readiness copy mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; reopen only from current exact canonical/focused evidence.

### ERR-0069 — P2 — prior shell-density composer geometry mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; do not infer it from a visual-verdict failure.

## FIXED / HELD CLOSED

### Develop current successor
Status: `FIXED`
Current Develop `03157f15...` completed exact canonical Quality `34954990041 = SUCCESS`. The integrated deep-verify CONTROL route introduces no current exact-SHA failure cluster.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No current exact evidence reproduces the manifest-truth defect. Capture-derived manifest truth, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics remain unchanged.

### ERR-0070 — P2 — Core focused selector contract drift after Research expansion
Status: `FIXED`
No current exact Spec/Core regression evidence.

### ERR-0071 — P2 — focused mypy/package-resolution candidate
Status: `FIXED`
No current exact Spec/Core regression evidence.

- `ERR-0063` — `FIXED`.
- `ERR-0064` — `FIXED`.
- `ERR-0065` — `STALE`.
- `ERR-0066` — `FIXED`.
- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards

On backend `649b735c...`, Linux storage regressions, local Core/API restart + pypdf packaging, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are green. The canonical failure is isolated to two new durable-service unit tests. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Backend owns `ERR-0072` and `ERR-0073`: fix the two test-contract errors without changing canonical priority or backup validation semantics, then rerun focused + canonical on the resulting exact SHA.
2. Error worker must consume the next Backend exact-SHA evidence; close these IDs only on terminal green evidence or reclassify from the actual new failure signature.
3. Consume any new current-SHA UI canonical/focused evidence; keep `ERR-0054` UI/Visual-Review-owned and `ERR-0059` closed absent a new exact regression.
4. Keep Develop and Spec/Core green clusters closed unless a new exact-SHA regression reproduces them.
