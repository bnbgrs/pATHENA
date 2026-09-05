# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@415debaae20fd84cd12fa0613dc063dc48dd134f`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization commit: `32fe54c850dacee3e62be84c9f122539f35645d4`, with parents previous worker `f58ddd4ad333401a12bf8fd786d1f45016363d57` plus exact Develop `415debaae20fd84cd12fa0613dc063dc48dd134f`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Completed Core coverage

Normal Hybrid Search facade/application composition, production contradiction acceptance, fenced Research source coverage, Scoped Project Research, Historical Backfill enqueue/durable validation, Historical Backfill candidate freeze, and its real persisted-Source inclusive-time/pinned-snapshot regression are already verified/integrated on Develop and remain closed.

## Current slice — truthful Local plus Web Research

Primary source: `docs/beta/11_Exhaustive_Research.md`.

The previously versioned Local+Web patch has now been materially applied. The original pseudo-unified patch was not directly consumable by `git apply`, so the worker used an exact-match deterministic transformation against the fully inspected current product blobs. During application one concrete mismatch was corrected: `_canonical_uuid_list()` previously returned `None`, while truthful Local+Web durable validation needs the canonical UUID list for exact captured-source equality; the helper now returns that canonical list without weakening any existing validation.

Product/test commit: `6c5431f35951b7916e1db97138306de41a5da622`.

Implemented contract:

- `ResearchService.enqueue_local_plus_web()` requires an explicit UUID authorization and at least one captured external Source;
- persists truthful `mode=local_plus_web` plus canonical non-null `internet_scope` with exact authorization id and captured Source ids;
- durable `research.exhaustive` validation accepts Local+Web only with canonical authorization/captured-source provenance and requires captured ids to exactly match `explicit_source_ids`;
- all non-Web Research modes continue to require null Internet scope;
- `ExternalResearchService` still captures authorized external URLs first and only then delegates to truthful Local+Web enqueue;
- no candidate-freeze union expansion is included yet;
- no Protected/Archive expansion or synthetic Source/Claim/Evidence/PALLAS data is introduced.

## Verification state

Focused mutation run `33986943543` succeeded before the product/test commit:

- `tests/unit/test_research_local_plus_web.py`
- `tests/unit/test_research_scoped_project.py`
- `tests/unit/test_research_historical_backfill.py`
- focused Ruff on changed product/test files
- focused mypy on changed product files

Result: focused pytest `10 passed`; Ruff PASS; mypy PASS.

The automatic PR Quality attempt on the workflow-authored product commit was `33986966745` with conclusion `action_required` and zero jobs, so it is **not** a Quality PASS. This handoff commit exists to trigger canonical Quality through the normal repository mutation identity on the same product/test tree. No READY claim is made until that exact descendant Quality run succeeds.

## Collision avoidance

- Backend storage/disk-pressure work is disjoint.
- UI presentation/navigation work is disjoint.
- Current Error handoff has no Core-owned blocker for this slice.
- No candidate-freeze, Protected/Archive, or implicit Internet scope broadening occurred.

## Integrator handoff

`NOT READY` pending a real canonical Quality run on this product/test tree. Do not integrate the new Local+Web slice solely from the focused run.

## Next Alpha/Beta gap

If canonical Quality succeeds, mark this truthful enqueue/durable-scope slice READY with the exact Quality evidence, then immediately implement Local+Web candidate-freeze union semantics: eligible local Sources at the pinned snapshot plus only exact external Sources linked to the explicit authorization through durable external capture linkage; unrelated historical external captures must remain excluded and Protected/Archive must remain fail-closed.
