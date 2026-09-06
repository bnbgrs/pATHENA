# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@8ca3c7b87677a59b9d99d6a5b8703cfc78da6c28`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- Product/test head before synchronization: `396a66302d0e4e96deb2d69076fdaa340bb395c5`.
- Exact product/test head passed ATHENA Quality Gate run `34008561064` with conclusion `success`.
- History-preserving NON-FORCE synchronization merge: `9b9807694b50cc237cae37480743bde6be3bf6fe`, parents `396a66302d0e4e96deb2d69076fdaa340bb395c5` and `8ca3c7b87677a59b9d99d6a5b8703cfc78da6c28`.

## READY slice — model-inferred Personal Memory default suggest boundary

Spec source: `docs/beta/06_Personal_Memory.md` default-suggest/review-gate and sensitive-memory Human-Control requirements.

Product lineage:

- proposal model: `3fd6a31b7d469aacee30353e82b4083bfe6f3fa0`;
- service boundary: `7d3a2ae8da7f14d376d1b7400d3b49be006dbce8`;
- real SQLite acceptance: `396a66302d0e4e96deb2d69076fdaa340bb395c5`;
- canonical Quality: `34008561064 = success`.

Contract now verified:

- `ModelInferredMemoryProposal` is non-canonical and requires `MODEL_INFERRED`, confidence, caller-supplied `model_signature_id`, caller-supplied `processing_run_id`, and `review_required=True`;
- `PersonalMemoryService.propose_model_inferred()` performs no Personal-Memory repository write;
- NORMAL inferred preferences remain suggestions pending explicit review;
- SENSITIVE/PROTECTED inferred content fails closed before canonical persistence;
- focused persistence acceptance proves both normal suggestion and rejected sensitive inference leave the canonical Personal Memory store unchanged;
- explicit-user Memory write/revise/confirm semantics and scoped context ordering remain unchanged.

Integrator may review/import this bounded lineage. The synchronized worker preserves exact product/test blobs over current Develop without force/rebase/history rewrite.

## Coordination / collision avoidance

- Backend active head observed this run: `a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`; current work is Backend/System-owned and disjoint from Personal-Memory review composition.
- UI active head observed this run: `3c5fe2e16293e9bfb8228e62b0f7a183b34a92f7`; UI presentation remains disjoint.
- Error active head observed this run: `46fb660d7980d83e1b22c061187bae2b99832610`; no current exact-SHA Core blocker was found.
- Integrator handoff on current Develop was reviewed before mutation.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Retained release/runtime invariants

Do not regress Windows pypdf distribution metadata, frozen unknown-argv fail-closed routing, Desktop/Worker two-EXE topology, bounded/non-growing worker process tree, adaptive 2048-context DirectChat reserve/safety guard, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster, or storage-bootstrap/migration startup invariants. Historical signatures reopen only on current exact-SHA reproduction.

## Next Alpha/Beta gap

Implement the smallest explicit review-acceptance boundary for one `ModelInferredMemoryProposal`. User acceptance must be the only path that can convert a reviewed proposal into canonical Memory; it must not silently overwrite an existing explicit-user revision. Before product mutation, verify the durable provenance model can persist the proposal's real `model_signature_id` and `processing_run_id`. If the current Personal-Memory provenance schema cannot represent those IDs, do not discard or synthesize them: version the exact schema/composition blocker and switch to the next disjoint evidence-backed Core slice rather than weakening provenance.

Normal-Hybrid Search remains previously verified/integrated; do not reopen or broaden Archive/Protected Search semantics without new evidence.
