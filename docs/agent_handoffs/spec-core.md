# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Integration target: `develop/pathena-next@a9aaf5f414b7a030598d1735244bcbf6407e6bcb`.
- Worker before this slice: `postmerge/spec-core@af5283d7a6c6c5f1e256af1b2f07678ab52cd87b`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Exact worker Quality run `34774353839` completed SUCCESS before this mutation.
- Current Error handoff reports no OPEN error; Backend/UI historical priorities are non-authoritative unless their signatures recur on current Develop.

## Current gap selection

The highest central composition gap remains exposing the existing `KnowledgeInspectionService` through `CoreApiFacade` and `AthenaApplication`. The available mutation interface for those broad central files is complete-file replacement only, so this run does not risk a non-surgical reconstruction.

The next independent B05 gap is the semantic-identity guard from Beta 05 §§37-38: `same_as` is strong and string similarity alone is insufficient; confirmed `different_from` must prevent accidental identity collapse. The existing `RelationTypeRegistry` defines and canonicalizes both relation types but does not decide whether evidence is sufficient to materialize `same_as`.

## Product slice — identity relation evidence gate

Added `src/athena/knowledge/identity_relation_policy.py` as a deterministic, persistence-neutral policy. It never creates relations, provenance or truth state.

Rules:

- string similarity alone -> `REQUIRE_REVIEW`;
- explicit semantic identity without conflicting distinction -> `ALLOW_SAME_AS`;
- explicit `different_from` -> `KEEP_DISTINCT`;
- conflicting explicit identity/distinction -> `REQUIRE_REVIEW`;
- no identity evidence -> `REQUIRE_REVIEW`;
- runtime signals must be genuine booleans.

Focused acceptance is `tests/unit/test_knowledge_identity_relation_policy.py` and covers all branches plus fail-closed input validation.

## Ownership boundaries

- No UI files changed.
- No Storage/Recovery/Transport/Security semantics changed.
- No job/scheduler implementation duplicated.
- No provenance, Source, Claim or Relation is fabricated.
- Durable B05 revalidation execution remains Backend/System-owned beyond the existing Core planning semantics.
- Persisted Knowledge -> ProcessingRun -> ModelSignature linkage remains dependent on real Backend/Storage provenance.

## Qualification state

Fresh exact-SHA focused and canonical evidence is required for the new candidate. Do not claim READY until both complete without a candidate-specific regression.

## Next distinct Core gap

After qualification of this slice, re-read then-current Develop. Prefer the existing `KnowledgeInspectionService` central Facade/Application composition if a safe surgical mutation path is available; otherwise take the next independent Alpha/Beta Core gap backed by current specs/code rather than revisiting closed stale-knowledge work.
