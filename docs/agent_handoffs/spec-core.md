# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@8236500a5ae0ae58e7dce5bb3cf0771eb534670d`.
- Worker branch: `postmerge/spec-core`.
- Verified provenance product/test head before synchronization: `e5a6c6bd2c84ec6101b93a354ef2515b240fd353`.
- Canonical ATHENA Quality: `34018695781 = success` on exact head `e5a6c6bd2c84ec6101b93a354ef2515b240fd353`.
- History-preserving NON-FORCE synchronization: `d82c0260abdea2c6133cf90f6624ddfff4b5aa88`, parents exact verified Core head plus exact current Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## READY — model-inferred Personal-Memory provenance runtime boundary

Product commit: `450590be1a0d658ecf3666a99ab60627d5dd145a`.
Focused test commit / exact green head: `e5a6c6bd2c84ec6101b93a354ef2515b240fd353`.
Canonical Quality: `34018695781 = success`.
Status: `VERIFIED / READY_FOR_INTEGRATOR`.

Contract verified:

- `model_signature_id` must be a real `uuid.UUID` before a model-inferred proposal crosses the Core boundary;
- `processing_run_id` must be a real `uuid.UUID` before the proposal crosses the Core boundary;
- `review_required` must be exact boolean `True`, not a truthy substitute;
- `MODEL_INFERRED`, confidence and NORMAL-sensitivity requirements remain enforced;
- default-suggest remains non-canonical and review-gated;
- previously verified explicit review acceptance and durable model/processing provenance persistence are preserved;
- explicit-user Memory semantics remain unchanged;
- no synthetic provenance, Archive/Protected expansion, Search broadening or PALLAS fake data was introduced.

Current Develop already integrates the earlier reviewed-inference acceptance (`src/athena/memory/repository.py`, `src/athena/memory/service.py`, `tests/unit/test_personal_memory_review_acceptance.py`). Synchronization therefore overlays only the still-missing verified provenance-boundary blobs (`src/athena/memory/models.py` and `tests/unit/test_personal_memory_inferred_provenance_validation.py`) onto the exact current Develop tree.

## Coordination state

- Error worker: `postmerge/errors@0049ca90d1687b1c5ea8722895e1c9f2a1fe9e76`; `ERR-0016` is OPEN and Backend-owned (local HTTP overflow poisoning), disjoint from Core Memory work.
- Backend worker: `postmerge/backend@a5904fc2078a8dec5eece17dd352436d14453d8f`; current Provider work is NOT READY while canonical failures remain, disjoint from Core Memory work.
- UI worker: `postmerge/ui@089a0e4b0b8fc43e37f00f8288f64cd62014fbb4`; Research-detail focus presentation is disjoint from Core Memory work.
- Integrator on Develop explicitly requested review of `e5a6c6bd2c84ec6101b93a354ef2515b240fd353` once exact-green evidence was bound; that condition is now satisfied.

## Normal-Hybrid Search

Normal-Hybrid Search facade/application composition remains `VERIFIED` on Develop. One-time attachment, capability gating, exact delegation, canonical DTO mapping, propagation of semantic retrieval failure and application wiring identity are already integrated. This run does not reopen or broaden Search, Archive or Protected semantics.

## Persistent Beta/release regression knowledge

Retain as explicit candidate regression requirements: Windows `pypdf` metadata packaging; fail-closed frozen child argv and two-EXE Desktop/Worker split; exactly one Desktop with bounded/non-growing workers; 2048-context adaptive Chat output reserve; lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; and `Failed to start service 'storage-bootstrap'`. Reopen as current defects only on exact-SHA reproduction.

## Next Core gap

Durable review-idempotency remains blocked because no existing Personal-Memory proposal/review-decision identity contract was found; Core must not invent a synthetic durable identity or perform unowned storage migration.

The next disjoint evidence-backed Core gap is Beta Personal Memory §28, `Why is this remembered?`: expose a transport-neutral, non-synthetic explanation derived only from the current canonical Memory revision (`learning_mode`, current revision timestamp, confirmation timestamp and stable IDs). It must distinguish explicit-user, accepted model-inferred and imported origin without inventing source facts, must perform no writes, and must preserve protected-content and Human-Control boundaries. Add focused real-repository acceptance before canonical Quality and Integrator handoff.
