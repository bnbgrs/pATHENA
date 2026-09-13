# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Integration target checked first: `develop/pathena-next@1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`.
- Worker before this repair: `postmerge/spec-core@36452888894de49fdcd9b1968d1eaf83bc4412b0`.
- Canonical Quality `34786426851 = SUCCESS` on exact worker `36452888...`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — exact Focused mypy diagnostic repair

The exact diagnostics artifact from Core Focused `34786426823` proves the Merge/Split product code, Ruff and focused pytest were green (`9 passed`). The only failure was changed-file mypy on `tests/unit/test_knowledge_merge_split_policy.py`: two intentional invalid-argument tests placed `# type: ignore[arg-type]` on the call line rather than the offending keyword-argument line. Strict mypy therefore emitted two `unused-ignore` errors plus the two un-suppressed `arg-type` errors.

This repair moves each narrow ignore to the exact intentionally invalid argument. Assertions and runtime validation remain unchanged: the tests still prove fail-closed rejection of a string entity ID and a list used where a tuple is required. No Skip/XFail, strictness reduction, workflow weakening, or product-semantics change is introduced.

The current Develop CI hardening commit is included history-preservingly in the same candidate lineage; there is no sync-only productless commit.

## Product invariants retained

- merge requires two distinct canonical entity IDs;
- retaining one existing merge identity supersedes only the absorbed identity;
- a new merge identity supersedes both originals;
- split requires at least two unique result IDs;
- split result IDs cannot recycle the source identity;
- source identity remains historically superseded after split;
- non-UUID identities and non-tuple split result containers fail closed at runtime;
- the planner does not authorize semantic merges, generate IDs, persist entities, fabricate provenance, or perform Storage work.

## Ownership boundaries

- No UI, Storage, Recovery, Transport or Security semantics changed.
- Durable transaction execution and provenance for actual Merge/Split persistence must reuse existing repository/service boundaries.
- Durable B05 revalidation execution remains Backend/System-owned beyond current Core planning semantics.
- Persisted Knowledge -> ProcessingRun -> ModelSignature remains dependent on real Backend/Storage provenance.

## Next distinct Core gap

After exact-SHA focused and canonical qualification, re-read current Develop and current handoffs. Highest known independent composition target remains exposing the existing `KnowledgeInspectionService` through `CoreApiFacade` and `AthenaApplication` without introducing a parallel API. If that composition is blocked, select the next independent current Alpha/Beta Core product gap rather than revisiting CLOSED temporal-staleness or semantic-identity work.
