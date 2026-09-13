# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `9e607472ba65ce86b795cf8f6926a0809700a2cd`.
- Exact parent canonical Quality `34755721026 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration 1 — Core-Focused user-correction harness coverage

The Error handoff identified a generic CI omission after the user-correction product slice had to be renamed into the existing `test_knowledge*.py` selector. Current Develop still omitted `tests/unit/test_user_correction*.py` from both the PR path trigger and changed-test selection.

This bounded cross-cutting fix adds only the missing trigger/selector and a regression contract in `tests/unit/test_core_focused_candidate_workflow.py`. It expands mandatory coverage; it does not skip, xfail, relax, or remove any check. Exact worker commits used as implementation evidence: `4b723fe7202c841e0c768aaf3a62600eaadf02ff` and `ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e`.

## Current worker state before mutation

- Errors: `a1f6b796c6d9cb7b5aab3e2b36e663d872569f6d`.
- Spec/Core: `77048de78be4dd7ca2555ed1b09e00d088f9c624`; canonical `34756815221 = SUCCESS` and tree synchronized with Develop.
- Backend: `e76bfbe266107a781e3602246d143ee8e9e849b3`; canonical `34757222993 = SUCCESS` and tree synchronized with Develop.
- UI: `d351dba17b69c3f5b55a1447f2ac088b929a1b48`; current canonical was still active during qualification, so no UI slice was promoted.

## Visual/source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` is historical where newer exact-SHA evidence exists.
- Eleven-screen parity remains fail-closed: no `MATCH` without an opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` still records screenshot-level parity as unverified.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
