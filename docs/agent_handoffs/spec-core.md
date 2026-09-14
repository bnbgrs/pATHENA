# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop checked first: `develop/pathena-next@3a8120805e41d0fe9d283fc948d6e52b327a8e58`.
- Develop canonical Quality `34893392725 = SUCCESS`.
- Worker before this candidate: `postmerge/spec-core@9fe5dd44473ae200941d40ba37d14bc8816fdcdf`.
- The Knowledge-read application chain is integrated in Develop and CLOSED.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current Core slice — Research API projection

Current Develop contains a real durable `ResearchService` with local Exhaustive Research enqueue semantics, but the API layer has no Research-facing projection. This slice adds `athena.api.research.ResearchApiService` as a transport-neutral adapter over the existing enqueue boundary.

Product contract:

- local Exhaustive Research remains owned by the existing durable Research orchestrator;
- the API adapter delegates query, priority, coverage target, and requested model identity without reimplementing Research scheduling;
- the returned API response projects the durable job's exact identity, type, priority, and state;
- no fake Research data, synthetic provenance, repository bypass, storage path, scheduler duplicate, or new Research engine is introduced.

Focused acceptance in `tests/unit/test_api_research.py` verifies exact delegation and proves that durable job identity/type are projected rather than regenerated or rewritten.

## Collision discipline

Backend retains Storage/transaction/recovery ownership. UI retains Qt/PALLAS presentation. Security/Protection authorization semantics are unchanged. Persistent release guards and no-Skip/XFail remain binding.

## Qualification state

Fresh exact-SHA Core Focused must pass before canonical Quality is treated as candidate evidence. Until canonical terminal success, no further `postmerge/spec-core` commit may be published.

## Next distinct Core gap

After this adapter is exact-SHA green, re-read current Develop and attach the existing `ResearchApiService` to `CoreApiFacade` with strict single-attach/capability gating, then compose the same real `ResearchService` instance in `AthenaApplication`. Do not reopen the closed Knowledge-read chain without a new exact regression.
