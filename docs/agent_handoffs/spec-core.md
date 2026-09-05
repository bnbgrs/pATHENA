# pATHENA Alpha/Beta Core Handoff

## Current state

- Baseline: `develop/pathena-next@4ce70615cffcbf0e76ec404e7e58b34c7c5e308a`.
- Worker: `postmerge/spec-core`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Historical Backfill exact product/test head: `1bf7a9947a004b813924c91aad105fe2eacffa56`.
- Canonical ATHENA Quality: `33965803951 = success` on that exact head.
- History-preserving NON-FORCE synchronization onto current Develop: `ce2c3a8dce06a94a1e9e966218ab594864637fad`, parents `1bf7a9947a004b813924c91aad105fe2eacffa56` and `4ce70615cffcbf0e76ec404e7e58b34c7c5e308a`.

## READY — Historical Backfill Research

Verified exact blobs carried by the synchronized worker:

- `src/athena/research/service.py@902ab0423b8d63cd4ee7e16f60cb45fcd389264d`;
- `src/athena/jobs/payload_validation.py@171fddf4c8d2bd2643fffdb338a19976ede645d8`;
- `tests/unit/test_research_historical_backfill.py@1340b5ce4d63d6c317321c44a1d3fe231d1b7c02`.

Product contract:

- explicit `enqueue_historical_backfill()` persists truthful `ResearchMode.HISTORICAL_BACKFILL`;
- both time bounds are mandatory, non-negative genuine integers; bool is rejected;
- end before start fails closed before persistence;
- durable `research.exhaustive` payload validation independently enforces the historical-backfill bounds;
- existing local/scoped-project behavior, snapshot pinning, candidate dedup identity, model parameters, coverage and null `internet_scope` remain unchanged;
- no implicit external access and no synthetic source/claim/evidence/provenance/PALLAS data.

Status: `VERIFIED_ON_WORKER / READY_FOR_INTEGRATOR_REVIEW`.

## Previously verified/integrated Core slices

- Normal Hybrid Search facade/application composition: verified and integrated.
- Production contradiction acceptance temporal + attribution gate: verified and integrated.
- Fenced Research durable source coverage: verified and integrated.
- Scoped Project Research: verified and integrated.

## Coordination

- Backend current head reviewed: `postmerge/backend@1cc0017d560a1534de1fc2c83989d26e05238236`; no Core collision identified.
- UI current head reviewed: `postmerge/ui@77b3f9582d4530dbe081e3c81b8768ad00d3f050`; UI presentation ownership remains separate.
- `errors.md`, `backend.md`, `ui.md`, and `integrator.md` on current Develop were reviewed before mutation.
- Integrator has already integrated Scoped Project Research; Historical Backfill is the new Core READY input.

## Next Core gap

Select the next highest bounded Alpha/Beta Core gap from current specs/code after excluding completed Search, contradiction acceptance, source coverage, Scoped Project, and Historical Backfill. Any Local-plus-Web Research work must remain authorization/provenance-first and must not reuse the local null-Internet path as an implicit external-access grant.
