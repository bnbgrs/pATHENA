# Quality incident — superseded GitHub Actions runs delay current-head evidence

## Scope

- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- Ownership: QUALITY/GATE
- Status: MITIGATED, verification pending
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

## Verification required

1. Observe a newer `agent/pathena` PR quality run after the mitigation commit.
2. Confirm older queued/in-progress PR runs for the same PR become cancelled/superseded rather than continuing to consume the queue.
3. Confirm the newest PR run proceeds to execution.
4. Once complete, inspect Specification/Ruff/mypy/pytest results and update `QG-CI-SUPERSEDED-RUNS` to DONE only with observed CI evidence.

## Current verification

Implementation commit exists, but CI behavior has not yet been observed conclusively. Status remains `IN_PROGRESS` / verification pending.
