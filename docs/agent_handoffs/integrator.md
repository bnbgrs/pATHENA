# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `522a01050dba5b4dafa81d60573bd185a8e7e15b`.
- Exact parent canonical Quality: `34712404459 = FAILURE`.
- Exact failure classification: Windows path safety, Linux storage regressions, Local install smoke and full pytest passed; Python quality failed only at Ruff with `I001` in `tests/unit/test_core_focused_candidate_workflow.py`.
- Worker heads checked: Errors `cc856567b5e7c05c8b36e919cddb7808476f366a`; Spec/Core `9f2052b9c10668ad9eeeb2857dbcbb25145cc832`; Backend `365df03a040cb9dffddf6f942ae61a2cdb8dc375`; UI `6bc46a2464344d56ca00461df30ba4a619437498`.

## Iteration 1 — current Develop regression closure

The previous integration added a regression test for the Core Focused candidate workflow. Canonical Ruff identified one exact import-block formatting defect in that new test. This integration changes formatting only: the extra blank line after the sole import is removed so the file satisfies Ruff I001. Test assertions and workflow guard semantics are unchanged.

No Product, Storage, Recovery, Security, UI, packaging, runtime-topology, Skip/XFail, assertion, or canonical-gate semantics are relaxed.

## Worker qualification

- Spec/Core exact `9f2052b9c10668ad9eeeb2857dbcbb25145cc832`: NOT READY. Exact Core Focused and canonical Quality are both red; no stale READY classification is accepted.
- Backend exact `365df03a040cb9dffddf6f942ae61a2cdb8dc375`: current successor specifically targets the sidecar-free preflight fixture/Storage line. Treat conservatively until exact Storage Focused plus canonical Quality are green on this head.
- UI exact `6bc46a2464344d56ca00461df30ba4a619437498`: synchronization/head movement alone is not a bounded READY product slice; require exact current UI evidence for any later promotion.
- Errors exact `cc856567b5e7c05c8b36e919cddb7808476f366a`: diagnostic handoff trails the now-completed Develop run and remains advisory rather than sole truth.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` is maintained without invented completion percentages.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` keeps all eleven slots fail-closed at `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot `MATCH` is inferred without opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` likewise asserts no screenshot-level `MATCH`.
- Worker candidate evidence superseded by later commits is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
