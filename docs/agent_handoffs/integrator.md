# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop baseline for this run: `b04b0107f55d8af8b0398e48066481a84d27775f`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `28028ffdecac12e296e5c6268b0a657934fc74a2`; spec-core `d7032f86adf79746ac73be19b1bcc4542b7e5689`; backend `3fbd8c238b8e926c5c175e37805c3033cb90e6b6`; UI `a426469b503c6276cd6d1fd3ed6d89be0af67948`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, history rewrite, auto-merge or main promotion was used.

## Exact evidence consumed

- Exact Develop head `b04b0107f55d8af8b0398e48066481a84d27775f` had no associated canonical Quality run and no queued/in-progress Develop exact-head gate when mutation eligibility was checked.
- UI exact head `a426469b503c6276cd6d1fd3ed6d89be0af67948` has canonical Quality `34291934346` still `in_progress`; it was not consumed as READY evidence.
- Backend exact head `3fbd8c238b8e926c5c175e37805c3033cb90e6b6` has canonical Quality `34290849093` still `in_progress`; it was not consumed as READY evidence.
- Spec/Core current head is documentation-only over the already-integrated adaptive DirectChat lineage; no new product slice was selected.
- Error handoff records completed WAL candidate evidence, but the current Backend exact-head gate is still running, so no storage/runtime prerequisite was integrated conservatively.

## Progress this run — adaptive-reserve upper-bound regression

No current worker was READY at mutation time. A bounded Core-owned release-guard regression was added to `tests/unit/test_direct_chat_context_budget.py`: when the active loaded context is 2048 tokens and sufficient room remains, a smaller configured output reserve of 128 tokens must remain exactly 128 rather than being inflated by adaptive budgeting.

This locks the second half of the adaptive-reserve contract: adaptation may reduce the configured reserve to fit the loaded context, but must never increase the user/configured generation ceiling. Existing 2048-context adaptation, one-token boundary and fail-closed exhaustion assertions remain unchanged. No production behavior, provider contract, Storage, Recovery, Security, scheduler/worker, packaging or Windows process semantics changed. No Skip/XFail or assertion weakening was added.

Local repository checkout remained blocked by DNS resolution of `github.com`; the focused pure-function boundary was independently evaluated against the exact current helper semantics and passed. Canonical repository Quality remains required before promotion/readiness claims.

## Current quality/error state

- UI current exact Quality `34291934346`: `in_progress`.
- Backend current exact Quality `34290849093`: `in_progress`.
- Develop after this test/handoff commit has no completed canonical Quality claim yet; promotion-ready remains false.
- Historical Windows/runtime signatures remain release guards and are not reopened without exact-current reproduction.

## Tracker / visual state

- `docs/development/ALPHA_BETA_PROGRESS.md` was read as current source-of-truth input. No percentage was invented and no unsafe truncated whole-file rewrite was attempted.
- The 11-screen manifest and Visual-Gap ledger remain UI evidence sources; this run made no UI product mutation and no visual `MATCH` claim.

## Next integration order

1. Re-check exact-current Develop CI before any further Develop mutation.
2. Consume UI Quality `34291934346` only if it completes successfully on exact head `a426469b503c6276cd6d1fd3ed6d89be0af67948` without superseding worker commits, then independently review its bounded palette slice.
3. Consume Backend Quality `34290849093`; keep Backend/Storage/WAL conservative until exact-green before unblocking dependent Core composition.
4. Preserve the Windows/Packaging/Runtime regression matrix before any Beta/release claim.

## Persistent release guards

Retain explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting including one-token and configured-upper-bound behavior; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
