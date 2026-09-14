# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop baseline used for this slice: `develop/pathena-next@8a8f7e716075e6248214b15563a0e282aba7723c`.
- Worker before this slice: `postmerge/spec-core@52b4e322041547e9039a0f3026f6747583605914`.
- Develop exact canonical Quality `34800785441` is `success`.
- `main` and `bnbgrs/ATHENA` remain read-only.

Historical Search/Merge-Split worker notes in earlier handoffs are not authoritative for current priority. Merge/Split is integrated/closed; normal Hybrid Search composition already exists on current Develop.

## Selected current Core gap

Beta chapter 05 §§39-40 requires Project to remain a Knowledge entity and permits one KnowledgeUnit to belong to multiple projects through `belongs_to_project` or an equivalent relational link.

Current Develop already has:

- `KnowledgeKind.PROJECT_KNOWLEDGE`;
- the curated `belongs_to_project` relation definition;
- a directed `knowledge -> project` domain constraint in `RelationTypeRegistry`.

The missing Core behavior is a deterministic membership planner that validates canonical project targets, preserves multiple distinct project memberships, collapses duplicate targets without inventing edges, and fails closed if the registry silently falls back away from `belongs_to_project`.

## Product slice

`src/athena/knowledge/project_membership.py` adds `ProjectMembershipPlan` and `plan_project_memberships()`.

The planner:

- accepts canonical `KnowledgeUnitSnapshot` values only;
- requires at least one target;
- requires every target to use `KnowledgeKind.PROJECT_KNOWLEDGE`;
- uses the existing `RelationTypeRegistry` and its established `belongs_to_project` definition;
- preserves multiple distinct project memberships in first-seen order;
- collapses duplicate target IDs to a single edge;
- rejects missing/deprecated/fallback membership semantics;
- does not persist relations, synthesize IDs, create provenance, or bypass repository/storage ownership.

`tests/unit/test_knowledge_project_membership.py` covers multi-project membership, duplicate collapse, non-project rejection, empty input, wrong collection type, and registry fallback rejection.

A local focused logic harness using the same planner/registry contract completed `6 passed`; exact repository focused and canonical evidence must be taken from the candidate SHA after publication.

## Ownership and collision avoidance

- KnowledgeInspection -> `CoreApiFacade` -> `AthenaApplication` remains the higher-priority composition gap, but the available mutation interface still makes safe surgical replacement of the broad existing facade/application files impractical in this run. No parallel facade or domain-object leakage was introduced.
- Durable relation persistence/provenance remains bound to existing repository/storage transaction paths; this slice only plans validated Core edges.
- UI/PALLAS visual lifecycle work remains UI-owned.
- Deep storage/system work remains Backend-owned.

## Next distinct Core gap

After exact focused/canonical qualification of this candidate and Integrator consumption, re-read current Develop and handoffs. Prefer safe central composition of the existing `KnowledgeInspectionService` if a surgical path is available; otherwise continue with the next independent Alpha/Beta Core functionality gap without revisiting closed Merge/Split or stale historical Search work.
