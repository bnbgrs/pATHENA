# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop checked first: `develop/pathena-next@3a8120805e41d0fe9d283fc948d6e52b327a8e58`.
- Develop canonical Quality `34893392725 = SUCCESS`.
- Worker before repair: `postmerge/spec-core@95a60521bb06cb883e14bdc5803181b224f53f64`.
- The Knowledge-read application chain is integrated in Develop and CLOSED.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current Core slice — Research API projection

Current Develop contains a real durable `ResearchService` with local Exhaustive Research enqueue semantics. `athena.api.research.ResearchApiService` is a transport-neutral adapter over that existing enqueue boundary.

Product contract:

- local Exhaustive Research remains owned by the existing durable Research orchestrator;
- the API adapter delegates query, priority, coverage target, and requested model identity without reimplementing Research scheduling;
- the returned API response projects the durable job's exact identity, type, priority, and state;
- no fake Research data, synthetic provenance, repository bypass, storage path, scheduler duplicate, or new Research engine is introduced.

`tests/unit/test_api_research.py` verifies exact delegation and durable job identity/type projection.

## Current regression evidence

Exact worker `95a60521bb06cb883e14bdc5803181b224f53f64` produced two separate qualification findings:

- Core Focused run `34898273973`: immutable checkout, Ruff, mypy, and changed focused pytest all completed successfully; only the final outcome-enforcer step failed. The changed-file selector contained a double `.py` suffix requirement for `src/athena/api/(knowledge_.*|research)`, so the selector contract itself was malformed. The repair removes the inner suffix and retains the single outer `\.py$`; no lint/type/test guard is relaxed.
- Canonical Quality run `34898274002`: Windows path/storage/API/lifecycle/packaging guards, Linux storage, local-install/Core-restart/pypdf, specification validator, Ruff, and mypy succeeded. Only full pytest failed. Canonical diagnostics artifact `10370332645` exists for exact SHA `95a60521bb06cb883e14bdc5803181b224f53f64`; its exact failing-test signature must be consumed before any candidate-owned pytest repair is attempted.

## Collision discipline

Backend retains Storage/transaction/recovery ownership. UI retains Qt/PALLAS presentation. Security/Protection authorization semantics are unchanged. Persistent release guards and no-Skip/XFail remain binding.

## Qualification state

The focused selector repair is a guard correction, not a guard relaxation. After the repaired exact SHA is published, consume its Core Focused evidence first. Because canonical Quality is also expected to start automatically, do not publish another worker commit until that canonical run is terminal. If canonical full pytest remains red, repair only an exact candidate-owned failure; otherwise hand off unrelated regressions to their owner.

## Next distinct Core gap

After the Research adapter and guard are exact-SHA green and integrated, re-read current Develop and attach the existing `ResearchApiService` to `CoreApiFacade` with strict single-attach/capability gating, then compose the same real `ResearchService` instance in `AthenaApplication`. Do not reopen the closed Knowledge-read chain without a new exact regression.
