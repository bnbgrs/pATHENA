# Quality incident — superseded GitHub Actions runs delay current-head evidence

## Scope

- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- Ownership: QUALITY/GATE
- Status: MITIGATED, supersession verified; newest-run execution still pending
- Detection date: 2026-08-23

## Evidence

At branch HEAD `025ca1ab6657e08748cbe96c148f021c97b0c3d2`, the pull-request-triggered ATHENA Quality Gate run #2477 was still `queued`. Its immediate parent `25e3573975247752376f6a4c74463630e6113a7e` also had pull-request run #2475 still `queued`.

The quality workflow at that point triggered on both `push` and `pull_request` and had no `concurrency` block. The branch is under high parallel write activity, so obsolete workflow runs can accumulate faster than they finish and delay evidence for the newest HEAD.

This is a Quality/CI infrastructure defect: it does not prove a product failure, but it makes current-head gate verification stale and increases runner consumption.

## Root cause

`.github/workflows/quality.yml` lacked GitHub Actions concurrency cancellation. Every new commit could enqueue another quality run even when an older run for the same event/ref had become obsolete.

## Mitigation

Commit `03e373d49d5832a2aac6fbfa6eb04a3bbca88326` adds:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event_name }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

The group is event-scoped deliberately. It cancels superseded PR runs against the same PR and superseded push runs against the same ref, while preserving the newest PR run for connector-based verification rather than allowing a push event to cancel it.

No product code, Backend tests, UI code, or UI tests were changed.

## Observed verification

- PR quality run #2490 for commit `a162164cfcbe182a5d1a399ed433b3e93290cfbe` completed with conclusion `cancelled` after the later PR run was created.
- PR quality run #2492 for commit `9f0e2717f282b6ea7c724545832e04575af806de` became the surviving newest run and was observed `pending` with its quality job still `queued`.
- This proves the new concurrency group supersedes newer-workflow PR runs as designed.
- Older runs such as #2477 were created before the workflow contained the concurrency group and remained queued; the new rule cannot retroactively assign those historical runs to a concurrency group.

## Remaining verification

1. Confirm the surviving newest PR run proceeds to execution once historical queue pressure clears.
2. Inspect its Specification/Ruff/mypy/pytest results.
3. Mark `QG-CI-SUPERSEDED-RUNS` DONE once both supersession and successful newest-run scheduling are observed.

The mitigation itself is verified. End-to-end queue recovery remains `IN_PROGRESS` because #2492 had not yet started its job at the last observation.
