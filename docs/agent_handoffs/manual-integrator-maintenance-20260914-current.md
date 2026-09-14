# Integrator maintenance consolidation — 2026-09-14 current Develop

## Exact lineage

- Integration target: `develop/pathena-next`.
- Exact current base: `5024a7c2b60c80083d1650ae924c89cb3085019e`.
- Base canonical Quality: run `34815625453` is the required exact-base verification and was still in progress when this handoff revision was written.
- Prior immediately-green Develop base: `3231615650473fd549a7d852fb3bbe215f7b721f`, canonical run `34811112376 = SUCCESS`.
- Current maintenance commit before this handoff: `0739dee6348371c6581ed601311520de6923d204`, whose direct parent is the exact current base above.
- Isolated branch: `manual/integrator-maintenance-20260914-current`.
- `main` remains untouched.

This branch consolidates three maintenance slices that were each independently canonical-green on the earlier exact Develop base `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`:

- PR #140 / `7aa5f19cbb1be2ef5f4377b600475ab71dcd718a` — canonical run `34792310407 = SUCCESS`;
- PR #141 / `e548075cda5e7b35e6a87364dba22445348647a6` — canonical run `34792553351 = SUCCESS`;
- PR #142 / `1228adabf77988e3b70e0bee987114d7c75d8ee3` — canonical run `34792653158 = SUCCESS`.

Develop advanced after those runs. The old-base-to-current-base changes were reviewed before reconstruction. The later `5024a7c2...` base increment adds Core claim-inspection composition and progress documentation only; it does not touch any functional maintenance path owned here. Rather than merge stale branch histories, the nine functional blobs were reconstructed directly on the exact `5024a7c2...` tree via a new Git tree/commit.

## Consolidated ownership

Owned paths are exactly:

- `.github/workflows/promotion-readiness.yml`
- `scripts/quality.py`
- `scripts/coordination_guard.py`
- `scripts/promotion_guard.py`
- `tests/unit/test_quality_gate_config.py`
- `tests/unit/test_quality_script.py`
- `tests/unit/test_local_quality_runner.py`
- `tests/unit/test_coordination_guard.py`
- `tests/unit/test_promotion_guard.py`
- `docs/agent_handoffs/manual-integrator-maintenance-20260914-current.md`

No pATHENA product runtime, desktop UI, Storage, Knowledge, provider, scheduler, Security, or worker-handoff path is intentionally changed.

## Local quality reproducibility

`scripts/quality.py` now mirrors the current canonical Python quality lane instead of using the caller's ambient interpreter:

- validates `uv lock --check` first;
- runs validator, Ruff, mypy, and pytest through `uv run --locked --extra dev --extra desktop`;
- anchors subprocesses to repository root;
- defaults Qt to `offscreen` while preserving an explicit override;
- mirrors the canonical isolated `test_desktop_api_controller.py` interpreter plus the remaining suite;
- retains fail-fast and `--keep-going` modes;
- adds a side-effect-free `--dry-run` exact command plan;
- fails closed with exit 127 if `uv` cannot start.

Regression coverage prevents the local runner from silently drifting away from `.github/workflows/quality.yml`.

## Coordination evidence hardening

Candidate diff evidence now fails closed when internal candidate identity is incomplete or contradictory:

- every commit must contain at least one non-blank path;
- a changed candidate SHA requires commits;
- supplied commits must advance beyond the base SHA;
- the final supplied commit SHA must equal the declared candidate SHA.

Existing active-claim, completed-claim, stale-ledger, product/non-product classification, and coverage behavior is preserved.

## Promotion evidence hardening

Promotion execution is now tied to immutable candidate evidence:

- `${{ github.sha }}` becomes the exact `CANDIDATE_SHA`;
- checkout and setup-python are pinned to reviewed action commit SHAs;
- checkout uses the exact candidate SHA and disables persisted credentials;
- the workflow proves `git rev-parse HEAD == CANDIDATE_SHA` before quality tooling;
- Python 3.12 selection does not use `check-latest`;
- pip and uv inputs are pinned;
- direct guard invocation requires `--actual-ref`;
- the canonical Quality workflow must be a non-symlink regular file;
- broken forbidden legacy symlinks count as present and fail closed.

## Current worker collision boundary

Fresh heads observed during this consolidation:

- Backend `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`;
- Spec/Core `postmerge/spec-core@ae82147ab8de6d3805bb5f2299497296af8ff19f`;
- Errors `postmerge/errors@35871d5e32dd49306b433374de9b2693048eb24f`;
- UI `postmerge/ui@5c2f066a9542569f8f23398e10cd7187c4722882`.

The consolidation deliberately does not touch the active UI 44-vs-48 send-button contract issue or visual-reference work. Those remain UI-owned.

## Verification contract

This exact current-base consolidation requires both:

1. exact-base Develop run `34815625453` to complete successfully; and
2. a fresh exact-head canonical run on this branch after the current handoff commit.

Candidate requirements:

1. Specification Validator PASS;
2. Ruff PASS;
3. mypy PASS;
4. isolated Desktop API controller PASS;
5. remaining full pytest suite PASS;
6. Linux Storage PASS;
7. Windows path/release-guard lane PASS;
8. Local Install smoke PASS;
9. no unexpected diff paths;
10. fresh collision check if Develop or a relevant worker changes an owned path before merge.

Do not weaken tests, add Skip/XFail, restore ambient Python, relax candidate identity, relax symlink/ref checks, or use a moving action tag to obtain green CI.

## Superseded historical PRs

If this exact current-base branch reaches canonical green and is integrated, PRs #140, #141 and #142 are superseded and should be closed without merge. Their successful runs remain historical evidence for the three isolated source slices.
