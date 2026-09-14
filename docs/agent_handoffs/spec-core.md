# ALPHA/BETA Core handoff

## Current source of truth

- Develop baseline inspected: `4634af7ab0db315574e692c57635585d3a3b3bf6` (`develop/pathena-next`).
- Worker parent before this slice: `873c6e3e301d319fa7971cedf76fba0b4bf118a7`.
- `main` and `bnbgrs/ATHENA` remain read-only.
- Current Develop already integrates canonical Knowledge Inspection application wiring; that slice is CLOSED and must not be selected again absent a new regression.

## Selected Core gap: canonical Knowledge supersession relation

Beta Knowledge lifecycle requires a superseded entity to remain addressable in history and to be linked explicitly to its successor. Merge/Split already calculates `superseded_entity_ids`, but the versioned Core relation registry had no `superseded_by` relation and therefore no fail-closed canonical edge plan for persisting that identity consequence.

This slice:

- registers directed `superseded_by` for Knowledge-to-Knowledge only;
- adds a persistence-neutral supersession-edge planner;
- preserves predecessor order and historical IDs;
- rejects empty, duplicate, self-superseding, and non-UUID plans;
- fails closed if a custom registry would silently fall back to `related_to`;
- performs no storage write and introduces no parallel transaction/audit path.

Focused acceptance is `tests/unit/test_knowledge_supersession_policy.py` and is intentionally named inside the Core Focused Candidate Knowledge test scope.

## Next distinct Core gap

After exact-SHA qualification/integration, re-read current Develop first. If still absent, prioritize central composition of the existing `KnowledgeReadApiService` through `CoreApiFacade` and `AthenaApplication`, reusing the existing `KnowledgeService` as the real provenance/history reader. Do not create a parallel read API, repository, provenance model, or synthetic source metadata.
