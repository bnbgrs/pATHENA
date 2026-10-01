# CI superseded PR-run concurrency — 2026-10-02

## Ausgangslage

During the 2026-10-02 engineering run, GitHub Actions queue depth grew from 146 to
184 queued runs while current product PRs were still waiting for runners.

A sample of the first 100 queued runs contained 56 runs belonging to duplicate
`workflow + pull-request branch` groups. Examples included five queued UI-Focused
and five queued Visual runs for different obsolete heads of the same PR branch.

## Root Cause

Several focused workflows used the exact PR head SHA as their concurrency group and
set `cancel-in-progress: false`. A new commit therefore created a new concurrency
group instead of superseding the old one.

The 11-surface visual workflow was stricter still:
`github.sha + github.run_id` made every run's group unique, so GitHub could never
auto-cancel an obsolete PR-head run.

This preserved obsolete exact-head evidence at the cost of starving the current head.
For pull requests the current head is the integration candidate; old head runs should
be cancelled once a newer head exists.

## Änderungen

PR-only focused workflows now group by stable PR number and use
`cancel-in-progress: true`:

- Backend Focused Candidate
- Core Focused Candidate
- Storage Focused Candidate
- UI Focused Candidate

Mixed-event workflows now use a stable PR-number group for pull requests and cancel
only pull-request supersessions:

- 11-Surface Visual Regression
- Windows Runtime Boundary

Push and manual/workflow-dispatch runs are not auto-cancelled by these mixed-event
changes. Exact candidate checkout/proof logic inside each workflow is unchanged.

A regression test reads only each workflow's `concurrency:` block and verifies that
PR workflows no longer key concurrency by head SHA or unique run ID.

## Dateien

- `.github/workflows/backend-focused-candidate.yml`
- `.github/workflows/core-focused-candidate.yml`
- `.github/workflows/storage-focused-candidate.yml`
- `.github/workflows/ui-focused-candidate.yml`
- `.github/workflows/ui-snapshot.yml`
- `.github/workflows/windows-runtime-boundary.yml`
- `tests/unit/test_ci_concurrency_contract.py`
- this handoff

## Nicht verändert

- `.github/workflows/quality.yml`: already has the correct stable PR group and
  pull-request-only cancellation.
- `.github/workflows/windows-package.yml`: actively owned by packaging PR #381;
  deliberately excluded to avoid conflict.
- Bot schedules/configuration: unchanged.
- Product code: unchanged.

## Erwartetes Verhalten danach

When a bot pushes a newer commit to the same PR:
- obsolete queued/running Focused/Visual/Windows-Runtime PR runs are cancelled;
- the new head receives the gate;
- unrelated PRs do not cancel each other;
- push/manual exact-candidate runs retain their existing non-cancelling semantics.

This reduces runner starvation without weakening any assertion, test, visual
threshold, exact-SHA checkout or release gate.

## Parallelität / Konfliktrisiko

Historical PR #314 also touches Core/UI/Visual workflow files but is an old,
merge-conflicted V3 candidate. Do not let it overwrite these current-Develop
concurrency blocks if it is ever revived.

Active #327 owns `quality.yml`, which this slice intentionally does not touch.
Active #352 owns the PALLAS capture script, not `ui-snapshot.yml`.
Active #381 owns `windows-package.yml`, which this slice intentionally does not
touch.

## Validierung

In-PR self-validation is intentional: after the first candidate head queued the
affected workflows, a documentation-only successor commit is pushed on this same PR.
Because the workflow definitions now group by PR number, GitHub should cancel the
older #389 PR-head runs and retain only the successor head. This validates the
concurrency behavior itself rather than only its YAML/text contract.

Before change:
- queue depth observed: 146, then 184;
- first 100 queued runs contained 56 entries in duplicate PR workflow/branch groups.

After change, exact-head CI must validate YAML parsing and the new unit concurrency
contract. No claim is made that already queued runs disappear retroactively until
this workflow configuration reaches the relevant base/PR context.

## Branch

- Branch: `ci/cancel-superseded-pr-runs-20261002-sol`
- Parent: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`
