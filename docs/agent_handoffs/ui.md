# pATHENA UI Handoff

## Current baseline

- Develop source checked first: `develop/pathena-next@82aaef0caaa90599f530acc84d728b602dee6739`.
- Worker before sync: `postmerge/ui@3cbb2aee7fb3e3bc48b7d6a9fefe86ea3132cb9e`.
- Prior worker exact canonical Quality: `34312166038 = success`.
- History-preserving NON-FORCE synchronization: `0c78b3e43cf7886efa6320c0354159498cc67b29`, using the current Develop tree with both UI and Develop histories retained.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Evidence consumed this run

The user-library reference `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png` was actually opened. It shows a deep-black Workspace/Chat surface, narrow left-owned navigation, quiet top status chrome, a large central work area and a materially larger lower composer with a distinct arrow send target. No current-build screenshot was available side-by-side, so no `MATCH` or pixel-parity claim is made.

Current Develop product code still inherits the legacy base composer geometry from `AthenaMainWindow._build_command_input()` (`composer.setFixedHeight(58)`). The visible pATHENA wrapper already reuses the real prompt input, grounding path and send route, making composer scale a bounded presentation-only gap rather than a need for a mock feature.

## Active slice — UI-GAP-0004 Workspace composer scale

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

Candidate product blob `951d42436388539e0aa1f90760f33c6ef9ebe6fc` changes only `src/athena/desktop/pathena_window.py` presentation geometry:

- composer fixed height: 88 px;
- composer accessible name: `Message composer`;
- prompt minimum height: 44 px;
- real grounding control minimum height: 36 px;
- existing send control fixed to 44×44 px while retaining the real send signal, tooltip, accessible name and Ctrl+Enter route;
- modest composer margins/spacing to prevent the larger targets from crowding the workspace.

No Attach/Focus mock controls are added. Chat submission, grounded/direct routing, model/provider selection, persistence, Storage, Security, Recovery, worker/scheduler and backend semantics are unchanged.

Focused Qt contract blob `8e29fcfc5e8ac0ba4a402ae07f1f593783588063` extends `tests/unit/test_pathena_window.py` to assert the enlarged real composer, its accessible name and the 44×44 send target without weakening existing navigation, inspector, accessibility or routing assertions.

## Coordination

- Current Develop already contains the bounded left-owned primary-navigation integration at `82aaef0caaa90599f530acc84d728b602dee6739`; do not reopen that slice absent a current exact-SHA regression.
- Core/Search work remains Core-owned.
- Backend/Storage/Security semantics remain untouched.
- Error handoff currently reports no OPEN error; no historical runtime signature is reopened here.
- Slot 01 in the manifest now records direct reference availability; other slots remain `VISUAL_REFERENCE_PENDING` unless opened directly.

## Verification / Integrator handoff

Do not mark UI-GAP-0004 Integrator-ready until the focused Qt test and canonical Quality complete on the exact final candidate head containing product, test, manifest, ledger and this handoff. If the exact candidate is green and Develop remains compatible, the slice is bounded for Integrator review. A green code gate still does not imply screenshot-level `MATCH`.

## Next gap

After exact-green verification and Integrator handoff of UI-GAP-0004, select at most one further visible gap backed by an actually opened reference and a real current code/render state. Priority remains workspace hierarchy/spacing, typography or contextual Inspector composition rather than new decorative controls.
