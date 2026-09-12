# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `915668a376390d86fb333291f555eb804dfa4358`.
- Exact parent canonical Quality: `34718446158 = FAILURE`; Windows path safety, Linux storage regressions and Local install smoke passed; Python quality failed only in full pytest after specification validator, Ruff and mypy passed.
- Worker heads checked: Errors `58922ab89a6ce6f7d5bf24b9012d9a0fa8c48018`; Spec/Core `2d92eec5c63234ab2af85ac8a06617043723a707`; Backend `0ca66fceb78bf7744f12029430780c7cb20be72f`; UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`.

## Iteration 1 — close current integrated storage regression

Backend exact `0ca66fceb78bf7744f12029430780c7cb20be72f` is based on current Develop content and its effective delta versus Develop is bounded to two files: `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py`. Exact Storage Focused `34720329575 = SUCCESS` and canonical Quality `34720329568 = SUCCESS`.

The correction preserves fail-closed startup identity handling while accepting one legitimate SQLite lifecycle transition that the previous Develop hardening rejected: a previously validated complete WAL+SHM pair may be withdrawn together while the primary database identity remains unchanged. Partial sidecar changes, primary replacement and unstable revalidation remain rejected. A focused regression test covers the complete-withdrawal transition.

No Security, Storage, Recovery, packaging, runtime-topology, assertion, Skip/XFail or canonical-gate guard is relaxed.

## Worker qualification

- Backend `0ca66fceb78bf7744f12029430780c7cb20be72f`: READY for this two-file regression closure; Storage Focused and canonical Quality are exact-head green.
- Spec/Core `2d92eec5c63234ab2af85ac8a06617043723a707`: newer product head; requalify exact Core/canonical evidence after current Develop recovery before promotion.
- UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`: synchronization head; not imported as a product slice.
- Errors `58922ab89a6ce6f7d5bf24b9012d9a0fa8c48018`: diagnostic handoff is newer than the repository Error Ledger and records `ERR-0046` as the current harness-owned issue; exact CI evidence remains authoritative.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for OPEN state when newer exact-SHA evidence exists.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` contains no invented completion percentage.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no screenshot `MATCH` without opened original reference plus real exact-SHA render.
- Superseded Worker CI is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. `main` and `bnbgrs/ATHENA` remain read-only.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation.
