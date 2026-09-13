# pATHENA Error Hunter Handoff

## Current exact state

- Develop: `c1847b26941ff83d9b80b2839435a6079dc19dea`; canonical Quality `34766898131 = IN_PROGRESS`. Do not start a competing run or mutate Develop from this worker.
- Spec/Core: `d2569f97607566e241443622ec1f11370aebb880`; Core Focused and canonical are `SUCCESS`.
- Backend: `b7a1358caa1c5ae97066ea8075fcde4285b47882`; Backend Focused `34765672180 = SUCCESS`; canonical `34765672205 = FAILURE` because GitHub's hosted runner was shut down at 92% and pytest exited 143. No product assertion failed before shutdown; the new timezone tests passed. Treat as infrastructure interruption pending a clean exact-SHA canonical run, not a new product Error ID.
- UI: `4322820fd02e15e30626e42107291360d5f79b18`; UI Focused `34766506253 = SUCCESS`, Core Focused `34766506246 = SUCCESS`, canonical `34766506348 = SUCCESS`; Visual `34766501013 = FAILURE` at capture route identity.
- `main` and `bnbgrs/ATHENA` remain read-only. Error worker mutations remain confined to `postmerge/errors`.

## ITERATION-1 — ERR-0053 closure

Status: `FIXED`

Develop `1c20496e5e91c800050a9586dce7a903f9d86a6c` has canonical `34764344711 = SUCCESS`. The 44 px Send-target repair is therefore fully integrated and verified. Do not reopen without a new exact-SHA reproduction.

## ITERATION-2 — backend canonical red deduplicated

No Error ID opened.

Backend `b7a1358...` is owner-focused green. Its canonical Python job passed validator, Ruff, mypy, isolated desktop controller 6/6, new `test_job_schedule_definition.py` 2/2, existing schedule-definition tests, and proceeded through 92% of 5086 collected tests before the hosted runner emitted a shutdown signal and exited 143. Linux Storage, Windows release guards and Local Install/pypdf are green on the same SHA.

Action: request/consume a clean exact-SHA canonical rerun through the owning workflow/integrator. Do not change schedule/storage/runtime code merely to address runner termination.

## ITERATION-3 — ERR-0054 reclassified

Status: `STALE`

The historical missing-Windows-baseline root cause is not reproduced on current UI exact SHA. Current Visual run fails earlier during capture, so baseline comparison is skipped. `ERR-0054` must remain stale unless a future current exact SHA reaches comparison and reproduces the missing-baseline verdict.

## ITERATION-4 — ERR-0058 opened

Status: `OPEN`

Exact current UI Visual run: `34766501013` on `4322820fd02e15e30626e42107291360d5f79b18`.

Primary error:

`Workspace route identity drifted before capture: requested row 5, navigation row 1, page index 1.`

The harness itself passes Ruff, mypy, comparator tests, shared visual-token tests and primary-navigation accessibility tests. Capture exits 1 before route-identity verification/baseline comparison. Artifact `pathena-visual-4322820fd02e15e30626e42107291360d5f79b18` is uploaded. Current manifest reports all 11 assigned/captured reference surfaces but status `FAIL` with the row-5 route-drift error.

Ownership: UI/visual. Current UI commit adds `_link_top_navigation_tab_order()` and validates focus-chain ordering. Because the current failure occurs in navigation/capture sequencing and UI owns the same surface, Error worker must not parallel-patch UI product code.

Required UI closure: reproduce on an exact successor, isolate whether focus traversal or capture selection changes navigation row/page, apply the smallest fix without weakening route-identity enforcement, and obtain a Visual run that reaches route verification and baseline handling while UI Focused/Core Focused/canonical remain green.

## Persistent release guards

Current exact UI canonical Quality, Windows path/release guards, Linux Storage and Local Install/pypdf are green. The visual log contains one transient startup identity exception before a later successful Core startup, but it does not cause the run failure and canonical storage/restart guards pass. Do not open a storage/root-runtime error unless an exact current guard fails or the signature becomes the repeatable failing outcome.

## Next root cause

1. `ERR-0058` remains highest priority.
2. Consume terminal Develop `34766898131` without starting a competing canonical run.
3. Consume a clean backend exact-SHA canonical rerun after the runner-shutdown interruption.
4. Re-evaluate UI successor evidence; if UI already owns/fixes `ERR-0058`, close the parallel Error path and immediately select the next independent current failure.
