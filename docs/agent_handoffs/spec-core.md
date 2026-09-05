# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Integration baseline: `develop/pathena-next@49212a0f157d433d68e9d04e9a9643e2909b6827`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Worker: `postmerge/spec-core`.
- Verified product/test head: `2f62d2a26f9341e7ea8c84abe2ae48762bfe117c`.
- Canonical ATHENA Quality: `33977608224 = success` on that exact head.
- History-preserving NON-FORCE synchronization with current Develop: `015b0e39376d03bfaea21c6a1e26efa93f6819c3`, parents `2f62d2a26f9341e7ea8c84abe2ae48762bfe117c` and `49212a0f157d433d68e9d04e9a9643e2909b6827`.

## READY slice — Historical Backfill persisted Source boundaries

The focused acceptance in `tests/unit/test_research_historical_backfill.py` uses the real `AthenaApplication` and `SourceCaptureService`/`SourceRepository` persistence path. It proves Historical Backfill candidate discovery against the production `_select_sources_as_of()` contract:

- durable Sources immediately below/start/end/above the requested interval are captured through the real Source persistence path;
- the Research scope is initialized after those captures, pinning `snapshot_commit_seq`;
- another in-window Source is captured only after the pinned snapshot;
- `freeze_local_candidates()` selects exactly the start/end boundary Sources;
- below/above-window Sources are excluded;
- the in-window Source committed after the pinned snapshot is excluded.

Production selection already enforces inclusive `acquired_at_us >= time_start_us` and `acquired_at_us <= time_end_us` together with pinned commit/evidence-scope visibility, so this slice required no speculative production rewrite.

## Preserved contracts

- truthful `ResearchMode.HISTORICAL_BACKFILL` remains unchanged;
- snapshot identity and commit visibility remain authoritative;
- no direct schema fixture or synthetic provenance was introduced;
- no Project/Domain/Internet/Protected/Archive scope broadening;
- no synthetic Sources, Claims, Evidence or PALLAS data;
- no Security, Storage, Transport, Recovery or UI behavior changed.

## Integrator handoff

READY for independent integration review:

- exact verified head: `2f62d2a26f9341e7ea8c84abe2ae48762bfe117c`;
- exact test blob: `tests/unit/test_research_historical_backfill.py@c25b4ac25fd84fe0ce6a0174c1665120d17b8284`;
- Quality: `33977608224 = success`;
- current-Develop synchronization head: `015b0e39376d03bfaea21c6a1e26efa93f6819c3`.

Current Develop changes since the verified head are disjoint: Integrator handoff plus disk-pressure product/test changes. The synchronization tree is based on current Develop and overlays only the exact verified Historical Backfill test blob.

## Coordination

- Backend worker observed at `postmerge/backend@5b04d7e335823f59bd33847e5b5c2c5b7e23458c`; its disk-pressure work is disjoint.
- Error handoff reports no open Core blocker on current Develop.
- UI handoff remains presentation-owned and disjoint from Research Core.
- Integrator explicitly prefers a newer exact-green bounded Core successor when available.

## Next Core gap

Select the highest currently unclaimed Alpha/Beta Core composition gap after excluding already verified normal-Hybrid Search, contradiction acceptance, Research source coverage, Scoped Project Research, Historical Backfill entrypoint/payload/candidate-freeze, and this persisted Source boundary acceptance. Preserve authorization-first semantics for any Internet/Protected/Archive work and do not widen a local Research path implicitly.
