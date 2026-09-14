# Manual promotion hardening handoff — 2026-09-14

## Exact lineage

- Integration target: `develop/pathena-next`.
- Exact base: `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`.
- Base canonical Quality: `34785279278 = SUCCESS`.
- Isolated branch: `manual/promotion-hardening-current-20260914`.
- Historical reviewed source: PR #88 / `manual/integrator-promotion-hardening-20260910`.
- `main` and `bnbgrs/ATHENA` remain untouched and read-only.

## Current problems reproduced on Develop

The current promotion path still has two independent fail-open surfaces.

### Candidate execution identity

`.github/workflows/promotion-readiness.yml` checks out a moving ref through `actions/checkout@v6` and does not independently prove that the worktree SHA equals the exact workflow trigger SHA. It also leaves checkout credentials at the action default and relies on floating major action tags.

For promotion evidence, the tested tree must be bound to the immutable candidate event SHA rather than merely to the expected branch name.

### Promotion tree guard

`scripts/promotion_guard.py` currently:

- accepts direct CLI invocation without `--actual-ref`, so a caller can skip ref verification entirely;
- accepts a symlink at the required canonical Quality workflow path if it resolves to a file;
- uses `Path.exists()` for forbidden legacy paths/trees, allowing a broken forbidden symlink to appear absent.

These are release-evidence boundary problems, not product-runtime changes.

## Bounded repair

Owned paths are exactly:

- `.github/workflows/promotion-readiness.yml`
- `scripts/promotion_guard.py`
- `tests/unit/test_promotion_guard.py`
- `docs/agent_handoffs/manual-promotion-hardening-current-20260914.md`

The current-base repair:

- stores `${{ github.sha }}` as `CANDIDATE_SHA`;
- checks out that exact SHA rather than the branch tip;
- pins `actions/checkout` and `actions/setup-python` to reviewed commit SHAs;
- disables persisted checkout credentials;
- proves `git rev-parse HEAD == CANDIDATE_SHA` before running quality tooling;
- disables setup-python `check-latest` drift;
- pins pip `26.1.2` and uv `0.11.21`;
- requires direct guard CLI invocation to provide `--actual-ref`;
- requires the canonical Quality workflow to be a non-symlink regular file;
- treats broken forbidden symlinks as present and therefore invalid.

The existing lock check, Ruff, mypy and focused promotion-guard pytest remain mandatory.

## Regression coverage

Focused tests now cover:

- valid candidate tree;
- all legacy forbidden files/trees;
- missing canonical Quality workflow;
- wrong candidate ref;
- required Quality workflow symlink rejection;
- broken forbidden file symlink rejection;
- broken forbidden tree symlink rejection;
- mandatory CLI `--actual-ref`;
- exact trigger-SHA checkout and immutable identity proof;
- pinned runtime inputs and resolver versions.

The code/workflow/test blobs intentionally match the previously reviewed PR #88 implementation, recreated on the current green Develop base instead of merging its stale history.

## Collision review

Fresh worker review during this run shows no active worker owns these paths:

- Backend is tree-synchronous with current Develop.
- Spec/Core changes only Merge/Split policy/test plus handoff.
- Errors changes only error ledger/handoff and visual-capture truth paths.
- UI changes Desktop/UI/visual-evidence paths.

The other manual current-base slices created in this run are also disjoint:

- PR #140 owns local-quality runner paths.
- PR #141 owns coordination-guard paths.

This slice does not change product runtime, Storage, Core, UI, Security, providers or worker handoffs.

## Verification contract

No local full-suite PASS is claimed from the connector-only execution environment. Required before integration:

1. canonical Specification Validator PASS;
2. canonical Ruff PASS;
3. canonical mypy PASS;
4. canonical full pytest PASS;
5. Linux Storage PASS;
6. Windows release-guard lane PASS;
7. Local install smoke PASS;
8. fresh Develop/worker collision review if any relevant branch advances.

In addition, the promotion-readiness workflow itself must remain syntactically valid and preserve the exact-SHA identity proof. Do not replace pinned actions with moving tags, restore credential persistence, relax symlink checks, make `--actual-ref` optional, add Skip/XFail, or weaken promotion evidence to make validation pass.

## Bot consumption

This is an Integrator/release-maintenance slice. Bots should not independently recreate PR #88 or mutate these four paths while this exact candidate is under verification. Any failure outside this ownership surface must be classified before scope is widened.
