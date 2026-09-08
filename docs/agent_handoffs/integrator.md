# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `84ab7ffc23771ff2be0392b0f8d3445fc6140a7d`; spec-core `56a6d0602361e0e7b3ad97e6ec52e2a35443dded`; backend `00b630e4915ec85abc08252d85e6403009b48858`; UI `b0c74459af0d6382f23106819f34778c86b6f18b`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Progress this run — unblock Jobs status-copy regression execution

No current worker product slice was READY at review time. Backend exact v41 Quality `34239590519` on `200543ac78754664c2559bcc9a998ce558d62ef6` was cancelled and the current Backend head is under Quality `34239827573 = pending`. UI current head `b0c74459af0d6382f23106819f34778c86b6f18b` is under Quality `34240229731 = pending`. Spec/Core is waiting for the Backend §75 durable Delta prerequisite. Error remains diagnostic-only under `ERR-0025`.

The hard progress rule therefore used path C on a repeatedly tooling-blocked UI regression. Current Develop still contained `pytest.importorskip("PySide6")` at module scope in `tests/unit/test_pathena_jobs_status_copy.py`, which allowed the complete Jobs status-copy contract to be skipped instead of failing when the canonical Qt test dependency is absent. The current UI worker independently removed exactly those three lines in commit `b0c74459af0d6382f23106819f34778c86b6f18b` without changing assertions or product code.

Develop commit `cbfe6d65e424f83b9c39d0d8ecf9af1aaffbf66a` applies exactly that bounded three-line deletion. Compare against the prior Develop head is ahead-only by one commit, one file, zero additions and three deletions. Existing Jobs status-copy assertions remain byte-for-byte unchanged. No product, scheduler, worker, persistence, Storage, Security, Recovery, packaging or Windows-runtime semantics changed.

## Verification state

- Source UI worker test commit: `b0c74459af0d6382f23106819f34778c86b6f18b`.
- UI canonical Quality: `34240229731 = pending` at review time.
- Develop unblocking commit: `cbfe6d65e424f83b9c39d0d8ecf9af1aaffbf66a`.
- Exact Develop compare: one modified file, only removal of module-level `pytest.importorskip("PySide6")`.
- No exact-current-Develop workflow run was associated yet; no global-green or promotion-ready claim is made.

## Error / Alpha-Beta / UI state

- ERR-0025 remains IN_PROGRESS. Backend now has exact Ruff/mypy/pytest diagnostics on its v41 lineage; speculative blame remains forbidden.
- ERR-0023 remains FIXED_PENDING_VERIFY until exact Develop canonical green evidence exists.
- Spec/Core §75 remains blocked on an exact-green integrated Backend durable Delta prerequisite.
- All eleven screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim is made.
- `ALPHA_BETA_PROGRESS.md` was read. No destructive whole-file rewrite was performed because the connector returned only truncated content for the large tracker.

## Next integration order

1. Consume Backend Quality `34239827573` and UI Quality `34240229731` when completed.
2. If Backend becomes exact-green, integrate the bounded §75 durable Delta prerequisite before Core implements `enqueue_delta` composition.
3. If UI becomes exact-green, independently review the remaining two Jobs test-alignment commits before importing any additional test-only changes; do not weaken assertions or reintroduce skips.
4. Obtain exact-current-Develop canonical Quality for the descendant carrying `cbfe6d65e424f83b9c39d0d8ecf9af1aaffbf66a`.
5. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
