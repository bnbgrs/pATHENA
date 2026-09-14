# Quality exact-head concurrency policy

Date: 2026-09-14
Issue: #169

## Problem

The canonical ATHENA Quality workflow is an exact-head integration gate. A completed run for an older pull-request head is useful historical diagnostics, but it cannot authorize a newer head for integration. With `cancel-in-progress: false`, obsolete full-pytest runs for the same PR consumed runner time while the current head waited behind them.

## Policy

The Quality concurrency group remains scoped by workflow name, event type and pull-request number or ref. `cancel-in-progress` is enabled only for `pull_request` events.

Consequences:

- a newer head of the same PR supersedes and cancels the older in-progress Quality run;
- different PR numbers remain independent concurrency groups;
- `pull_request` activity cannot cancel a `push` Quality run because event type is part of the group;
- push runs on `develop/pathena-next` and `main` remain non-cancelling even when newer pushes arrive;
- the newest exact PR head still requires a complete successful canonical Quality run before integration.

## Trade-off

Some tail diagnostics from a superseded head are intentionally discarded. This is acceptable because the stale head cannot authorize integration, while its already-completed fast checks and Git history remain available. Exact-head throughput is prioritized over finishing obsolete full-suite diagnostics.

## Regression boundary

`tests/unit/test_quality_workflow_concurrency.py` statically pins the event and PR/ref scoping and rejects an unconditional `cancel-in-progress: true` policy.
