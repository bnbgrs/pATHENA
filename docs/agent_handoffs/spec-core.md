# Spec/Core Handoff

## Current baseline

- Develop baseline checked: `develop/pathena-next@270f97c36bd114036658e322f68d8011983ff150`.
- Pre-run Core worker: `postmerge/spec-core@298bb61c07dd2fdedea0e8a24db30410442c6794`; canonical Quality `34244657010 = SUCCESS`.
- Current Develop differs from the worker only in Integrator/UI-owned Jobs copy/test files relative to merge-base `4f077e36248a49d261f13d3f3838d62a376f506f`; no Core/Research file collision was found. No force update, history rewrite, main mutation or ATHENA mutation occurred.

## Required handoffs checked

- Errors: current handoff reviewed; Backend v41 remains split into ERR-0026 through ERR-0029 and is not consumable by Core while exact Backend Quality remains red.
- Backend: current handoff reviewed; storage/schema/WAL ownership remains Backend-only.
- UI: current handoff reviewed; UI-GAP-0004 is exact-green/integrated-lineage work and remains presentation-owned.
- Integrator: current Develop handoff reviewed at `270f97c36bd114036658e322f68d8011983ff150`.

## Preserved Core contracts

Normal Hybrid Search remains exact-green in inherited lineage: one-time `attach_normal_search`; `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagates unchanged; `app.api._normal_search is app.hybrid_retrieval`. Research §68-§74 accepted lineage remains preserved. No synthetic provenance, Archive/Protected expansion, fake PALLAS data, Skip/XFail, assertion weakening, force push, main mutation or ATHENA mutation.

## §75 Delta Research

Backend v41 remains unverified/red on its current lineage, so Core did not consume or duplicate schema/storage work. The bounded Core continuation remains: explicit completed `base_scope_id`, durable lower commit boundary, upper `snapshot_commit_seq`, and frozen candidates only in `(lower_commit_seq, snapshot_commit_seq]`, restart-stable without wall-clock substitution.

## §65 Partial Result — implemented pending exact verification

Beta Research §64 requires cancellation to preserve confirmed intermediate results without a false complete Final Result; §65 permits an explicitly requested report that is clearly partial.

Product commit `47027ae91680765c6e9da640f90cad2566c77ae3` adds `ResearchPartialResultService`. It is deliberately post-cancel and opt-in: only `research.exhaustive` jobs in durable `CANCELLED` state with a durable `PARTIAL` Research scope are eligible. The service persists a `ResearchResult` with `final_artifact_id = NULL`, `partial = true`, `result_status = "partial"`, `completion_reason = "cancelled"`, real coverage/problem-source fields and the existing source-coverage composition. It reuses only already-completed immutable synthesis artifacts, records each artifact identity/hash/content plus its resolved SourceAnalysis artifact provenance, leaves the scope PARTIAL and job CANCELLED, and is idempotent for the same partial representation. It performs no model call and fabricates no missing sections/evidence.

Acceptance commit `1165890634a3bef43e27eed3f262552e70f768a9` adds `tests/unit/test_exhaustive_research_partial_result.py`. The test drives four real captured Sources through Source processing/analysis, commits a real REDUCE artifact, cancels through the real Research worker, then explicitly creates the partial report. Assertions require nullable final artifact, explicit partial labeling, inclusion of the exact confirmed REDUCE artifact/content hash/source-analysis provenance, real persisted coverage, unchanged PARTIAL/CANCELLED state, idempotency, and absence of any completed FINAL artifact.

Canonical Quality `34250365477` is PENDING on exact acceptance SHA `1165890634a3bef43e27eed3f262552e70f768a9`. No PASS/READY claim is made yet.

## Required next actions

1. Consume exact Quality `34250365477`. If red, repair only the exact demonstrated §65 defect without weakening partial/provenance/cancellation assertions.
2. If exact-green, mark §65 READY and hand the verified product/test SHA to Integrator; then inspect the next highest independent Alpha/Beta Core gap.
3. Consume Backend §75 only after its v41/schema/WAL line is exact-green; do not absorb unverified persistence code.
4. Preserve release regression matrix: pypdf/frozen argv/two-EXE routing, bounded worker tree, 2048-context reserve, lane-lock ownership cluster, duplicate-column startup, Core startup and storage-bootstrap signatures. Historical signatures become OPEN only on exact-SHA reproduction.
