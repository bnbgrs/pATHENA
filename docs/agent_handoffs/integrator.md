# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-12T02:48+02:00
Branch: `develop/pathena-next`
Run-start HEAD: `5db4c92f40d5d14119a991796be38fb9248072de`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Exact Develop canonical Quality `34659583545@5db4c92f40d5d14119a991796be38fb9248072de = SUCCESS` before mutation.
- Immediately before mutation, Develop had zero queued and zero in-progress workflow runs.
- Worker heads reviewed: Errors `4c21173a2bdd9f1a55ad41959ccb06069dd6a65b`; Spec/Core `acacc2da478d7f7afad4cd44681201268d5b13b3`; Backend `b595c960a747d9805b0865ea9f7237094318b706`; UI `4772c6aaf16a6eb570b891eae4fa8323d32b54ce`.
- Error evidence freshly reproduces `ERR-0033 / BE-046` on exact current Develop: emergency-reserve unlink does not prove physical reclamation while foreign descriptors or alternate links can retain the inode. `ERR-0035 / BE-052` remains Backend-owned but was not freshly revalidated in the Error run.
- Spec/Core exact head has Core Focused Candidate `34661219526 = SUCCESS`, but canonical Quality `34661219465` remained in progress at review time; it was not promoted.
- Backend exact head has a canonical Quality run `34662086156` in progress at review time; it was not promoted despite the new bounded emergency-reserve candidate.
- UI head is a Develop-baseline synchronization head; older product evidence is not transferred onto it without equivalent exact-head evidence.
- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not used as sole current OPEN truth.
- Root `ALPHA_BETA_PROGRESS.md` is absent on current Develop; no synthetic completion percentage is recorded.
- Visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; all eleven manifest slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`, with no screenshot-level `MATCH` claim absent approved reference/current-render pairing.

## Cross-cutting slice implemented this run

No worker product slice met the exact-head READY rule at mutation time because the two active product candidates still had canonical Quality in progress.

Added `.github/workflows/storage-focused-candidate.yml` as a bounded, fail-closed qualification lane for Storage candidates. It:

- binds exact pull-request head and base SHAs and verifies the immutable checkout identity;
- runs Ruff only on changed Storage/emergency-reserve candidate Python files;
- type-checks the Storage package with mypy;
- always runs the persistent `tests/unit/test_emergency_reserve.py` invariant and additionally runs changed `test_storage*.py` tests;
- persists Ruff, mypy and pytest diagnostics for seven days;
- requires all three focused outcomes to succeed;
- uses `cancel-in-progress: false`, so documentation or subsequent worker commits must not silently replace evidence.

This does not relax canonical Quality, tests, assertions, Security, Storage, Recovery, packaging or Windows guards. It provides exact-head focused evidence for the freshly reproduced BE-046 family without modifying Backend-owned product code.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv, Desktop/Worker two-EXE topology, one Desktop instance with bounded workers, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap protections remain unchanged.
- No Skip/XFail, assertion relaxation, Storage/Recovery/Security weakening or visual threshold reduction was introduced.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation.
2. Re-read all worker heads and exact-SHA evidence after that gate completes.
3. If Backend's BE-046 candidate becomes exact-green, qualify its bounded diff conservatively under the new Storage lane or equivalent exact evidence before integration.
4. Keep BE-052 Backend-owned and conservative until freshly reproduced or bounded exact-tested current evidence closes it.
5. Preserve visual `MATCH` fail-closed requirements.
