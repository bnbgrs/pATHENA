# PALLAS Living Foundation — post-#150 current-base handoff

## Exact lineage

- Integration base: `develop/pathena-next@b3766e0c690aac4db0567c63a3e2886f8fbce368`.
- Foundation commit before this handoff: `8c6b28c15721aeb542da13d7179e0357d9e0b0fc`.
- Source qualification vehicle: PR #149 exact head `0417410e2fdff9dc4ce953951b451bad01fa2361`.
- Source UI-Focused run `34820947441 = SUCCESS`.
- Source canonical run `34820947425 = SUCCESS` including full pytest, Specification Validator, Ruff, mypy, Windows path safety, Linux storage regressions, and Local install smoke.

## Exact functional blobs carried forward

- `docs/ui/PALLAS_LIVING_FIELD.md` = `3dfc7b804ad7ce7284322715dd2a5cb1406e8cb6`
- `src/athena/desktop/pathena_pallas_living.py` = `c4892fa24b6b78c61e5b22d4f5cef0b6816b9913`
- `src/athena/desktop/pathena_pallas_living_qt.py` = `7f0207eadaa9f16139ccb1be7a2653b3fa29b28d`
- `tests/unit/test_pathena_pallas_living.py` = `42cb45920a0d862217f4423313ca64068312b0e0`
- `tests/unit/test_pathena_pallas_living_qt.py` = `cf11422a99c5a16cacaf8e44bb80f55a3022ab0c`

## Safety boundary

This slice intentionally excludes `src/athena/desktop/pathena_pallas_full_view.py` and any active UI-worker shell/controller file. The living engine may move presentation items and diffuse vitality over real graph edges, but it must not add, remove, rewrite, or infer semantic graph truth.

The Qt regression uses the real `PallasGroundedFieldController` and locks graph immutability across ticks/lenses, fail-closed unknown lenses, and timer/state cleanup after actual field disposal.

## Review notes

- `graph_id` for normal grounded-chat snapshots is derived from `processing_run_id`, so the Qt bridge's graph-id reconciliation boundary is aligned with immutable grounded-run snapshots.
- The current engine intentionally performs pairwise force/similarity work. Semantic token caching is a later performance optimization, not part of this foundation integration.

## Integration rule

Do not merge historically. Require:

1. post-#150 Develop canonical Quality on `b3766e0...` = SUCCESS;
2. fresh exact-head UI-Focused + canonical Quality on the current-base branch;
3. final collision review against the latest `postmerge/ui` before merge.

No Skip/XFail, no visual MATCH claim, no provenance weakening, no auto-merge.