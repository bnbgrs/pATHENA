# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `98b110882910653566fa70b27e9bdaa3f328ef6b`.
- Exact parent canonical Quality: `34724047841 = SUCCESS`.
- Worker heads checked: Errors `493b145af1b31c52a3207484be45039c460e5552`; Spec/Core `6cc6977be39809e464ae62a546312a8217698bc9`; Backend `597297aa1f07d36d872df6e8d20a939a7fab941b`; UI `b3d43e4bcaff1a188668b437d31cb0fffdfc0351`.

## Iteration — Core-Focused ownership repair

`ERR-0046` is closed in code pending exact Develop verification. The Core-Focused workflow previously selected every changed `tests/unit/test_*.py` for focused pytest even though its trigger contract is Core-owned. Exact UI evidence showed that this admitted UI/PySide-only tests and could fail the Core lane despite UI canonical success.

The focused pytest selector now accepts only the explicit Core-owned families already represented by the workflow trigger contract: `test_claim*`, `test_knowledge*`, `test_concept_note*`, `test_identity_transition*`, and `test_temporal*`. A repository regression test locks this ownership boundary and rejects restoration of the generic `test_.*` selector.

Preserved invariants: `--diff-filter=ACMR`, exact candidate/base SHA checks, locked environment, changed-file Ruff, tracked-worktree fail-closed remediation, immutable reset, diagnostics upload, and final Ruff+pytest outcome enforcement. No Skip/XFail or test-strength relaxation was introduced.

## Worker qualification

- Spec/Core `6cc6977be39809e464ae62a546312a8217698bc9`: exact Core Focused and canonical are red; changed Ruff and focused tests themselves passed before final enforcement failed. Not READY; no product slice imported.
- Backend `597297aa1f07d36d872df6e8d20a939a7fab941b`: effective delta versus Develop is schedule-startup code/tests; Backend Focused is green while canonical was still in progress at qualification time. Conservative hold.
- UI `b3d43e4bcaff1a188668b437d31cb0fffdfc0351`: synchronization head before visual shell work; no bounded UI product slice imported.
- Errors `493b145af1b31c52a3207484be45039c460e5552`: current handoff identifies `ERR-0046` as the Core-Focused ownership-selection gap and `ERR-0047` as the Backend schedule-startup test-contract blocker.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority where newer exact-SHA evidence exists.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` contains no invented completion percentage.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no screenshot `MATCH` without opened original reference plus real exact-SHA render.
- Superseded Worker CI is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup and storage-bootstrap regression signatures. `main` and `bnbgrs/ATHENA` remain read-only.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation. If exact-green, requalify current Backend first because its canonical run was still active during this integration.
