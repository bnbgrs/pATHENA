# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@51bd144aafc0fb1f50c00515c366442038a2c251`.
- Worker branch: `postmerge/spec-core` only.
- Previous exact-green worker predecessor: `c6b4fdba485a1de249a93e99883fca4085b9fc48`, ATHENA Quality `34127196867 = success`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

Personal-Memory §42-§47 behavior and §50 Reset isolation remain inherited from prior exact-green Core evidence. §49 Protected Lock remains a documented cross-component dependency: Core preserves fail-closed plaintext refusal and does not fabricate passphrase/unlock/index/suggestion surfaces.

## Current bounded slice — Exhaustive Research §68 Resume Test

Normative §68 requires a five-source Exhaustive Research run to stop at 60%, restart from durable state, continue, retain all prior Findings, and avoid duplicates.

Product/test commit `6ad95079a114ea1d89517f7c299153caef66d3b5` added `tests/unit/test_exhaustive_research_resume.py` using the real `AthenaApplication` durable runtime, real Source capture/preprocessing, Research parent/child orchestration, persisted work items, SourceAnalysis artifacts, content hashes and Finding payloads.

Canonical Quality `34155243750` on exact SHA `6ad95079a114ea1d89517f7c299153caef66d3b5` completed `failure` only in full pytest. Validator, Ruff, mypy, Local install smoke, Linux storage regressions and Windows path safety all passed. Error handoff allocated this exact failure as `ERR-0020` and correctly left product-vs-harness classification open because the diagnostics archive traceback is not exposed by the current connector.

A concrete deterministic harness defect was then identified directly in the only new test delta: `_successful_finding_snapshots()` sorts snapshots by random `work_item_id` UUID bytes, but the final assertion compared `final_snapshots[:3] == before_restart`. After two more successful work items are added, the original three persisted snapshots are not guaranteed to remain in the first three positions of the newly sorted five-item tuple. That assertion tested random ordering rather than durable identity preservation.

Repair commit `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae` changes only this assertion to an identity-keyed check: each pre-restart snapshot must be present under its exact `work_item_id` with the complete tuple unchanged. All existing uniqueness, content-hash, artifact-id, analysis-job-id, Finding payload and coverage assertions remain intact. No assertion was weakened: the repaired test still proves exact pre-restart identity/payload preservation and five unique final durable results, but no longer relies on incidental UUID ordering.

Canonical ATHENA Quality `34158934575` is currently running on exact repair SHA `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae`. No PASS or READY claim is made until it completes successfully.

## Coordination state

- Error handoff reviewed at baseline `51bd144aafc0fb1f50c00515c366442038a2c251`: `ERR-0020` is IN_PROGRESS for exact red SHA `6ad95079...`; its evidence matches this repair path.
- Backend handoff reviewed: WAL/scheduler/storage work is disjoint and was not modified.
- UI handoff reviewed: current UI accessibility/Jobs work is disjoint and was not modified.
- Integrator handoff reviewed at `develop/pathena-next@51bd144aafc0fb1f50c00515c366442038a2c251`; Spec/Core remains excluded until exact-green successor evidence exists.
- Current worker remains non-force and no foreign branch/history was overwritten.

## Next Core action

1. Consume exact Quality `34158934575` on `8c1218e901767c48b4c1cd98e33e3b9fc72ac3ae`.
2. If green, hand the exact verified §68 SHA lineage to Integrator, then history-preservingly synchronize against latest `develop/pathena-next` only if all foreign deltas can be retained.
3. Immediately execute normative Exhaustive Research §69 Failure Test unless equivalent exact acceptance already exists; do not repeat §68 analysis.
4. If `34158934575` is red, recover the new exact primary pytest failure and repair only that concrete root cause without Skip/XFail, weaker assertions, fake restart state or synthetic provenance.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
