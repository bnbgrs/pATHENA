# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@b5d888b09774e70a389457f568a8079faf130b5e`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization: `c5f27a33efe9327eb64fdeae4672acb987f33f32`, parents prior worker `372697dbbb356ac0bbedfbd4d27f917c38fcefac` plus exact Develop `b5d888b09774e70a389457f568a8079faf130b5e`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Previously READY / integrated

Normal Hybrid Search facade/application composition, production contradiction acceptance, fenced Research source coverage, Scoped Project Research, Historical Backfill enqueue/durable validation/candidate freeze/persisted-source boundaries, and truthful Local+Web enqueue/durable authorization scope are verified and integrated on Develop.

## READY — Local+Web candidate freeze union

Exact product/test commit: `31a52e034c154759a2ccce2eebc77a2f2d961f37`.
Exact canonical-green descendant: `372697dbbb356ac0bbedfbd4d27f917c38fcefac`.
Focused execution: `33992910995 = success` with `12 passed`, Ruff PASS, mypy PASS.
Canonical Quality: `33993014519 = success` on exact head `372697dbbb356ac0bbedfbd4d27f917c38fcefac`.

Verified contract:

- `ResearchRepository.freeze_local_candidates()` admits `ResearchMode.LOCAL_PLUS_WEB` only with canonical persisted Internet scope.
- The scope requires canonical UUID `authorization_id` plus sorted/unique canonical `captured_source_ids`.
- Durable `external_source_captures` linkage for that authorization must exactly equal the requested captured Source set; mismatch or absence fails closed.
- `_select_sources_as_of()` remains authoritative for pinned-snapshot/time/source-type visibility.
- The local portion excludes Sources carrying any external-capture linkage.
- Only external Sources linked to the exact current authorization may re-enter the candidate union.
- Another authorization's historical capture and post-snapshot Sources are excluded.
- Local Exhaustive and Historical Backfill semantics remain unchanged; project/domain/Protected/Archive scope remains fail-closed.
- Freeze performs no external transport and introduces no synthetic Source/Claim/Evidence/Provenance/PALLAS data.

Real acceptance uses `AthenaApplication`, real local Source persistence, explicit ExternalAccess authorization and real `capture_url()` persistence through `external_source_captures`, with deterministic in-process transport replacing network I/O only.

## Runtime / crash invariants retained

This slice does not change packaging metadata/dependencies, frozen entrypoints/argv routing, Desktop/Worker process topology, DirectChat context-budgeting or safety margin, scheduler lane-lock policy, migrations/storage bootstrap, or Windows publication. Known pypdf packaging, fail-closed unknown argv, bounded worker-tree, 2048-context DirectChat guard, lane-lock/runtime crash cluster, and storage-startup prevention invariants remain release-regression requirements and were not reopened without exact-SHA evidence.

## Collision avoidance

- Current Develop changes were limited to Integrator handoff plus UI theme/test work relative to the prior worker merge-base and were preserved exactly in the two-parent synchronization.
- Only `postmerge/spec-core` was mutated; no force push or history rewrite occurred.

## Integrator handoff

`READY` for Local+Web candidate-freeze union.

- Product/test: `31a52e034c154759a2ccce2eebc77a2f2d961f37`
- Exact green descendant: `372697dbbb356ac0bbedfbd4d27f917c38fcefac`
- Canonical Quality: `33993014519 = success`
- Develop synchronization: `c5f27a33efe9327eb64fdeae4672acb987f33f32`

Do not transplant temporary applicator workflow/script; they were deleted before the product/test commit.

## Next Alpha/Beta gap

Inspect the remaining production Knowledge/Claims mutation paths for any direct contradiction-review enqueue path that bypasses the already verified combined temporal + attribution gate. If a bypass exists, patch only that composition boundary and add exact-revision acceptance. If no bypass exists, take the next bounded evidence-backed Core composition gap from current Alpha/Beta specs without broadening Protected/Archive/Internet semantics.
