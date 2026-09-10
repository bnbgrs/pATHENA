# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58`.
- Error worker entered this run at `postmerge/errors@b7933c64c15763cc09b791b422ce0a09a83e9b4d`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `338e4514d144f4701e52515c0196e0f968f5db47`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop canonical Quality: `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58 = IN_PROGRESS`. Windows path safety, Linux storage and Local install are SUCCESS; spec validator, Ruff and mypy are SUCCESS; full pytest remains in progress at this checkpoint.
- Fresh compare `3330a0092eaddf58fd3a4fdcb7128f77f01b0301...e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58` is exactly one commit and changes only `.github/workflows/quality.yml` plus `docs/agent_handoffs/integrator.md`.
- `postmerge/errors@b7933c64c15763cc09b791b422ce0a09a83e9b4d` had zero queued/in-progress canonical Quality runs before the ledger mutation; after ledger commit `64a74ddf2a48897a8df9275fcf2c807e7cf170e8` there were again zero queued/in-progress runs, so this handoff update does not supersede active Error-worker CI.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 exact-current opening

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status: `OPEN`, P1. Specialist owner: Backend / BE-046.

Backend handoff at `postmerge/backend@338e4514d144f4701e52515c0196e0f968f5db47` marks BE-046 `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE`. Its current evidence is that POSIX reserve creation/release binds the opened parent directory identity, while the non-POSIX branch creates through `os.open(self.path, ...)`, validates pathname/file identity after open, and later performs release through pathname `stat()` / `unlink()`. This leaves directory identity unbound through the Windows mutation itself.

The source-trace evidence is current rather than historical: it was recorded against Develop `3330a0092eaddf58fd3a4fdcb7128f77f01b0301`; current Develop `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58` is exactly one commit ahead and the only changed files are the canonical Quality workflow and Integrator handoff. No Backend/Storage product source changed, so the traced condition survives on the current exact SHA.

This is not being mislabeled as a canonical failure. Current Quality `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58` is still running and its Windows path-safety lane is already SUCCESS. ERR-0033 is OPEN because a current exact source trace establishes an uncovered identity-binding invariant, not because a failing test was fabricated.

Errors made no product mutation because Backend already owns BE-046. Preserve physical non-sparse reserve allocation, exact release accounting, and fail-closed Storage/Recovery semantics; do not replace the invariant with pathname-only checks.

## Integrator handoff

- Current Develop: `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58`.
- Current canonical Quality: `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58 = IN_PROGRESS` at checkpoint; Windows path safety, Linux Storage, Local install, validator, Ruff and mypy are green, full pytest still running.
- `ERR-0033 = OPEN / P1`; maps to Backend `BE-046` on current worker `338e4514d144f4701e52515c0196e0f968f5db47`.
- Exact freshness evidence: Develop moved only one CI/docs commit from the BE-046 source-traced SHA, with no Backend/Storage source delta.
- Product mutation by Errors: none; avoid parallel ownership collision.
- Closure prerequisite: Backend provides a bounded candidate and focused Windows regression proving directory identity remains bound across reserve mutation/release, with exact candidate SHA and real PASS evidence. Canonical Quality should only be consumed/started under normal CI discipline.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and WAL exact-type fail-closed semantics.
