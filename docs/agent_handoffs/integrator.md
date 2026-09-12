# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `d8236b74e69d1eedfdd2b05a52ed767520246671`.
- Exact parent canonical Quality: `34692305368 = SUCCESS`.
- Worker heads checked: Errors `531f78037fdb1d6c89e77393b5be0a53a63ac0b3`; Spec/Core `3f864f5dd02db350b8b0df3103e6cc9c09725a37`; Backend `359b675a37b5b59210399bee1506afddc6ccee13`; UI `dd0ad210baf9125d03b532cbac6c807e56e1e558`.

## Worker qualification

- Backend exact `359b675a37b5b59210399bee1506afddc6ccee13`: Backend Focused Candidate `34693685313 = SUCCESS`; canonical Quality `34693685375 = SUCCESS`. Diff against current Develop is bounded to `src/athena/jobs/scheduled_materialization.py` and `tests/unit/test_scheduled_materialization.py`. READY.
- Spec/Core exact `3f864f5dd02db350b8b0df3103e6cc9c09725a37`: canonical Quality `34693360045 = SUCCESS`, but its synchronization head has the same tree as current Develop and therefore contributes no new bounded product delta.
- UI exact `dd0ad210baf9125d03b532cbac6c807e56e1e558`: canonical Quality is still running and a Core Focused check is failed on the cumulative PR lineage; not READY.
- Errors: current handoff diagnoses `ERR-0040` as the scheduled-materialization test fixture using unsupported SQLite `:memory:` journal mode. Backend's current exact head replaces that fixture with a file-backed canonical-schema database without relaxing Storage guards.

## Integrated bounded slice

Integrated durable scheduled-job materialization. A deterministic schedule occurrence UUID is used directly as the durable `jobs.job_id`; retries therefore converge on the same row through the existing primary-key boundary. Materialization requires an existing write transaction, rejects disabled schedules and malformed runtime values fail-closed, and refuses an existing occurrence identity already bound to a different job. The focused regression fixture uses a file-backed SQLite database initialized through the canonical schema path, preserving the v37->v38 journal-mode invariant instead of weakening it.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` is maintained without invented completion percentages.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed; no visual `MATCH` is inferred without opened original reference plus real exact-SHA render.
- Worker candidate evidence superseded by later commits is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
