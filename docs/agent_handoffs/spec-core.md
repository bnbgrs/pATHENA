# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@8ebb41102c1f1b59471ab6392e930af1c52fec31`.
- Worker branch: `postmerge/spec-core` only.
- Previous exact-green worker predecessor: `c6b4fdba485a1de249a93e99883fca4085b9fc48`, ATHENA Quality `34127196867 = success`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

Personal-Memory §42-§47 behavior and §50 Reset isolation remain inherited from prior exact-green Core evidence. §49 Protected Lock remains a documented cross-component dependency: Core preserves fail-closed plaintext refusal and does not fabricate passphrase/unlock/index/suggestion surfaces.

## Current bounded slice — Exhaustive Research §68 Resume Test

Normative §68 requires a five-source Exhaustive Research run to stop at 60%, restart from durable state, continue, retain all prior Findings, and avoid duplicates.

Product/test commit `6ad95079a114ea1d89517f7c299153caef66d3b5` added `tests/unit/test_exhaustive_research_resume.py` using the real `AthenaApplication` durable runtime, real Source capture/preprocessing, Research parent/child orchestration, persisted work items, SourceAnalysis artifacts, content hashes and Finding payloads.

Canonical Quality `34155243750` on exact SHA `6ad95079a114ea1d89517f7c299153caef66d3b5` failed only in full pytest. The first concrete harness defect was an order-dependent final assertion over UUID-sorted work items. Repair commit `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae` replaced only that ordering assumption with exact `work_item_id`-keyed tuple preservation while retaining all identity, uniqueness, content-hash, Finding-payload and coverage assertions.

Canonical Quality `34158934575` on `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae` also failed only in full pytest. Its exact descendant handoff Quality `34158994436` on `62e1f894d648b661f7e340167d4ac824de237dab` reports one failing test: `test_exhaustive_research_restart_at_sixty_percent_preserves_findings_without_duplicates`, where five distinct Finding payloads were required but the fixture produced only `{('synthesis finding',)}`.

Error worker diagnosis `ERR-0020` proved a second deterministic harness-only defect: `_ResearchProvider.generate_structured()` inferred source-analysis dispatch from `"map" in schema_id`, but real source-analysis schema IDs do not satisfy that fixture assumption. The production path therefore correctly executed while the test fixture returned its generic synthesis payload for every source.

Core repair commit `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce` ports the minimal proven fix onto `postmerge/spec-core`: detect the real per-source `resume-source-*` marker in request text and return a unique corresponding Finding. No production code, assertions, persistence semantics, provenance semantics, Source scope or Research orchestration was weakened or changed.

At handoff update time no workflow run was yet visible for exact SHA `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce`. Therefore §68 remains `IMPLEMENTED_PENDING_VERIFY`, not READY.

## Coordination state

- Error handoff reviewed on current baseline `8ebb41102c1f1b59471ab6392e930af1c52fec31`: `ERR-0020` is `IN_PROGRESS`; its exact diagnosis matches the Core fixture repair now applied on `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce`.
- Backend handoff reviewed: WAL/scheduler/storage work is disjoint and was not modified.
- UI handoff reviewed: current Jobs/accessibility work is disjoint and was not modified.
- Integrator/Develop baseline reviewed at `8ebb41102c1f1b59471ab6392e930af1c52fec31`; the affected Spec/Core lineage remains excluded until exact-green successor evidence exists.
- Current worker mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Consume exact focused/canonical verification for `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce` or its unchanged documentation descendant.
2. If green, close §68 with the exact verified SHA and hand it to Integrator; then history-preservingly synchronize with latest `develop/pathena-next` only if every foreign delta is retained.
3. Immediately execute normative Exhaustive Research §69 Failure Test unless equivalent exact acceptance already exists; do not spend another run re-analyzing §68.
4. If red, retrieve the new exact primary pytest failure and repair only that concrete root cause without Skip/XFail, weaker assertions, fake restart state or synthetic provenance.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
