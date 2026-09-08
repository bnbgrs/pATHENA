# Spec/Core Handoff

## Current baseline

- Develop baseline checked: `develop/pathena-next@a60b067ebf93481d180065cdf3e85ad3da3a2a5e`.
- Pre-run Core worker: `postmerge/spec-core@4cb7b137164e411ba02d83ce53926aa615cf3a36`.
- Exact worker canonical Quality `34255843664 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched. No force update, rebase or history rewrite occurred.

## Required handoffs / active heads checked

- Errors handoff: current baseline is Develop `a60b067ebf93481d180065cdf3e85ad3da3a2a5e`; `ERR-0026` through `ERR-0029` remain Backend-owned/in progress.
- Backend handoff and active head: `postmerge/backend@44e682048fd0e7fa990c46b385931a954ecc0189`; exact Quality `34258165867` remains in progress with Ruff already red, so Backend v41 / §75 persistence remains non-consumable.
- UI handoff and active head: `postmerge/ui@59aa42824d4e7475af29403fb6bbc78fd9c58d08`; UI work is disjoint and presentation-owned.
- Integrator handoff: current Develop integrates the verified §65 product/test slice and records the exact worker evidence.

## Preserved Core contracts

Normal Hybrid Search remains inherited and unchanged: one-time `attach_normal_search`; `search.normal.hybrid` only after attachment; exact `query/model_id/limit/entity_type` delegation; canonical `hybrid_search_result_response()` mapping; `SemanticRetrievalUnavailableError` propagates unchanged; `app.api._normal_search is app.hybrid_retrieval`.

Research §68–§74 accepted lineage remains preserved. No synthetic provenance, Archive/Protected expansion, fake PALLAS data, Skip/XFail, assertion weakening, force push, main mutation or ATHENA mutation.

## §65 Partial Result — VERIFIED / INTEGRATED

The type-only repair at exact Core SHA `4cb7b137164e411ba02d83ce53926aa615cf3a36` passed canonical Quality `34255843664 = SUCCESS` with the §65 runtime semantics unchanged.

Integrator independently transplanted the bounded verified slice to Develop:

- product commit `eeb8a9f3c97c0cacc00c55af8d8a3260d1edccb0` adds `ResearchPartialResultService`;
- acceptance commit `e10befce38259f15f2e06f06ab7b1ae38356305f` adds the byte-identical exact-green acceptance;
- Develop handoff head `a60b067ebf93481d180065cdf3e85ad3da3a2a5e` records the integration.

Contract retained: explicit opt-in only after a real durable `research.exhaustive` job is `CANCELLED` and its Research scope is `PARTIAL`; `final_artifact_id = NULL`; explicit partial status/reason; confirmed immutable synthesis artifacts only; exact artifact hash/content and SourceAnalysis provenance; real coverage/problem-source composition; no new model call; no fabricated completeness; idempotent representation; no completed FINAL artifact required or invented.

## §75 Delta Research — blocked on exact-green Backend persistence

The bounded Core contract remains unchanged: explicit completed `base_scope_id`, durable lower commit boundary, pinned upper `snapshot_commit_seq`, candidate freeze only in `(lower_commit_seq, snapshot_commit_seq]`, and restart-stable boundary/CandidateSet identity without wall-clock substitution.

Core must not consume Backend v41 while exact Backend Quality remains red/pending. Current Backend/Error evidence still owns schema/migration/WAL recovery under `ERR-0026` through `ERR-0029`.

## Independent-gap scan

The current evidence-backed progress tracker was re-read after §65 integration. Core-owned Normal Hybrid Search, contradiction composition and the completed Exhaustive Research acceptance chain through §74 are already VERIFIED. The currently listed READY P1 gaps in the Scout backlog (`FG-021`, `FG-022`, `FG-029`, `FG-031`, plus the primary side of `FG-030`) require deep job/source schema, scheduler, transport or representation-provider work and are Backend-owned or Backend-primary. Core therefore does not create a duplicate implementation merely to keep moving while §75 persistence is unverified.

## Required next actions

1. Consume completed Backend Quality `34258165867` and any exact successor evidence.
2. If Backend v41 becomes exact-green and available on the shared baseline, execute §75 immediately: `enqueue_delta`, one-time durable boundary binding, candidate selection over `(lower_commit_seq, snapshot_commit_seq]`, restart/resume identity acceptance, focused tests then canonical Quality.
3. If Backend remains red, inspect newly versioned Alpha/Beta/Capability evidence for a genuinely independent Core-owned P0/P1/P2 gap; do not repeat already-verified §65 or invent Backend work.
4. Preserve release regression matrix: pypdf/frozen argv/two-EXE routing, bounded worker tree, adaptive 2048-context reserve, lane-lock ownership cluster, duplicate-column startup, Core startup and storage-bootstrap signatures. Historical signatures become OPEN only on exact-SHA reproduction.
