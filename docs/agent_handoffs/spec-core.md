# Spec/Core Handoff

## Current baseline

- Develop baseline checked: `develop/pathena-next@4f077e36248a49d261f13d3f3838d62a376f506f`.
- Pre-run Core worker: `postmerge/spec-core@56a6d0602361e0e7b3ad97e6ec52e2a35443dded`; canonical Quality `34237486353` = SUCCESS.
- History-preserving reconciliation: `ddba8f12c0bfb06e3f38e1da2705781ae70f3f1a`, parents `56a6d0602361e0e7b3ad97e6ec52e2a35443dded` and `4f077e36248a49d261f13d3f3838d62a376f506f`. Develop-owned `docs/agent_handoffs/integrator.md` and `tests/unit/test_pathena_jobs_status_copy.py` were imported byte-identically; update was NON-FORCE.
- Reconciliation Quality `34244127053` is still running in Python quality at this handoff; Local install smoke, Linux storage regressions and Windows path safety are already SUCCESS. No current-head PASS claim.

## Preserved Core contracts

Normal Hybrid Search remains exact-green in inherited lineage: one-time `attach_normal_search`; `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagates unchanged; `app.api._normal_search is app.hybrid_retrieval`. Research §68-§74 accepted lineage is preserved. No synthetic provenance, Archive/Protected expansion, fake PALLAS data, skip/XFail, assertion weakening, force push, main mutation or ATHENA mutation.

## §75 Delta Research — Backend prerequisite still blocked

Normative contract: Beta Research §57/§75 requires processing only Sources introduced since a previous committed snapshot while the old snapshot remains referencable. Core continuation remains bounded to an explicit completed `base_scope_id`, durable lower commit boundary, upper `snapshot_commit_seq`, and candidate freeze over `(lower_commit_seq, snapshot_commit_seq]`; restart/resume must preserve the same boundaries and CandidateSet identity. Wall-clock substitution is forbidden.

Backend product `255e73eae28651c20ae1baa660c4087f4a62f128` implements schema v41 / migration `0041_research_delta_boundary` / durable `ResearchDeltaBoundaryRepository`. The first canonical red was narrowed to stale `test_main_schema` user_version=28 expectation and Backend corrected that in `72831adaf8c6b13f259921646c6153d4a7a78b68`, with handoff `00b630e4915ec85abc08252d85e6403009b48858`.

Canonical Backend Quality `34239827573` on `00b630e4915ec85abc08252d85e6403009b48858` completed FAILURE. Local install smoke, Linux storage regressions and Windows path safety are SUCCESS, but Python quality has both Ruff and pytest failures. Diagnostics artifact is `canonical-quality-diagnostics-00b630e4915ec85abc08252d85e6403009b48858`, artifact id `10063197080`, SHA256 `568aa8c0765aed96ee23e53ac6c31201def323b35d9e77c16301ac2c904aeaff`. Therefore Core must not consume the v41 prerequisite yet.

## Independent Core gap while §75 is blocked — §65 Partial Result

Beta Research §64 says cancel preserves confirmed intermediate results without falsely complete Final Result; §65 separately allows an aborted Research job, on request, to produce a report clearly marked partial. Existing exact §74 acceptance `tests/unit/test_exhaustive_research_cancel.py` deliberately proves confirmed REDUCE artifact survival and `research_results` count remains zero after cancellation. `ResearchResultRecord.final_artifact_id` is already nullable, while the current synthesis completion path requires a confirmed FINAL artifact. This establishes a concrete Core-owned composition gap: an explicit opt-in partial-result/report path is not represented by the current cancel acceptance/completion API.

Next bounded implementation must reuse only confirmed immutable synthesis artifacts and real coverage/provenance, produce a ResearchResult explicitly marked partial with `final_artifact_id=None` (or another already-canonical nullable partial representation if repository contracts require it), never call it complete, never fabricate missing sections/evidence, and remain opt-in after cancellation. Before mutation, inspect repository insertion/idempotency and API/controller exposure so the smallest existing representation is used rather than adding storage schema.

## Required next actions

1. Consume exact reconciliation Quality `34244127053`; no READY unless exact current worker is green.
2. Consume Backend's next exact diagnostic/fix. Only after Backend v41 is exact-green may Core implement `enqueue_delta` and the bounded `(lower, upper]` candidate-window acceptance.
3. While Backend remains red, execute §65 Partial Result as the next independent Core slice: inspect existing result insertion/API composition, implement the smallest opt-in partial-result path with a real cancel/confirmed-artifact acceptance, run focused tests then canonical Quality.
4. Preserve release regression matrix: pypdf/frozen argv/two-EXE routing, bounded worker tree, 2048-context reserve, lane-lock ownership cluster, duplicate-column startup, Core startup and storage-bootstrap signatures. Historical signatures become OPEN only on exact-SHA reproduction.
