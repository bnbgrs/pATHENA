# ALPHA/BETA Core handoff

## Current source of truth

- Develop baseline inspected: `0ea74a990f8375039769c7726a327fd9142d5985` (`develop/pathena-next`).
- Worker candidate before this repair: `f5013995078ce355e64fe4dd7bd7c2a549a30ef9`.
- `main` and `bnbgrs/ATHENA` remain read-only.
- Current Develop adds only the independently integrated PALLAS semantic-token cache relative to this Core candidate's prior Develop baseline; the merge is disjoint from the Knowledge supersession slice.

## Selected Core gap: canonical Knowledge supersession relation

Beta Knowledge lifecycle requires a superseded entity to remain addressable in history and to be linked explicitly to its successor. Merge/Split already calculates `superseded_entity_ids`, but the versioned Core relation registry had no `superseded_by` relation and therefore no fail-closed canonical edge plan for persisting that identity consequence.

The candidate registers directed `superseded_by` for Knowledge-to-Knowledge only and adds a persistence-neutral supersession-edge planner. It preserves predecessor identities and order, rejects empty, duplicate, self-superseding and malformed plans, and refuses silent fallback to `related_to`. No storage write, transaction path, audit path, fake data or synthetic provenance is introduced.

## Canonical regression and repair

- Core Focused Candidate `34838026579` on exact `f5013995078ce355e64fe4dd7bd7c2a549a30ef9`: SUCCESS.
- Canonical Quality `34838026561` on the same SHA: FAILURE only in full pytest.
- Exact canonical log: `5164 passed, 17 skipped`; the sole failure was `tests/unit/test_relation_registry_contract.py::test_unknown_relation_type_falls_back_without_ontology_growth`.
- Root cause: the pre-existing contract test hard-coded the old four canonical relation names, so adding the intentional fifth canonical relation `superseded_by` made that stale expectation fail. The new supersession-policy tests themselves passed.
- Repair: the contract now snapshots registry definitions before resolving an unknown relation and requires the definitions to remain byte-for-byte semantically unchanged afterward; it also requires `superseded_by` to be present in the canonical registry. This strengthens the actual anti-ontology-growth invariant rather than weakening or skipping it.

## Next distinct Core gap

After exact-SHA Focused and canonical qualification/integration, re-read current Develop first. If still absent, prioritize central composition of the existing `KnowledgeReadApiService` through `CoreApiFacade` and `AthenaApplication`, reusing the existing `KnowledgeService` as the real provenance/history reader. Do not create a parallel read API, repository, provenance model or synthetic source metadata.
