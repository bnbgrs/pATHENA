# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T21:48Z
Branch: `develop/pathena-next`
Run-start HEAD: `0298f0c4f2d28e516a458390f8b462131ebaf17e`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Exact Develop canonical Quality `34646579929@0298f0c4f2d28e516a458390f8b462131ebaf17e = SUCCESS` before mutation.
- Worker heads reviewed: Errors `d58378fb92b90fee5c338b0a23a3b334510394d5`; Spec/Core `229a46dd7d91d2c4518379db781c7e5e800c2811`; Backend `04c1609279297fb6b829cb8a96939eca5187c8ab`; UI `bffde469086fb011d36adbab61f7faa1a7b89d34`.
- Spec/Core exact head has canonical Quality `34648338237 = FAILURE` and Core-focused Candidate `34648337671 = FAILURE`. Canonical specification validation, mypy, full pytest, Linux storage, Windows release guards and local-install are green; canonical Ruff remains the isolated red quality step on the bounded identity-transition candidate.
- Backend exact head has focused evidence green but canonical Quality `34649415338` is still pending, so no Backend product slice is promoted.
- UI exact head canonical Quality `34650987626` is still in progress; no UI product slice is promoted while exact-head Quality is incomplete.
- Current Error handoff keeps `ERR-0033 / BE-046` and `ERR-0035 / BE-052` OPEN and Backend-owned, and identifies the current Spec/Core Ruff cluster separately; no competing Storage/Recovery mutation is taken.
- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not used as sole current OPEN truth.
- Root `ALPHA_BETA_PROGRESS.md` is absent on current Develop; no synthetic percentage is recorded.
- Visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; all eleven manifest slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`, and no screenshot-level `MATCH` is claimed without approved reference/current-render pairing.

## Cross-cutting slice integrated this run

Extended `.github/workflows/core-focused-candidate.yml` with an exact-candidate Ruff remediation artifact.

When the existing changed-file Ruff check fails, the focused lane now:

- re-selects only Python files changed between the immutable PR base SHA and exact candidate SHA;
- runs Ruff auto-fix only as a diagnostic operation after focused tests have completed;
- records Ruff's output plus a binary-safe `ruff-fix.diff` in the existing seven-day focused diagnostics artifact;
- hard-resets to the immutable candidate SHA immediately after producing the diagnostic patch and verifies a clean worktree;
- leaves the existing fail-closed enforcement unchanged: the candidate still requires both the original Ruff check and focused pytest to succeed.

This does not promote, modify or silently repair a worker candidate. It gives the owning Spec/Core worker a directly actionable exact-SHA remediation patch for import-order/lint-only failures while preserving candidate identity and canonical Quality authority.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv, Desktop/Worker two-EXE topology, one Desktop instance with bounded workers, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap protections remain unchanged.
- No Skip/XFail, assertion relaxation, Storage/Recovery/Security weakening or visual threshold reduction was introduced.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for the resulting Develop SHA before any further Develop mutation.
2. Re-read all worker heads and exact-SHA evidence after that gate completes.
3. Do not promote Spec/Core until a corrected exact head has focused Ruff + focused pytest green and acceptable exact canonical evidence.
4. Do not promote Backend or UI while their exact-current canonical runs remain incomplete.
5. Keep Backend Storage/Recovery prerequisites conservative until bounded exact-tested BE-046/BE-052 candidates exist.
6. Keep all visual `MATCH` claims fail-closed until approved original-reference and exact-render evidence exists.
