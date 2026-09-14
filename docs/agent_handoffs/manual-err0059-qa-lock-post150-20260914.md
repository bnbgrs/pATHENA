# ERR-0059 QA Lock — current Develop — 2026-09-14

## Scope

Current-base reconstruction of the remaining ERR-0059 regression lock on exact canonical-green `develop/pathena-next@b3766e0c690aac4db0567c63a3e2886f8fbce368`.

The renderer behavior itself is already present on current Develop: `scripts/render_pathena_ui_snapshot.py` reports `captured_reference_count` from `len(captures)` and reports `captured_reference_surfaces` from the captures actually produced.

This slice adds only the missing QA contract that prevents a future regression back to assigned or hard-coded capture claims.

## Added contract

`tests/qa/test_visual_capture_manifest_truth.py` requires:

- captured count is derived from `len(captures)`;
- captured surface names are derived from actual capture labels;
- count is not substituted from `expected_capture_count`;
- surface names are not replaced with a hard-coded nominal list.

## Boundary

This does not claim that the eleven captured runtime states are the eleven authoritative user reference identities. Current UI evidence documents that the human reference set includes states such as Light Workspace and Local Memory that are not yet represented by truthful same-state targets. Count equality therefore remains insufficient for visual MATCH or baseline promotion.

No renderer, UI, comparator threshold, workflow, product runtime, Storage, Core, Security or provider behavior changes in this slice.

## Integration rule

Require exact-head canonical Quality on this current-base branch and a fresh collision check. Do not consume stale Error-worker workflow files. No Skip/XFail, no threshold relaxation, no visual MATCH claim, no auto-merge.
