# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline checked before mutation: `develop/pathena-next@d5b4d1479416edd1cd55f8bff6190029f42d9289`.
- Pre-run worker: `postmerge/spec-core@f4abb89d7538a11efa50d94a847b6f69139c602b`.
- §73 External Capture acceptance `bb5806123097171598584166ff10f3b5e28d07ca` is exact-green via canonical Quality `34219791632 = success` and is already integrated in Develop.
- History-preserving NON-FORCE reconciliation commit `a36e447b84629e742d84989e5a8a0e86914963c5` has first parent the prior worker and second parent current Develop. Its tree keeps current Develop authoritative while preserving verified Spec/Core Memory files, personal-memory tests and this handoff. `main` and `bnbgrs/ATHENA` remain untouched.

## Verified Core contracts

Normal Hybrid Search remains preserved: one-time `attach_normal_search`; capability `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; unchanged `SemanticRetrievalUnavailableError`; and `app.api._normal_search is app.hybrid_retrieval`.

§68 durable restart, §69 model drift, §70 pinned 2048-context Large Archive, §71 opposing-source contradiction, §72 unavailable NAS and §73 external capture/no-refetch remain preserved.

## Exhaustive Research §74 — Cancel Test

Normative contract: cancel during REDUCE; confirmed partial results must remain durable; no complete final result may be emitted.

Existing product behavior already observes `CANCEL_REQUESTED` before further Research advancement, marks the Research scope `PARTIAL`, cancels nonterminal children and acknowledges the parent as `CANCELLED`. Existing tests did not prove the exact REDUCE-boundary preservation contract.

### Implemented acceptance

Test commit: `a37f4c624b5f4c8aef726384862de513294865f6`.

New file: `tests/unit/test_exhaustive_research_cancel.py`.

The acceptance uses real `AthenaApplication`, durable Research/Job repositories and real `ResearchSynthesisService` orchestration with the established deterministic model-provider test boundary. It drives four real captured Sources through SourceAnalysis to synthesis, splits FINAL work into REDUCE children, completes and persists one REDUCE artifact, requests user cancellation, then lets the real Research worker acknowledge it. It asserts:

- synthesis is actually in REDUCE;
- the first REDUCE work item and immutable artifact are confirmed before cancellation;
- parent transitions through `CANCEL_REQUESTED` to `CANCELLED`;
- Research scope becomes `PARTIAL`;
- the confirmed REDUCE artifact remains byte/identity-stable and its work item remains `COMPLETED`;
- no FINAL synthesis work is completed;
- no row exists in `research_results` for the cancelled scope.

No production code changed, no fake persistence/provenance was introduced, and no Skip/XFail/assertion weakening was added.

### Verification

No canonical workflow was visible yet for exact §74 SHA `a37f4c624b5f4c8aef726384862de513294865f6` when this handoff was written. Therefore §74 is `IMPLEMENTED_PENDING_EXACT_VERIFY`; no PASS/READY claim is made.

The preceding reconciliation commit is also awaiting its exact canonical result on this new lineage; do not infer PASS from prior ancestor runs.

## Coordination state

- Error handoff checked; no exact-current historical Windows/runtime crash signature was promoted to OPEN.
- Backend handoff checked; Backend WAL/storage/scheduler ownership remains disjoint and untouched.
- UI handoff checked; UI presentation/accessibility/Settings ownership remains disjoint and untouched.
- Integrator handoff checked on current Develop; no unverified §74 successor is offered READY.

## Next Core action

1. Consume the first canonical Quality run for `a37f4c624b5f4c8aef726384862de513294865f6` or unchanged handoff descendant.
2. If §74 is exact-green, mark it READY, hand the verified SHA to Integrator, then immediately execute the next normative Alpha/Beta Core gap.
3. If red, retrieve the exact failing assertion/traceback and repair only the demonstrated defect without weakening REDUCE identity, durable partial-artifact, `PARTIAL` scope, `CANCELLED` parent or no-complete-result assertions.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.