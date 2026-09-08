# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `e6ed6eba803e4084b5e5aeaa2ad576dccdaf9961`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `4dd4fecf704302457e3aaf6219851c5cd28923c1`; spec-core `4cb7b137164e411ba02d83ce53926aa615cf3a36`; backend `44e682048fd0e7fa990c46b385931a954ecc0189`; UI `59aa42824d4e7475af29403fb6bbc78fd9c58d08`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite, auto-merge or main promotion was used.

## Progress this run — Beta Research §65 explicit post-cancel partial result

Spec/Core became READY during independent review: exact current worker head `4cb7b137164e411ba02d83ce53926aa615cf3a36` has canonical ATHENA Quality Gate `34255843664 = success`. The worker lineage is highly divergent, so only the bounded §65 product/test blobs were transplanted; unrelated Personal Memory and cancellation-test files were not imported.

Develop product commit `eeb8a9f3c97c0cacc00c55af8d8a3260d1edccb0` adds `ResearchPartialResultService`. It is opt-in and post-cancel only: the job must be durable `research.exhaustive` in `CANCELLED`, its Research scope must remain durable `PARTIAL`, and an existing incompatible/final result fails closed. The service reuses only completed immutable synthesis artifacts, preserves exact artifact identity/hash/content and SourceAnalysis-artifact provenance, persists explicit `partial=true`, `result_status=partial`, `completion_reason=cancelled`, real coverage/problem-source fields, nullable `final_artifact_id`, and remains idempotent for the same partial representation. It makes no model call and does not fabricate missing evidence or a completed Final Result.

Develop acceptance commit `e10befce38259f15f2e06f06ab7b1ae38356305f` adds `tests/unit/test_exhaustive_research_partial_result.py`, byte-identical to the exact-green Core worker test blob. The acceptance drives four real captured Sources through processing/analysis, commits a real REDUCE artifact, cancels through the real Research worker, explicitly creates the partial report, checks confirmed artifact hash/provenance and real coverage, retains `PARTIAL`/`CANCELLED`, proves idempotency, and asserts no completed FINAL artifact exists. No Skip/XFail or assertion weakening is present.

Local exact-Develop execution was attempted but the runtime could not resolve `github.com`, so no local pass is fabricated. No automatic workflow run is currently associated with exact Develop commit `e10befce38259f15f2e06f06ab7b1ae38356305f`; global-green/promotion-ready is therefore not claimed. Verification evidence is the exact-green worker head plus byte-identical bounded product/test contents.

## Current quality/error state

- Exact Spec/Core head `4cb7b137164e411ba02d83ce53926aa615cf3a36`: Quality `34255843664 = SUCCESS`.
- Backend exact Ruff-recovery product run `34258124033` was cancelled; documentation successor `44e682048fd0e7fa990c46b385931a954ecc0189` has Quality `34258165867` pending at review time. Backend v41 remains held for `ERR-0026` through `ERR-0029`.
- Error handoff records `ERR-0023` fixed and older `ERR-0025` stale after exact Develop Quality `34248696450 = SUCCESS`; `ERR-0026` through `ERR-0029` remain in progress.
- UI-GAP-0004 and UI-GAP-0005 remain technically closed in their exact-green UI lineage; all eleven reference screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`, never `MATCH`, because original pixels are unavailable.

## Next integration order

1. Obtain exact-current-Develop focused §65 plus relevant Research/Core regressions and canonical Quality for the descendant carrying `e10befce38259f15f2e06f06ab7b1ae38356305f`.
2. Consume Backend Quality `34258165867`; do not integrate v41/schema/WAL work while Ruff/pytest evidence is cancelled, pending or red.
3. Once Backend v41 is exact-green, prefer the durable Delta prerequisite needed by Spec/Core §75; otherwise consume exactly one independently reviewed exact-green Core/UI successor.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
