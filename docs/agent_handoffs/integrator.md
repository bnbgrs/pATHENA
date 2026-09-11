# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T13:52Z
Branch: `develop/pathena-next`
Run-start HEAD: `b26eea46c89a8b628c2006d24d1fdac7492baa91`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34601243038@b26eea46c89a8b628c2006d24d1fdac7492baa91 = SUCCESS` before this mutation.
- Worker heads reviewed: Errors `685db6e76d68b32c620192d123edcb902e9b267a`; Spec/Core `5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `7f33ae92ec84d6a82052e4196bdd74c829fdf079`.
- Backend and UI workers have synchronized current Develop into their worker histories; no new bounded exact-qualified product slice was promoted from either worker in this run.
- Current Spec/Core PR #56 is exactly two files versus its PR base: `src/athena/knowledge/revision_diff.py` and `tests/unit/test_claim_revision_diff.py`.
- Spec/Core exact head `5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4` is not READY: canonical Quality run `34603615414` failed, and exact-head focused run `34603615415` also failed at Ruff. The focused pytest step was skipped only because the workflow stopped after Ruff; therefore no exact-head focused-test PASS exists yet for this candidate.
- The current Core candidate remains held. No product cherry-pick is taken while lint/test evidence is incomplete.
- `docs/agent_logs/ERROR_LEDGER.md` is retained but historical baseline entries are not treated as current OPEN truth without current reproduction or worker evidence.
- `ALPHA_BETA_PROGRESS.md` remains absent at the requested repository path; no synthetic completion percentage is recorded.
- Visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; no screenshot-level `MATCH` is claimed without approved reference/current-render pairing.

## Cross-cutting tooling unblocker integrated this run

Updated `.github/workflows/core-focused-candidate.yml` so exact-head Ruff and changed focused unit tests are independently observable in a single run.

Ruff and focused pytest now each use explicit step IDs and `continue-on-error: true` only to permit the sibling evidence step to execute. A final `if: always()` enforcement step reads both outcomes and fails the job unless **both** are `success`. Environment setup, immutable SHA validation, locked dependency setup, candidate/base identity, file selection, Ruff rules, pytest assertions, and canonical Quality remain unchanged.

This does not weaken CI. It prevents an earlier lint failure from hiding whether the bounded product tests pass or fail, while preserving a fail-closed overall job result whenever either contract fails.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv, Desktop/Worker two-EXE topology, one Desktop instance with bounded workers, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap protections remain unchanged.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for the resulting Develop SHA before any further Develop mutation.
2. Re-read all worker heads and handoffs after that gate completes.
3. Re-qualify Spec/Core only after an exact candidate run exposes both Ruff and focused pytest outcomes; do not promote while either is red or missing.
4. Keep Backend Storage/Recovery prerequisites conservative until a bounded exact-tested candidate exists.
5. Keep all visual `MATCH` claims fail-closed until approved original-reference and exact-render evidence exists.
