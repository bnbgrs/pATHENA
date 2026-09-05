# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline reviewed this run: `develop/pathena-next@d14aca9504021bdacadb89dc478ca41545ab4316`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization commit: `93193c4df012515099f809bd7c339f0b15df2783`, with parents verified worker `eaa43526398c2e5abb6efb2ec2ae58c53178e878` plus exact Develop `d14aca9504021bdacadb89dc478ca41545ab4316`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Completed Core coverage

Normal Hybrid Search facade/application composition, production contradiction acceptance, fenced Research source coverage, Scoped Project Research, Historical Backfill enqueue/durable validation, Historical Backfill candidate freeze, and its real persisted-Source inclusive-time/pinned-snapshot regression are already verified/integrated on Develop and remain closed.

## READY — truthful Local plus Web Research enqueue/durable scope

Primary source: `docs/beta/11_Exhaustive_Research.md`.

Exact product/test commit: `6c5431f35951b7916e1db97138306de41a5da622`.
Exact verified descendant: `eaa43526398c2e5abb6efb2ec2ae58c53178e878`.
Canonical ATHENA Quality: `33987002816 = success`.
Focused verification: `33986943543 = success` with pytest `10 passed`, Ruff PASS and mypy PASS.

Verified contract:

- `ResearchService.enqueue_local_plus_web()` requires an explicit UUID authorization and at least one captured external Source;
- persists truthful `mode=local_plus_web` plus canonical non-null `internet_scope` with exact authorization id and captured Source ids;
- durable `research.exhaustive` validation accepts Local+Web only with canonical authorization/captured-source provenance and requires captured ids to exactly match `explicit_source_ids`;
- all non-Web Research modes continue to require null Internet scope;
- `ExternalResearchService` captures authorized external URLs first and only then delegates to truthful Local+Web enqueue;
- no candidate-freeze union expansion is included in this READY slice;
- no Protected/Archive expansion or synthetic Source/Claim/Evidence/PALLAS data is introduced.

## Current open Core slice — Local plus Web candidate freeze union

The production gap is now concrete in `ResearchRepository.freeze_local_candidates()`:

- every non-null `internet_scope_json` is currently rejected;
- the supported-mode guard currently admits only `local_exhaustive` and `historical_backfill`;
- simply removing those guards would be incorrect because ordinary local discovery would also include unrelated historical external captures;
- durable `external_source_captures` already records the exact `authorization_id -> source_id` linkage created during capture-before-analysis.

Required next product contract:

1. For `local_plus_web`, parse the canonical Internet scope and require its authorization/captured Source ids to match the persisted explicit Source ids.
2. Build candidates from eligible local Sources at the pinned snapshot, excluding Sources that have any durable external-capture linkage.
3. Add only the explicit captured Sources whose durable `external_source_captures.authorization_id` matches this Research authorization and whose Source version is visible at the pinned snapshot.
4. Reject missing/mismatched capture linkage fail-closed; never fall back to all historical Web captures.
5. Keep local/historical behavior unchanged and keep project/domain/Protected/Archive scope fail-closed.

A versioned deterministic implementation/acceptance patch is stored at `docs/agent_handoffs/spec-core-local-plus-web-freeze.patch`. The next Core run must apply and verify it rather than repeat this analysis.

## Collision avoidance

- Current Develop Integrator/Backend changes are preserved by the two-parent sync.
- UI presentation/navigation work remains disjoint.
- Current Error handoff reports no Core-owned blocker for this slice.
- No implicit external access occurs during candidate freeze; only already captured durable Sources may participate.

## Integrator handoff

`READY` for the truthful Local+Web enqueue/durable authorization-scope slice only:

- product/test: `6c5431f35951b7916e1db97138306de41a5da622`
- exact green descendant: `eaa43526398c2e5abb6efb2ec2ae58c53178e878`
- canonical Quality: `33987002816 = success`
- current history-preserving sync: `93193c4df012515099f809bd7c339f0b15df2783`

Do not treat the candidate-freeze union as READY until its separate product/test head is green.

## Next Alpha/Beta gap

Apply `docs/agent_handoffs/spec-core-local-plus-web-freeze.patch`, run the focused Local+Web/Research regressions and canonical Quality, then version an exact READY SHA if green. If the patch exposes an exact schema/API mismatch, fix only the smallest fail-closed candidate-selection contract; do not broaden authorization, Internet, Protected or Archive scope.
