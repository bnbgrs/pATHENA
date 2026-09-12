# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`
- Develop parent before this integration: `cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80`
- Parent canonical Quality: `34676594675` = `SUCCESS`
- Promoted worker candidate: `postmerge/spec-core` exact SHA `8ee183e14ed2527d254def4946ce0b79104f1afa`
- Exact Core Focused Candidate: `34677902970` = `SUCCESS`
- Exact canonical Quality on the worker candidate was still running when this bounded slice was selected; no later worker commit superseded the exact-head focused evidence.

## Integrated bounded slice

Only the self-contained stale-claim revalidation planning slice and its direct focused tests are integrated:

- `src/athena/knowledge/revalidation_job.py`
- `tests/unit/test_revalidation_job.py`

The worker was synchronized to exact current Develop immediately before this product commit. Comparison against current Develop is exactly these two added Core-owned files. No Worker history, Backend, Storage, Recovery, Security, Qt/UI, CI, visual-ledger, or unrelated documentation mutation is imported.

`RevalidationPlanner` creates immutable work only for important claims carrying an active stale signal. Jobs are pinned to the historical Claim revision and baseline evidence revisions. Result assessment never rewrites or deletes the Claim: absence of genuinely new evidence keeps the historical Claim unchanged, while newly discovered evidence requires explicit review. UUID, tuple uniqueness, bool-safe timestamp and runtime-type boundaries fail closed.

## Current evidence rules

- Current Error handoff keeps `ERR-0035 / BE-052` `OPEN / P1 / Backend-owned`; Storage/Recovery is not mutated here.
- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- Root `ALPHA_BETA_PROGRESS.md` is absent on current Develop; no completion percentage is invented.
- The eleven-screen manifest remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`; `MATCH` still requires an opened original reference and a real exact-SHA render.
- Current Backend and UI canonical worker gates were still running/pending during selection and were not promoted.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
