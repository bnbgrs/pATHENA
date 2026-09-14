# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop checked first: `develop/pathena-next@6a7280ef9847c61c3c3b532c1e3a14068ae14583`.
- Develop canonical Quality `34907353758` is still `IN_PROGRESS`; no Develop sync is performed until that exact baseline is terminal green.
- Worker before this repair: `postmerge/spec-core@1ae84717c80b31664cfecf35d614cb4450076c44`.
- The Knowledge-read application chain is integrated in Develop and CLOSED.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current Core slice — Research API projection qualification repair

Current worker contains `athena.api.research.ResearchApiService`, a transport-neutral adapter over the existing durable local Exhaustive Research enqueue boundary. The adapter delegates query, priority, coverage target, and requested model identity directly and projects only the durable job identity, type, priority, and state.

The exact prior worker `1ae84717c80b31664cfecf35d614cb4450076c44` produced two candidate-owned qualification defects:

1. Core Focused `34903109878` selected `src/athena/api/research.py` correctly after the selector repair, but mypy rejected the mutable-attribute Protocol contract against the real immutable/frozen durable job projection. The repair changes `ResearchJobLike` to read-only Protocol properties; no cast, ignore, skip, XFail, or mypy relaxation is introduced.
2. Canonical Quality `34903109969` passed specification validation, Ruff, mypy, Windows release guards, Linux storage, and local-install/Core-restart/pypdf, then failed full pytest only in stale Core-focused workflow contract expectations that still described the pre-Research selector. Those tests are updated to require the restrictive Research-inclusive selector and explicit Research trigger paths.

Product invariants remain unchanged:

- the existing durable Research orchestrator remains authoritative;
- no fake Research data or synthetic provenance;
- no repository, scheduler, transaction, or storage bypass;
- no parallel Research engine;
- persistent release guards remain unchanged;
- no Skip/XFail or guard weakening.

## Current Develop compatibility

Develop moved from the worker's last green parent to `6a7280ef9847c61c3c3b532c1e3a14068ae14583` through the Backend-owned durable Deep verification pipeline. Its canonical Quality is still active. This worker repair intentionally does not merge or rewrite that unqualified Develop baseline. Once Develop is exact-SHA green, compatibility must be rechecked and incorporated history-preservingly together with the next real Core product slice rather than as a sync-only published head.

## Collision discipline

Backend retains Storage/transaction/recovery ownership, including the new durable Deep verification pipeline. UI retains Qt/PALLAS presentation. Security/Protection authorization semantics are unchanged. Core owns the Research transport-neutral API/facade/application composition only.

## Qualification state

After this atomic repair is published, consume exact-SHA Core Focused first. Do not publish any further worker commit once canonical Quality starts for the repaired candidate until that run is terminal. Integrator-ready remains forbidden until both exact focused and canonical evidence are green on a current-compatible Develop lineage.

## Next distinct Core gap

After the Research adapter/qualification repair is exact-SHA green and current Develop is terminal green, re-read current handoffs/specs/coverage and history-preservingly incorporate exact Develop in the same candidate as the next real product mutation. Highest verified next gap remains `ResearchApiService -> CoreApiFacade`: strict single attach, fail closed before attachment, truthful capability gating, and direct `start_local` delegation. Then compose that exact API service from the existing `AthenaApplication.self.research`. Do not reopen Knowledge-read without a new exact regression.
