# PALLAS Living Foundation — current Develop reconstruction

Date: 2026-09-14
Owner: Integrator / PALLAS foundation
Base: `develop/pathena-next@ee8aa791742f7cbdd056532e66a50da14c461c4a`
Source candidate: `feat/pallas-living-engine@edb37e79e1b62bc74fc40c3de9573ae421468876`

## Purpose

Split the collision-free PALLAS living foundation from the shell-integration conflict in `pathena_pallas_full_view.py`.

This slice intentionally excludes `src/athena/desktop/pathena_pallas_full_view.py`, which is concurrently owned by the active UI worker. It therefore does not change how the current UI opens or hosts PALLAS.

## Exact source blobs

- `src/athena/desktop/pathena_pallas_living.py` — `c4892fa24b6b78c61e5b22d4f5cef0b6816b9913`
- `src/athena/desktop/pathena_pallas_living_qt.py` — `7f0207eadaa9f16139ccb1be7a2653b3fa29b28d`
- `tests/unit/test_pathena_pallas_living.py` — `42cb45920a0d862217f4423313ca64068312b0e0`
- `docs/ui/PALLAS_LIVING_FIELD.md` — `3dfc7b804ad7ce7284322715dd2a5cb1406e8cb6`

These feature blobs are copied unchanged from the source feature head after its isolated Ruff import-order repair.

A current-base regression module, `tests/unit/test_pathena_pallas_living_qt.py`, was then added after Integrator review identified that the documented Qt lifecycle invariant was not directly exercised by the source candidate.

## Foundation behavior

- deterministic bounded force simulation at the configured target rate;
- semantic similarity can affect layout only and never fabricate graph edges;
- explicit contradiction relations increase repulsion;
- temporal drift, center/focus attraction and bounded motion;
- vitality state with diffusion only across real graph edges;
- runtime age progression `· : + o O ░ ▒ ▓ █`;
- reconciliation preserves recurring entity age/position while admitting new nodes;
- Qt bridge moves already-rendered grounded nodes/edges and annotates runtime age/vitality;
- semantic graph membership and provenance remain owned by the grounded Core snapshot.

## Focused acceptance

`test_pathena_pallas_living.py` proves determinism, semantic attraction without edge creation, contradiction repulsion, age-glyph progression, reconciliation survival pulse and edge-bounded vitality diffusion.

`test_pathena_pallas_living_qt.py` uses the real `PallasGroundedFieldController` and offscreen Qt to prove:

- one living tick changes presentation state without mutating `PallasGraphSnapshot.nodes` or `.edges`;
- semantic, age and vitality lens changes remain presentation-only;
- unknown lenses fail closed;
- disposing the primary semantic field causes the living controller to stop its timer and clear runtime state.

Neither test module depends on or mutates the competing full-view controller.

## Integration boundary

The later UI integration must reconcile two independent requirements:

1. current UI worker: PALLAS is shell-hosted with focus/route restoration;
2. source PALLAS feature: one shared `PallasLivingQtController` powers compact/full renderers and full-view lenses.

Do not reintroduce the source feature's detached/full-view behavior by copying its whole `pathena_pallas_full_view.py` over the UI worker.

## Qualification

Require fresh current-base canonical Quality and UI Focused evidence on the exact current head after the added Qt lifecycle regression. No visual MATCH claim is made by this foundation slice. No Skip/XFail or comparator relaxation.
