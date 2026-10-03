# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop checked first: `develop/pathena-next@7bd4abfcf40a80c829731427c66d0a3b4aa09d13`.
- Develop canonical Quality `34915516889 = SUCCESS`.
- Worker before this candidate: `postmerge/spec-core@52c4592efeeebec7c1ed3d70949a084b3d8c205f`.
- The Research API projection/qualification slice is integrated in Develop and CLOSED.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current Core slice — canonical Research API builder

The candidate adds `build_research_api()` to the existing `athena.api.research` module. It wraps the exact existing durable Research orchestrator in `ResearchApiService`; it does not create a scheduler, repository, job identity, provenance source, or second Research engine.

Focused acceptance extends `tests/unit/test_api_research.py` and proves the builder delegates through the supplied existing orchestrator and preserves its durable job identity.

The candidate tree is based on exact current green Develop and is committed with previous worker plus exact Develop as parents. No sync-only intermediate head is published.

## Next distinct Core gap

After exact qualification, add ResearchApiService to CoreApiFacade with strict single attach, fail-closed calls, truthful `research.start.local` capability gating, and direct `start_local()` delegation. Then compose the exact adapter from `AthenaApplication.self.research`.
