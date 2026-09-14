# UI reference identity evidence — post-#150 handoff

## Exact lineage

- Base: `develop/pathena-next@b3766e0c690aac4db0567c63a3e2886f8fbce368`.
- Initial pair-evidence implementation: `d1c2eda4d4dd4f8bfa2b713164baee032eb4dfb8`.
- Explicit release-ready exit-mode hardening is included on this branch.
- Evidence-identity hardening commits: `3028bb769ff23965c3af001e4adfb160212c02d9` and `45578160b8e756205dc7d8d9cbff1b25cdc585ec`.

## Problem

The visual comparator can validate eleven runtime PNG filenames, but eleven captures are not automatically the eleven authoritative user references. The authoritative set includes a dedicated Light Workspace while the current renderer still captures a Files workspace instead. Count-only or filename-only evidence can therefore look complete while pairing the wrong states.

## Repair

- bind slots 01–11 to authoritative reference IDs, original filenames and reference states;
- require opened original plus opened runtime render, a non-blank runtime identity and exact lowercase 40-character SHA for substantive verdicts;
- count a pair as verified only when the authoritative reference identity itself matches;
- require same-state comparison and explicitly reject using Files as slot 10 Light Workspace;
- require `visible_gaps` to be a list of non-blank descriptions for `CLOSE` and `GAP`; malformed gap evidence fails closed;
- require eleven exact same-state `MATCH` verdicts for `visual_ready_11_of_11=True`; `CLOSE` remains not-ready;
- keep normal validation useful for truthful incomplete evidence: structurally valid `UNVERIFIED`, `GAP` or `CLOSE` evidence may exit 0 while reporting not-ready;
- `--require-ready` is the release mode: malformed evidence exits 1, valid but not-11/11-ready evidence exits 2, and only exact 11/11 `MATCH` exits 0.

This slice does not modify the UI worker manifest, renderer, comparator thresholds, baseline bundle or product UI. It cannot manufacture a visual match.

## Integration rule

Keep this branch staging-only until the preceding ACMRT integration has merged and its new Develop SHA is canonical-green. Then reconstruct the three-file slice on that exact base, open one Draft PR and require exact-head canonical Quality. UI rendering remains owned by `postmerge/ui`; later workflow wiring must use `--require-ready` when the intent is release gating rather than evidence-shape validation.