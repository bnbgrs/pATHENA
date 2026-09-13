# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Current integration target checked first: `develop/pathena-next@ba6bc224cc152c144d13ca21730dad6620610abe`.
- Worker before this regression repair: `postmerge/spec-core@b35033657b2809febb491235bb284b6219975cb2`.
- Prior Develop parent `72ab7085f40afa74c0334b698dffc3462665d366` has canonical Quality `34779068839 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — B05 Merge/Split planner qualification regression

Candidate `b35033657b2809febb491235bb284b6219975cb2` introduced the persistence-neutral merge/split identity planner and its focused acceptance tests. Core Focused `34780613663 = SUCCESS`, while canonical Quality `34780613667 = FAILURE`.

Exact canonical lane evidence:

- specification validator: PASS;
- Ruff: PASS;
- mypy: FAIL;
- full pytest: PASS;
- Linux storage regressions: PASS;
- Local install smoke: PASS;
- Windows path safety and persistent release guards: PASS.

Because exact parent Develop `72ab7085...` was canonical-green and the candidate's only failing canonical step was mypy, this is candidate-specific. The planner used a direct runtime `isinstance(result_entity_ids, tuple)` guard on a parameter statically declared `tuple[UUID, ...]`; repository mypy is strict with `warn_unreachable = true`. The repair preserves the strict public function signature and moves runtime container validation into `_require_uuid_tuple(value: object, ...)`, matching the existing `_require_uuid(value: object, ...)` fail-closed pattern. No Merge/Split semantics or acceptance assertions are weakened.

The repaired product/test slice is carried on current Develop content in one history-preserving product commit; there is no sync-only commit.

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

After exact-SHA focused and canonical qualification of this repair, re-read current Develop and handoffs. Highest known independent composition target remains exposing the existing `KnowledgeInspectionService` through `CoreApiFacade` and `AthenaApplication` without introducing a parallel API. If that cross-file composition is unsafe or blocked, select the next independent current Alpha/Beta Core product gap rather than revisiting CLOSED temporal-staleness or semantic-identity work.
