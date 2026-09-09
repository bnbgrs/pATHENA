# pATHENA UI Handoff

## Current baseline

- Develop baseline reviewed: `develop/pathena-next@363d6ca497b12cf9f04d9c9392d945960eade3d3`.
- Prior UI exact-green head: `2cb2feb3685358f629095445554c9d04fd56efd1`.
- Worker branch: `postmerge/ui`.
- `main` and `bnbgrs/ATHENA` remain read-only; no force push, history rewrite or main mutation occurred.

## Source-of-truth review

Current `spec-core.md`, `backend.md`, `errors.md`, `integrator.md`, 11-screen manifest and Visual Gap Ledger were reviewed before mutation. Error handoff has no current OPEN UI error. Current Develop advanced from the prior UI merge base only through the DirectChat requested/effective context-budget provenance slice in `src/athena/chat/direct.py`, its focused test and Integrator handoff; these files are disjoint from the UI-GAP-0005 product/test pair.

Actual user reference pixels were directly opened again for Workspace/Chat and Knowledge/PALLAS. They support left-owned primary navigation and restrained top status/context chrome. No pixel parity or screenshot-level `MATCH` is claimed.

## UI-GAP-0004 — black/orange visual foundation

Status: `FIXED / INTEGRATED`.

Exact worker evidence: `a426469b503c6276cd6d1fd3ed6d89be0af67948` -> Quality `34291934346 = success`. Current Develop preserves the integrated deep-black / functional `#F26A21` foundation.

## UI-GAP-0005 — duplicate horizontal primary navigation

Status: `VERIFIED_ON_WORKER / SYNCED_PENDING_EXACT_QUALITY`.

The shared shell had five labeled Workspace/Library/Research/Jobs/Sources primary controls in the top bar while the same product destinations were already owned by the narrow left `iconRail`. The opened Workspace/Chat reference instead reserves the top region for quiet status/context and places primary destinations on the left.

The bounded product slice removes those five `topNavButton` controls from `PathenaMainWindow._install_reference_shell()`. It preserves:

- the actual left `iconRail` and existing navigation model;
- System and Settings utility buttons in the top bar;
- page routing and current-page title updates;
- accessible names/tooltips;
- `Local · Private` status;
- all Backend, Storage, Security, scheduler/worker, provider, transport, process and recovery semantics.

Focused contract `tests/unit/test_pathena_window.py` now requires zero horizontal primary `topNavButton` controls while proving the left primary rail remains present. No test guard was weakened, and no Skip/XFail was introduced.

Exact worker verification: canonical Quality `34304620632 = success` on exact head `2cb2feb3685358f629095445554c9d04fd56efd1`.

## Current synchronization

The current candidate is built history-preservingly from current Develop's tree while reapplying only the exact verified UI product/test blobs and this versioned UI documentation. Current Develop DirectChat provenance changes are retained. A fresh exact-head canonical Quality run is required before whole-candidate Integrator-ready status.

## Integrator handoff

Do not integrate the synchronized descendant until its exact canonical Quality completes green. Once green, UI-GAP-0005 is bounded to `src/athena/desktop/pathena_window.py`, `tests/unit/test_pathena_window.py` and versioned UI coordination docs; the product behavior itself already has exact-green worker evidence at `2cb2feb3685358f629095445554c9d04fd56efd1`.

## Next UI gap

Consume the synchronized candidate's exact Quality first. If green, mark UI-GAP-0005 Integrator-ready and then select at most one next visible reference-backed gap, preferably composer scale, workspace hierarchy, inspector behavior or typography, using a real current render where available. Do not reopen UI-GAP-0001 through UI-GAP-0005 without current exact-SHA regression evidence.
