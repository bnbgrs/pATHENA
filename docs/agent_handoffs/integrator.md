# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `54c990285503e5076d31f46408ef530b9f02de28`.
- Exact parent canonical Quality: `34715466882 = SUCCESS`.
- Worker heads checked: Errors `cbcb9f60981484554d39f614308b32b67f378787`; Spec/Core `47053f798bae152f676e9ff4be22ca4c6c06a6a8`; Backend `c40be5764e600fe961bc3aeaf39c17f91100e34f`; UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`.

## Iteration 1 — bounded Backend promotion

Backend exact `c40be5764e600fe961bc3aeaf39c17f91100e34f` has Backend Focused `34717283972 = SUCCESS`, Storage Focused `34717283988 = SUCCESS`, and canonical Quality `34717283963 = SUCCESS`. The effective content delta versus current Develop is bounded to four files; the Worker history itself is not imported.

Integrated product content:

- `src/athena/jobs/schedule_codec.py`: deterministic, versioned durable JSON serialization for `ScheduleDefinition`, with strict schema, duplicate-field rejection, canonical lowercase UUIDs, explicit policy decoding, and reuse of existing schedule invariants.
- `src/athena/storage/database.py`: startup identity revalidation now only accepts a complete concurrent WAL+SHM publication for the same primary identity and re-inspects read-only before accepting it; partial or foreign changes remain fail-closed.
- corresponding focused tests in `tests/unit/test_schedule_codec.py` and `tests/unit/test_storage_database_startup_identity.py`.

No Security, Storage, Recovery, packaging, runtime-topology, assertion, Skip/XFail, or canonical-gate guard is relaxed.

## Worker qualification

- Spec/Core exact `47053f798bae152f676e9ff4be22ca4c6c06a6a8`: Core Focused is green, canonical Quality was still in progress at qualification time; not promoted in this iteration.
- Backend exact `c40be5764e600fe961bc3aeaf39c17f91100e34f`: READY and bounded content integrated.
- UI exact `8b38c1a501789cbfb7c76b1ee1acef999270fa13`: synchronization head only; require exact bounded UI evidence before promotion.
- Errors exact `cbcb9f60981484554d39f614308b32b67f378787`: diagnostic/advisory; newer exact-SHA CI takes precedence.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` is not the sole authority for current OPEN state when newer exact-SHA evidence exists.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` contains no invented completion percentage.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no screenshot `MATCH` without opened original reference plus real exact-SHA render.
- Superseded Worker CI is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. `main` and `bnbgrs/ATHENA` remain read-only.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation.
