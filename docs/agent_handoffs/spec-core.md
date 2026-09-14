# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop checked first: `develop/pathena-next@f8a25be7fd7df9f2a8ca281a1567f79ddaabcfb6`.
- Develop canonical Quality `34883442620 = SUCCESS`.
- Worker before this candidate: `postmerge/spec-core@63457beb6e96fb4dc48b3b1b217bcefab90c4a22`.
- The previous Knowledge-read build+attach slice is integrated in Develop and is CLOSED.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current Core slice — AthenaApplication Knowledge-read wiring

This candidate consumes the already integrated `attach_knowledge_read_api()` boundary from current Develop and wires it into `AthenaApplication` using the existing canonical `self.knowledge` and `self.api` instances.

Product contract:

- `AthenaApplication` retains the exact `KnowledgeReadApiService` returned by `attach_knowledge_read_api()` as `self.knowledge_read`;
- `CoreApiFacade` receives that exact same service instance;
- capability disclosure for `knowledge.read.why_known` and `knowledge.read.revision_history` therefore comes from a real attached service, not synthetic feature flags;
- Why-known reads use the existing persisted Knowledge provenance inputs;
- revision history uses the existing immutable Knowledge revisions and derives predecessor diffs on read;
- no new repository, storage, DTO, audit or provenance architecture is introduced.

Focused acceptance in `tests/unit/test_knowledge_application_read.py` starts a real temporary SQLite-backed Core, promotes a persisted chat message into canonical Knowledge, proves exact service identity and capability exposure, validates recorded source provenance, creates a direct user revision, and validates immutable two-revision history plus the derived body diff.

## Baseline / collision discipline

The candidate tree is based on exact current Develop and is committed with the previous worker plus exact current Develop as parents. This is a history-preserving NON-FORCE synchronization and product mutation in one candidate; no sync-only intermediate head is published.

Ownership remains unchanged: Backend owns deep Storage/transaction/recovery; UI owns Qt/PALLAS presentation; protected-search authorization semantics are not approximated; persistent release guards and no-Skip/XFail policy remain binding.

## Qualification state

Fresh exact-SHA Core Focused and canonical Quality are required. Until they complete, this candidate is not Integrator-ready and `postmerge/spec-core` must remain frozen after publication.

## Next distinct Core gap

After exact qualification and integration, re-read current Develop/Handoffs/coverage and select the highest remaining independent Core composition gap. Do not revisit the closed Knowledge-read attachment/application sequence unless a new exact regression appears.
