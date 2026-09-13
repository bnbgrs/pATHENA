# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Integration target: `develop/pathena-next@72ab7085f40afa74c0334b698dffc3462665d366`.
- Worker before this slice: `postmerge/spec-core@97bb3c13d6c6a1911b631f0b9d511d0c10c5cc71`.
- Current Develop canonical Quality `34779068839` completed SUCCESS before mutation.
- The semantic-identity guard from the previous worker is integrated in Develop and is CLOSED.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current gap selection

The highest composition gap remains exposing the existing `KnowledgeInspectionService` through `CoreApiFacade` and `AthenaApplication`. It touches broad central files and was not selected for this atomic slice because a smaller independent normative B05 gap can be completed without introducing a parallel API or unsafe partial composition.

Beta 05 §§51-52 require explicit identity/supersession behavior for Merge and Split: an authorized merge may retain one existing identity or use a new ID while absorbed/original IDs remain historically superseded; a split creates new independently addressable IDs while retaining the source historically as superseded. Current deduplication produces merge candidates but does not encode these identity consequences as a reusable Core invariant.

## Product slice — Merge/Split identity planning

Added `src/athena/knowledge/merge_split_policy.py` as a deterministic, persistence-neutral planning boundary.

Rules:

- merge requires two distinct canonical entity IDs;
- retaining the left identity supersedes only the right identity;
- retaining the right identity supersedes only the left identity;
- using a new merge identity supersedes both originals;
- split requires at least two unique result IDs;
- split result IDs must be new relative to the source ID;
- a valid split always marks the source ID as historically superseded;
- all identity inputs fail closed unless they are UUIDs;
- the planner does not authorize semantic merges, generate IDs, persist entities, fabricate provenance, or perform Storage work.

Focused acceptance is `tests/unit/test_knowledge_merge_split_policy.py` and covers both retained-identity merge paths, new-identity merge, same-ID rejection, valid split, insufficient/duplicate/source-ID split rejection, and fail-closed runtime identity validation.

## Ownership boundaries

- No UI files changed.
- No Storage/Recovery/Transport/Security semantics changed.
- No job/scheduler implementation duplicated.
- No Source, Claim, Relation, provenance record, audit record, or canonical entity is fabricated by this planner.
- Actual atomic persistence of merge/split plus provenance remains repository/service integration work and must reuse existing durable transaction boundaries.
- Durable B05 revalidation execution remains Backend/System-owned beyond existing Core planning semantics.
- Persisted Knowledge -> ProcessingRun -> ModelSignature linkage remains dependent on real Backend/Storage provenance.

## Qualification state

Fresh exact-SHA focused and canonical evidence is required for this candidate. Do not claim READY until both complete without a candidate-specific regression.

## Next distinct Core gap

After qualification, re-read current Develop and handoffs. Prefer `KnowledgeInspectionService` central Facade/Application composition if it can be performed atomically and safely. Otherwise continue B05 with actual merge/split persistence integration or another independent current Alpha/Beta Core gap; do not revisit CLOSED stale-knowledge or semantic-identity slices.
