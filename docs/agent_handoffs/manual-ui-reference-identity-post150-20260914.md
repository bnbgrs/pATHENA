# UI reference identity evidence — post-#150 handoff

## Exact lineage

- Base: `develop/pathena-next@b3766e0c690aac4db0567c63a3e2886f8fbce368`.
- Functional commit: `d1c2eda4d4dd4f8bfa2b713164baee032eb4dfb8`.

## Problem

The current visual comparator can validate a set of eleven runtime PNG filenames, but eleven captures are not automatically the eleven authoritative user references. The active UI worker manifest correctly inventories the real reference set, including a dedicated Light Workspace, while the current renderer still captures a Files workspace instead.

A count-only or filename-only baseline proposal can therefore be structurally wrong even when it contains eleven images.

## Repair

- add an independent fail-closed pair-evidence validator;
- bind slots 01–11 to the authoritative reference IDs, original filenames, and reference states already opened during visual review;
- require opened original + opened runtime render + exact lowercase 40-char SHA for substantive verdicts;
- require same-state comparison;
- explicitly reject using a Files workspace as slot 10 Light Workspace;
- require eleven exact same-state `MATCH` verdicts for `visual_ready_11_of_11=True`; `CLOSE` remains not-ready.

This slice does not modify the UI worker manifest, renderer, comparator thresholds, baseline bundle, or product UI. It cannot create a visual MATCH by itself.

## Integration rule

Open a Draft PR only after the post-#150 Develop base is canonical-green. Require exact-head canonical Quality. Keep UI rendering changes owned by `postmerge/ui`; this validator only defines evidence eligibility and should be wired into release/visual workflow in a separate reviewed follow-up if appropriate.