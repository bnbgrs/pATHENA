# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@fd15a75212acac7f88886117835b8d754577ea91`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `00f2441e67407f4402d82c8ad3b6aad28403e212`, parents prior Core head `0824bc5779d19e53585a315aeee2e468217b3f41` and exact current Develop `fd15a75212acac7f88886117835b8d754577ea91`.

## Previously READY — model-inferred Personal Memory default suggest boundary

- Exact product/test head `396a66302d0e4e96deb2d69076fdaa340bb395c5` passed ATHENA Quality `34008561064 = success`.
- `ModelInferredMemoryProposal` remains non-canonical and review-gated.
- NORMAL inferred preferences remain suggestions pending explicit review; SENSITIVE/PROTECTED inference fails closed before canonical persistence.
- Explicit-user Memory operations and scoped context ordering remain unchanged.

## Implemented pending canonical Quality — explicit reviewed inference acceptance

Spec source: `docs/beta/06_Personal_Memory.md` Human-Control/default-suggest requirements plus the repository-wide provenance contract.

Current provenance schema already contains `model_signature_id` and `processing_run_id`; no schema migration was required. The previous repository path always wrote both columns as `NULL`, so this slice changes only the Memory create/provenance composition boundary.

Product/test head: `f4a793171e56305f47e49d177e16287619b943bf`.

Contract implemented:

- `PersonalMemoryRepository.create()` accepts an optional model-provenance pair and rejects a half-present pair;
- `_insert_provenance()` persists the exact caller-supplied `model_signature_id` and `processing_run_id` when present, while explicit-user writes retain `NULL/NULL` behavior;
- `PersonalMemoryService.accept_model_inferred()` is the explicit user-review boundary that canonizes one previously non-canonical proposal;
- accepted Memory retains `MODEL_INFERRED` learning mode and confidence, receives an explicit confirmation timestamp, and persists the proposal's exact model/processing provenance;
- acceptance creates a new canonical Memory entry rather than silently revising or overwriting an existing explicit-user Memory revision.

Real SQLite acceptance: `tests/unit/test_personal_memory_review_acceptance.py` proves durable provenance identity and non-overwrite behavior.

Focused GitHub runner evidence:

- initial applicator run `34013694569` failed before tests because a deterministic exact-match anchor was intentionally non-unique; no product mutation occurred;
- corrected run `34013731297 = success` after narrowing the anchor to the `personal_memory.create` call;
- corrected run passed the deterministic patch, focused Personal-Memory pytest set, Ruff, mypy and `git diff --check`, then created product/test commit `f4a793171e56305f47e49d177e16287619b943bf`;
- the automatic canonical Quality attached directly to the GitHub-Actions-authored product commit was `34013750664 = action_required`, so it is not counted as canonical verification;
- temporary applicator/workflow were removed in `37ff0586ef92b922465f7cf9dc954e5cfbc38acc` and `00f37a56e3b910903866027a1d57899639a232ab`.

No READY claim is made for this new slice until canonical ATHENA Quality succeeds on this handoff head or an exact descendant carrying the same product/test blobs.

## Coordination / collision avoidance

- Backend active head checked: `9dc8375399c6b07f9c52545783004607aa9dd430`; Backend/System work remains disjoint from Personal-Memory review composition.
- UI and Error handoffs were checked on current Develop; neither claims this Memory composition path.
- Integrator handoff was checked before mutation; current Develop had not integrated this acceptance slice.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Retained release/runtime invariants

Do not regress Windows pypdf distribution metadata, frozen unknown-argv fail-closed routing, Desktop/Worker two-EXE topology, bounded/non-growing worker process tree, adaptive 2048-context DirectChat reserve/safety guard, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster, or storage-bootstrap/migration startup invariants. Historical signatures reopen only on current exact-SHA reproduction.

## Next Alpha/Beta gap

First consume canonical Quality for this exact product/test lineage. If green, hand the exact READY SHA to Integrator, then select the highest evidence-backed bounded Core gap. A natural next Personal-Memory slice is durable review-decision identity/idempotency so the same reviewed proposal cannot be accepted twice without an explicit distinct decision, but do not implement it unless current Beta/spec and persistence contracts support it without synthetic provenance or destructive merge semantics.

Normal-Hybrid Search remains previously verified/integrated; do not reopen or broaden Archive/Protected Search semantics without new evidence.
