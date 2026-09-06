# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@14ca6fece527d6b51956b3e5fa3ec7b291252420`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `b306f486c387d83ddf6ab4f5267835fec9ef47b2`, parents prior Core head `b4d7ac9d0102981b133983c5fa93e113e2df4360` and exact current Develop `14ca6fece527d6b51956b3e5fa3ec7b291252420`.

## READY — explicit reviewed Personal-Memory inference acceptance

Product/test commit: `f4a793171e56305f47e49d177e16287619b943bf`.
Exact verified descendant: `b4d7ac9d0102981b133983c5fa93e113e2df4360`.
Canonical ATHENA Quality: `34013788076 = success`.
Focused mutation/verification run: `34013731297 = success`.

Contract verified:

- model-inferred default-suggest remains non-canonical and review-gated;
- `PersonalMemoryService.accept_model_inferred()` is an explicit Human-Control boundary;
- accepted Memory retains `MODEL_INFERRED` mode and confidence;
- exact `model_signature_id` and `processing_run_id` persist durably through provenance;
- repository rejects half-present model provenance;
- explicit-user writes retain NULL model provenance;
- acceptance creates a distinct canonical Memory and does not silently overwrite an existing explicit-user revision;
- SENSITIVE/PROTECTED inferred content remains fail-closed before canonical persistence.

Real SQLite acceptance: `tests/unit/test_personal_memory_review_acceptance.py`.

## Current synchronization

The exact verified Core delta (`src/athena/memory/models.py`, `src/athena/memory/repository.py`, `src/athena/memory/service.py`, and the two focused Memory acceptance files) was overlaid onto exact current Develop and committed with two parents at `b306f486c387d83ddf6ab4f5267835fec9ef47b2`. Ref movement was NON-FORCE only. Develop/main/ATHENA were not mutated.

## Coordination / collision avoidance

- Backend active head checked: `20edbed46471a50e72661e2e69502b094a0b599f`; system/transport scope remains disjoint.
- UI active head checked: `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`; presentation/focus scope remains disjoint.
- Error active head checked: `3392f70d4c4c0830fefe2833d098bed34fa2127b`; no current exact-SHA Core blocker was claimed.
- Integrator handoff on current Develop was checked before synchronization and had the Core review-acceptance slice still pending canonical verification.

## Next Alpha/Beta gap

Beta Personal Memory requires explicit user authority over inferred suggestions and explicit-user changes to outrank automatic inference. The current reviewed-inference acceptance can canonize the same in-memory proposal more than once because no durable proposal/review-decision identity is currently bound to canonicalization. Before changing persistence, verify whether the repository-wide provenance/review contracts provide an existing durable identity field suitable for idempotent acceptance. If such a field exists, implement the smallest fail-closed one-decision/one-canonicalization contract with real SQLite acceptance. If not, do not synthesize identity or add a deep storage migration in Core; record the concrete composition blocker and immediately select the next disjoint evidence-backed Core gap.

Normal-Hybrid Search remains previously verified/integrated and must not be reopened or broadened. PALLAS remains data-driven only.

## Retained release/runtime invariants

Do not regress Windows pypdf distribution metadata, fail-closed frozen unknown-argv routing, Desktop/Worker two-EXE topology, bounded/non-growing workers, adaptive 2048-context DirectChat reserve/safety guard, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster, or storage-bootstrap/migration startup invariants. Historical signatures reopen only on current exact-SHA reproduction.
