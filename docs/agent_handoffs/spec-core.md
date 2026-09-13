# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current Develop inspected first: `develop/pathena-next@7b4779b7be8c19b9ca0acaa57f826d0da8478592`.
- Current Core worker before this candidate: `postmerge/spec-core@77048de78be4dd7ca2555ed1b09e00d088f9c624`; canonical Quality `34756815221 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Current Develop canonical Quality `34758273159 = FAILURE`: specification validation, mypy, full pytest, Windows Path Safety, Linux Storage and Local-install are green; Ruff is the only failing canonical step after the CI-focused-test harness integration.
- That Develop Ruff regression is cross-cutting/Integrator-owned and is not duplicated or weakened by Core.

## Source-of-truth anchors

Beta 05 §63 requires time-dependent Knowledge to be signalable as possibly stale when validity or source age supports it; stale is a maintenance signal, not an automatic falsehood. §64 allows revalidation jobs but forbids deleting old Claims without new evidence.

Current Develop contains two public stale-policy surfaces:

- `src/athena/knowledge/staleness_policy.py` — canonical KnowledgeRevision-aware policy used by revalidation planning.
- `src/athena/knowledge/stale_policy.py` — compatibility-oriented maintenance policy with the same validity/source-age business decision implemented a second time.

That duplicated rule engine is an active Core architecture regression because the two surfaces can drift while representing the same Beta §63 decision.

## Current product slice — consolidate stale decision engine

The candidate preserves both public result contracts while removing the duplicate stale-rule implementation.

- `KnowledgeStalenessPolicy.assess()` now delegates temporal rule evaluation to one shared `_assess_temporal_staleness()` function.
- `StaleKnowledgePolicy.assess()` preserves its existing input validation, enum/result contract and error surface, but delegates the stale decision to the same shared temporal evaluator and only maps canonical reasons into its legacy result type.
- The shared evaluator retains exact-boundary behavior, explicit paired source-age evidence, future-source rejection, simultaneous validity/source-age reasons, and no invented freshness/truth/provenance.
- No repository, Storage, job scheduler, Source, Claim, Knowledge revision or provenance mutation is introduced.

Focused acceptance is added as `tests/unit/test_knowledge_stale_policy_compat.py`, intentionally matching the existing Core-focused `test_knowledge*.py` family. It covers no-evidence, validity stale, source-age stale, multiple signals, exact boundaries, legacy fail-closed validation and future source timestamps, and requires both public surfaces to emit equivalent stale reasons.

## Current Develop blocker

The candidate is based history-preservingly on current Develop, but Integrator-ready status cannot be claimed while current Develop itself is canonical-red solely at Ruff. Core must not repair or weaken that foreign CI harness inside this product slice. Focused Core evidence can still establish whether the consolidation itself is sound; canonical evidence must be interpreted against the already-present Develop Ruff failure.

## Collision avoidance

- Backend retains deep Storage/Recovery/Transport and durable job/scheduler ownership.
- UI retains presentation/styling ownership.
- Integrator/Error owns the current Develop CI-harness Ruff regression.
- Core does not alter `.github/workflows`, the CI regression test, Storage, Security, Recovery or release guards.

## Next distinct Core gaps

1. If the stale-policy consolidation passes focused evidence, keep it bounded and hand off the foreign canonical Ruff blocker precisely rather than changing CI.
2. `KnowledgeReadApiService -> CoreApiFacade -> AthenaApplication` remains a Core-owned composition gap; implement only with a safe surgical patch path and exact capability/delegation/application identity tests.
3. B05 §64 durable revalidation execution remains Backend/System-owned beyond the existing Core revalidation planner.
4. Persisted Knowledge -> ProcessingRun -> ModelSignature remains a Backend/Storage prerequisite; Core must not synthesize that provenance.
