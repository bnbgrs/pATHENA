# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@d40dc421585193db7bda039d113d7d81ccfb9c03`.
- Worker branch: `postmerge/spec-core` only.
- Current pre-handoff worker head: `80915e1e8c7dff42fc998e9035df41273bdb08ca`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, rebase or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

Personal-Memory §42-§47 behavior and §50 Reset isolation remain inherited from prior exact-green Core evidence. §49 Protected Lock remains a documented cross-component dependency: Core preserves fail-closed plaintext refusal and does not fabricate passphrase/unlock/index/suggestion surfaces.

## Exhaustive Research §68 — READY

Normative §68 requires a five-source Exhaustive Research run to stop at 60%, restart from durable state, continue, retain all prior Findings, and avoid duplicates.

`tests/unit/test_exhaustive_research_resume.py` exercises the real persistent `AthenaApplication`, real Source capture/preprocessing, real Research parent/child orchestration, persisted ResearchWorkItems, SourceAnalysis final artifacts, content hashes and Finding payloads. The test stops after exactly three of five successful sources, requires coverage `0.6`, reconstructs the application against the same durable root, proves the first three persisted identities/content hashes/Finding payloads survive, completes the remaining two sources, and requires coverage `1.0` with five unique work items, analysis jobs, final artifacts and Finding payloads.

The earlier ERR-0020 failures were harness-only and are now closed. Final repair commit `95ad54ce07af61d79baf31fbcb7f07ab2f6ff4f6` preserves the `resume-source-*` marker through MAP and reduce/final synthesis fixture responses without changing production code or weakening assertions. Canonical ATHENA Quality `34166054576` on that exact commit completed `success`.

Current worker head `80915e1e8c7dff42fc998e9035df41273bdb08ca` carries the unchanged verified fixture plus the prior handoff, and exact canonical ATHENA Quality `34166094972` completed `success`. Error handoff therefore marks `ERR-0020` FIXED and clears the hold for this exact Spec/Core head.

Status: `§68 READY / INTEGRATOR_READY @ 80915e1e8c7dff42fc998e9035df41273bdb08ca / Quality 34166094972 = success`.

## Exhaustive Research §69 — existing exact acceptance, no duplicate patch

Normative §69 requires changing the primary model between pause/resume and detecting drift rather than silently mixing model configurations.

Existing `tests/unit/test_exhaustive_research_orchestration.py::test_model_drift_between_candidates_waits_user_without_mixed_child` already uses the real Research orchestration path. It processes the first candidate under the pinned model signature, changes provider quantization from Q4 to Q5 before the next candidate, then requires the parent Research job to enter `WAITING` with `WaitingReason.USER` and proves only one successful work item / one analysis child exists. This is the required fail-closed model-drift behavior and prevents mixed-child processing.

No duplicate §69 test was created. The next normative Core-owned gap is §70 Large Archive Test.

## Coordination state

- Error handoff reviewed on `develop/pathena-next@d40dc421585193db7bda039d113d7d81ccfb9c03`: OPEN none, IN_PROGRESS none, `ERR-0020` FIXED; Spec/Core `80915e1e8c7dff42fc998e9035df41273bdb08ca` is recorded exact-green via Quality `34166094972`.
- Backend handoff reviewed; Backend WAL/deadline/storage work remains disjoint and no Backend file was modified by Core.
- UI handoff reviewed; Jobs product-language/accessibility work remains disjoint and no UI file was modified by Core.
- Integrator handoff reviewed from current Develop; its prior ERR-0020 hold is now superseded by exact-green Error/Core evidence above. Integrator should independently consume this exact READY SHA rather than infer readiness from divergent worker history.
- All Core mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Treat `80915e1e8c7dff42fc998e9035df41273bdb08ca` as exact §68 READY evidence for Integrator.
2. Do not duplicate §69; existing real acceptance already covers model drift fail-closed behavior.
3. Execute §70 Large Archive Test against the real SourceAnalysis/Research context-budget composition: CandidateSet materially larger than a single model context and explicit proof that no individual model call exceeds the pinned context budget. Do not simulate a fake budget surface or weaken the small-context safety contract.
4. Before mutation, re-read latest Develop and all worker heads; synchronize only history-preservingly and only if every foreign delta is retained.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
