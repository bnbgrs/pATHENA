# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@4e18f75beeaa1c5b57bca28dcad5a062ac498051`.
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

Canonical Quality `34158934575` on `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae`, descendant Quality `34158994436` on `62e1f894d648b661f7e340167d4ac824de237dab`, and first dispatch repair Quality `34162505649` on `b50920a93a3815ceeaef069fb974c7ff5d8ce9ce` all failed only in full pytest on the same §68 acceptance. Exact Error handoff evidence refined `ERR-0020`: final SourceAnalysis artifacts are reduce/final synthesis artifacts, so the prior fixture repair still collapsed all source-specific findings to the generic synthesis payload.

Error commit `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9` provides the proven second minimal fixture-only repair: preserve real schema-phase dispatch, extract `resume-source-\d+` anywhere in request text, return MAP-shaped data for map calls, and carry the same source marker through synthesis-shaped reduce/final responses.

Core commit `95ad54ce07af61d79baf31fbcb7f07ab2f6ff4f6` ports that byte-equivalent test-fixture behavior onto `postmerge/spec-core`. No production code, assertions, persistence semantics, provenance semantics, Source scope or Research orchestration was changed or weakened.

Canonical ATHENA Quality `34166054576` is currently `in_progress` on exact SHA `95ad54ce07af61d79baf31fbcb7f07ab2f6ff4f6`. Therefore §68 remains `IMPLEMENTED_PENDING_VERIFY`, not READY, and no PASS claim is made.

## Coordination state

- Error handoff reviewed on current baseline `4e18f75beeaa1c5b57bca28dcad5a062ac498051`: `ERR-0020` is `IN_PROGRESS`; exact diagnosis and repair source are recorded at Error commit `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9`.
- Backend head reviewed: `postmerge/backend@fa676f0d677bec1d69b2339bf030d57d12431d44`; WAL/scheduler/storage work is disjoint and was not modified.
- UI head reviewed: `postmerge/ui@377d5494b8a6aa9d5a65447b7fe12b5851664914`; current Jobs/accessibility work is disjoint and was not modified.
- Integrator handoff reviewed on `develop/pathena-next@4e18f75beeaa1c5b57bca28dcad5a062ac498051`; affected Spec/Core lineage remains excluded until exact-green successor evidence exists.
- Current worker mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Consume exact canonical verification `34166054576` for `95ad54ce07af61d79baf31fbcb7f07ab2f6ff4f6` or an unchanged documentation descendant.
2. If green, close `ERR-0020`/§68 with the exact verified SHA and hand it to Integrator; then history-preservingly synchronize with latest `develop/pathena-next` only if every foreign delta is retained.
3. Immediately execute normative Exhaustive Research §69 Failure Test unless equivalent exact acceptance already exists; do not spend another run re-analyzing §68.
4. If red, retrieve the new exact primary pytest failure and repair only that concrete root cause without Skip/XFail, weaker assertions, fake restart state or synthetic provenance.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
