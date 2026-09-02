# Quality incident — superseded GitHub Actions runs delay current-head evidence

## Scope

- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- Ownership: QUALITY/GATE
- Status: MITIGATED, final scheduling behavior under verification
- Detection date: 2026-08-23

## Evidence

At branch HEAD `025ca1ab6657e08748cbe96c148f021c97b0c3d2`, the pull-request-triggered ATHENA Quality Gate run #2477 was still `queued`. Its immediate parent `25e3573975247752376f6a4c74463630e6113a7e` also had pull-request run #2475 still `queued`.

The quality workflow originally triggered on both `push` and `pull_request` and had no `concurrency` block. The branch is under high parallel write activity, so obsolete workflow runs could accumulate faster than they finished and delay evidence for the newest HEAD.

This is a Quality/CI infrastructure defect: it does not prove a product failure, but it makes current-head gate verification stale and increases runner consumption.

## Root cause and refinement

The first mitigation, commit `03e373d49d5832a2aac6fbfa6eb04a3bbca88326`, introduced an event-scoped concurrency group with `cancel-in-progress: true`. This successfully collapsed superseded PR runs: runs #2490, #2492, #2494, #2498, #2514, #2526, #2543 and later runs were observed cancelled after newer commits arrived.

That observation also exposed a second-order problem specific to this continuously written branch: with `cancel-in-progress: true`, a gate can be cancelled before producing any baseline whenever commits arrive faster than runner scheduling. The long-lived CI carrier PR also means `pull_request.paths` evaluates the accumulated PR diff, so path filtering cannot reliably classify the newest commit as documentation-only.

A temporary documentation-specific workflow/path split was therefore tested and then removed before finalizing because it would add another PR workflow on this cumulative-diff PR without eliminating the PR full-gate trigger.

The final Quality-owned scheduling policy is implemented by commits `dd23cb21983b5f3c4028676c5b9ec47bfa4f8dff`, `b0701feadcbe1d4456fabe12f61828ac5c090a10`, and `00b30eed918de6b6d04a4493d233877cf76f8f2b`:

```yaml
on:
  push:
    branches:
      - main
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.event_name }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: false
```

Rationale:

- `agent/pathena` already has the persistent PR carrier, so feature-branch pushes no longer create a second full-gate copy for the same commit.
- `main` push coverage is retained for future merged state.
- The PR workflow remains connector-visible and continues to validate every branch update.
- GitHub concurrency retains at most one running and one pending member of a group. With `cancel-in-progress: false`, an active gate is allowed to finish while newer pending work converges toward the latest branch state instead of repeatedly terminating the active baseline.
- The workflow still runs `scripts/quality.py --keep-going`, so one completed gate exposes Specification, Ruff, mypy, and pytest evidence even when an earlier check is red.

No product code, Backend tests, UI code, or UI tests were changed by these CI mitigations.

## Regression coverage

`tests/unit/test_quality_workflow_contract.py` now locks the intended scheduling contract:

- event/ref-scoped concurrency exists;
- `cancel-in-progress` stays false;
- feature-branch push duplication is avoided by limiting push-triggered full gates to `main`;
- CI continues to invoke `scripts/quality.py --keep-going`.

The regression test has not yet executed because GitHub runner scheduling is still pending and local execution is unavailable in the connector runtime.

## Observed verification

- The initial concurrency implementation demonstrably cancelled superseded PR runs as designed.
- The final scheduling implementation is present on `agent/pathena`.
- A PR quality run was created for commit `00b30eed918de6b6d04a4493d233877cf76f8f2b` as run #2572 and was observed `pending` immediately after creation.
- Further commits landed before a completed final-policy run was available, so end-to-end evidence that an active run now survives subsequent commits remains pending.
- Older pre-concurrency runs cannot be retroactively assigned to the new concurrency group.

## Remaining verification

1. Observe the first final-policy PR gate reach `in_progress`.
2. After at least one newer commit lands, verify that the active gate is not cancelled.
3. Inspect the completed gate's Specification/Ruff/mypy/pytest results.
4. Update `QG-CI-SUPERSEDED-RUNS` and `QG-CI-FAILFAST-COVERAGE` from executed evidence only.

The infrastructure defect has a concrete mitigation and regression contract. End-to-end scheduling recovery remains `IN_PROGRESS` until a final-policy gate actually starts and completes.
