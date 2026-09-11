# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T20:51Z
Branch: `develop/pathena-next`
Run-start HEAD: `17d06d258ec2f5841049227504034ef601cdcdf8`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Exact Develop canonical Quality `34641291324@17d06d258ec2f5841049227504034ef601cdcdf8 = SUCCESS` before mutation.
- Immediately before mutation, Develop had zero queued and zero in-progress workflow runs.
- Worker heads reviewed: Errors `53d8a63e12f5010eed5e28498fe62cc36a617c78`; Spec/Core `58b8040f84d5cac2530aaaac349c695361a78996`; Backend `4feffb3492bcb656fd6d7a53818e61199f4e0d7a`; UI `854a0ada4b3663aa94e09083bf17017eebd68c50`.
- Spec/Core exact head has canonical Quality and Core-focused Candidate failures; no Core slice is promoted.
- Backend exact head has a bounded jobs-only delta (`src/athena/jobs/job_admission.py`, `tests/unit/test_job_admission.py`). Its focused Candidate is green, full pytest is green, Linux storage is green, Windows release guards are green and local-install is green, but canonical Quality is red because canonical mypy fails. The product slice therefore remains not READY pending exact type-check closure.
- Current Error handoff keeps `ERR-0033 / BE-046` and `ERR-0035 / BE-052` OPEN and Backend-owned; no competing Storage/Recovery mutation is taken.
- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not used as sole current OPEN truth.
- Root `ALPHA_BETA_PROGRESS.md` is absent on current Develop; no synthetic percentage is recorded.
- Visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; all eleven manifest slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`, and no screenshot-level `MATCH` is claimed without approved reference/current-render pairing.

## Cross-cutting slice integrated this run

Added `.github/workflows/backend-focused-candidate.yml` as a Develop-owned exact-PR-head qualification lane for bounded Backend Jobs candidates.

The lane:

- binds immutable PR head and base SHAs and checks out the exact candidate;
- runs Ruff on the actually changed Jobs source/tests;
- runs mypy on `src/athena/jobs` so Backend-owned typing failures are visible independently of unrelated packages;
- runs only the actually changed `tests/unit/test_job*.py` files;
- persists Ruff/mypy/pytest diagnostics for seven days;
- uses `cancel-in-progress: false` and a final fail-closed enforcement step requiring all three outcomes to succeed.

This does not replace or weaken canonical Quality. It adds narrower evidence so the current Backend Jobs candidate can distinguish an in-scope typing defect from an unrelated global failure before promotion.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv, Desktop/Worker two-EXE topology, one Desktop instance with bounded workers, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap protections remain unchanged.
- No Skip/XFail, assertion relaxation, storage/recovery/security weakening or visual threshold reduction was introduced.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for the resulting Develop SHA before any further Develop mutation.
2. Re-read all worker heads and exact-SHA evidence after that gate completes.
3. For Backend Jobs, require exact current-head focused mypy plus focused pytest and canonical evidence before promotion; do not absorb the current candidate while canonical mypy is red.
4. Keep Backend Storage/Recovery prerequisites conservative until bounded exact-tested BE-046/BE-052 candidates exist.
5. Keep all visual `MATCH` claims fail-closed until approved original-reference and exact-render evidence exists.
