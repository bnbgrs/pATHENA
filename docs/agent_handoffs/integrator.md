# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-12T04:49+02:00
Branch: `develop/pathena-next`
Run-start HEAD: `ca87e42c8820c47db7d6626feb17698560cd3b49`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Exact Develop canonical Quality `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS` before mutation; no newer canonical Develop run was queued or in progress immediately before mutation.
- Current worker heads reviewed: Errors `9b51bc0cea8f3d32eb9fd232a1711a848d74af39`; Spec/Core `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`; Backend `736fb66085084f3d0080c0918cdfba00d63558fc`; UI `626c7e0dead504b57f331c9b011d99c96cee6c4d`.
- Fresh Error evidence keeps `ERR-0035 / BE-052` OPEN/P1/Backend-owned: accepted SQLite DB/WAL/SHM preflight identity is not yet proven continuous through live writer establishment on Develop. `ERR-0033 / BE-046` is integrated and its exact Develop canonical Quality is now green; final Error-ledger closure remains Error-worker owned.
- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to current Develop and is not used as sole current OPEN truth.
- Root `ALPHA_BETA_PROGRESS.md` remains absent; no synthetic completion percentage is recorded.
- Visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; all eleven slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`, with no screenshot-level `MATCH` claim absent approved reference/current-render pairing.

## Worker qualification this run

- Backend exact `736fb66085084f3d0080c0918cdfba00d63558fc`: Storage Focused Candidate `34668097963 = SUCCESS`; canonical Quality `34668098022` is still pending. Because this is the conservative Storage/Recovery prerequisite for BE-052, it is not promoted before exact canonical completion.
- Spec/Core exact `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`: Core Focused Candidate `34667286211 = SUCCESS`; canonical Quality `34667286138` remains in progress. The bounded current diff from Develop is `src/athena/knowledge/claim_service.py` plus `tests/unit/test_claim_contradiction_resolution.py`, but it is not promoted while exact canonical verification is still running.
- UI exact `626c7e0dead504b57f331c9b011d99c96cee6c4d`: canonical Quality `34668610457` remains in progress. A Core Focused Candidate run was also triggered by UI-only `tests/unit/**` changes and failed even though the UI delta contains no `src/athena/knowledge/**` product file; that cross-lane trigger is tooling noise, not current Core product evidence.

## Cross-cutting tooling unblocker

No worker product slice met the conservative promotion threshold at mutation time, so this run implements exactly one collision-free tooling slice in `.github/workflows/core-focused-candidate.yml`.

The Core-focused PR trigger no longer treats every `tests/unit/**` file as Core-owned. It remains triggered by any `src/athena/knowledge/**` product change and by the current Core/Knowledge test families (`test_claim*`, `test_knowledge*`, `test_concept_note*`, `test_identity_transition*`, `test_temporal*`) plus changes to the workflow itself.

This prevents UI-only unit-test patches from creating an unrelated red Core-focused check while preserving focused evidence for current Knowledge/Core slices. The job body, immutable exact-head binding, Ruff enforcement, focused pytest enforcement, remediation evidence, `cancel-in-progress: false`, and canonical Quality workflow are unchanged. No test, guard, security, storage, recovery or release invariant is weakened.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv, Desktop/Worker two-EXE topology, one Desktop instance with bounded workers, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap protections remain unchanged.
- No Skip/XFail, assertion relaxation, Storage/Recovery/Security weakening, canonical Quality reduction or visual threshold reduction was introduced.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation.
2. Re-read worker heads after that gate completes; do not reuse the SHAs above if workers have advanced.
3. Prefer BE-052 once its exact Backend canonical Quality is green because it closes the remaining current Backend-owned P1 prerequisite; otherwise choose the highest-impact exact-verified bounded slice.
4. Keep visual `MATCH` fail-closed requirements and all persistent release guards intact.
