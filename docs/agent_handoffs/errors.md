# pATHENA Error Handoff

## Baseline

- Develop: `5eecb5f937de9325a9673df5f1a23d2f1b5e87cf`.
- Errors worker entered at `3f7f5e35b2248688de4203c1f072e8a9cda92dbc`; current ledger commit: `718a54123ca8f8759d594fe65aa14ac2b9453f14`.
- Current workers: Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; Backend `c5151466928dbe751a2e62c210717d0858a74bd3`; UI `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`.
- Develop canonical `34706615596@5eecb5f937de9325a9673df5f1a23d2f1b5e87cf = IN_PROGRESS`; no competing run started by Errors.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: `ERR-0042`, `ERR-0043`, `ERR-0044`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0041`, `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## ITERATION-1 — ERR-0042 exact owner repair diagnostics consumed

`ERR-0042` remains `OPEN / P1`.

Current Spec/Core exact head is `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`. Exact Core-focused diagnostics from run `34709904332` were downloaded and inspected:

- `ruff.txt`: exactly one `I001` at `tests/unit/test_revision_change_explanation.py:1:1`, `Import block is un-sorted or un-formatted`.
- `pytest.txt`: `6 passed in 0.17s`.

The owner commit `fix(core): normalize revision change import` therefore did not fix the Ruff blocker, but the revision-change behavior tests remain fully green. Canonical `34709904327` is still active; canonical Ruff is already failed while specification validator and the available platform/storage jobs are green.

A second harness defect was isolated in the same workflow: the Ruff-remediation step requires a completely clean worktree after earlier steps have created `.focused-evidence/ruff.txt` and `.focused-evidence/pytest.txt`. Thus the remediation step itself fails instead of returning the auto-fix diff. This does not change the product diagnosis; the real `I001` remains current.

Owner action: run the pinned Ruff fixer outside that dirty evidence state or make the remediation cleanliness check ignore its own evidence files, then apply only the exact formatting correction. Require Core Focused and canonical Quality green on one unchanged exact Spec/Core SHA before reclassification.

## ITERATION-2 — ERR-0043 opened: foreign SQLite sidecar accepted

New cluster: `ERR-0043 = OPEN / P1`.

Current Backend exact reproducer: `c5151466928dbe751a2e62c210717d0858a74bd3`.

Exact Storage-focused artifact from `34708379880` was downloaded and inspected:

- Ruff: all checks passed.
- mypy: success, 35 source files.
- pytest: `2 failed, 29 passed`.

Failure 1 is a current Storage release-guard regression: `test_bound_preflight_rejects_sidecar_mutation_before_writer_open` replaces the preflight WAL sidecar with literal foreign bytes and expects `DatabaseStartupIdentityChangedError`; current `SQLiteDatabase.start()` raises nothing. The candidate `_revalidate_existing_identity()` verifies only that the primary database identity is unchanged and then accepts the refreshed file-set identity, so a replaced existing WAL/SHM sidecar can be admitted.

Failure 2 invalidates the new positive test setup: `test_bound_preflight_accepts_valid_concurrent_sidecar_publication` expects a newly published sidecar identity, but `published_identity == original_identity`. `_create_current_database()` already left WAL/SHM present, so this fixture never demonstrates the intended absent-to-published transition.

Safe owner repair is bounded: retain fail-closed rejection of any replacement for a sidecar that existed at preflight. If absent-at-preflight sidecar publication must be supported, construct that state explicitly, prove the sidecar was absent, and validate only the legitimate publication transition. Do not weaken the negative substitution test or existing Storage/Recovery guards.

Backend canonical `34708379877` remains active; its canonical Ruff, mypy, Linux storage regressions, Windows release guards and local install are green, but that does not override this exact focused regression.

## ITERATION-3 — ERR-0044 opened: Core Focused selects deleted files

New cluster: `ERR-0044 = OPEN / P2`.

Current exact reproducer is Core Focused `34709115243` on UI head `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`. Downloaded diagnostics show:

- Ruff `E902` only for missing `src/athena/knowledge/orphan_knowledge.py` and `tests/unit/test_orphan_knowledge.py`.
- Pytest runs zero tests and errors because `tests/unit/test_orphan_knowledge.py` does not exist.

This is not an independent UI product defect. The Core-focused workflow uses `git diff --name-only BASE CANDIDATE` and then sends every selected Core/test path to Ruff/Pytest, including files deleted by the candidate lineage. Minimal harness repair is to exclude deletions consistently, e.g. `--diff-filter=ACMR`, in changed Core Python selection, focused-test selection and remediation selection.

Errors did not create a duplicate workflow file: `.github/workflows/core-focused-candidate.yml` is absent from the current divergent `postmerge/errors` lineage, so there is no safe surgical in-place mutation there without importing unrelated workflow history. The exact fix is handed to the current workflow/integration lineage.

## ITERATION-4 — release-guard and ownership classification

Current exact evidence separates the clusters cleanly:

- `ERR-0042`: Core-owned Ruff formatting defect; behavior tests green.
- `ERR-0043`: Backend-owned Storage identity-continuity regression; real negative Storage test fails and must block integration.
- `ERR-0044`: CI harness deleted-path selection defect; not UI product behavior.

No historical closed error was reopened merely because of an old ID. No product code outside Errors was mutated. No canonical run was duplicated. Windows packaged/runtime guards and Linux storage regression jobs available on the Backend canonical remain green, but `ERR-0043` still blocks that Backend candidate because its exact changed Storage contract is red.

## Integrator handoff

- `ERR-0042 = OPEN / P1`; Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; exact Core Focused `34709904332 = FAILURE`, one I001, six focused tests pass; canonical `34709904327` active with Ruff failed.
- `ERR-0043 = OPEN / P1`; Backend `c5151466928dbe751a2e62c210717d0858a74bd3`; Storage Focused `34708379880 = FAILURE`, exact pytest `2 failed, 29 passed`; foreign existing sidecar replacement is currently accepted. Do not integrate this Backend Storage change.
- `ERR-0044 = OPEN / P2`; Core Focused harness on UI exact `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`; deleted orphan-knowledge paths are passed to Ruff/Pytest. Fix diff selection, not UI product code.
- Develop `5eecb5f937de9325a9673df5f1a23d2f1b5e87cf` canonical `34706615596` remains active.

## CI discipline

- Errors heads checked before each mutation had zero workflow runs, including `261fc5213330c7abdd12c29c11677437604806fc`, `a9f5d1783fe99d95af954eca8f66bb0e9e3cedee`, and `718a54123ca8f8759d594fe65aa14ac2b9453f14`.
- No canonical run was started or duplicated by Errors.
- No product code or foreign worker branch was mutated.

## NEXT_ROOT_CAUSE

1. Consume current Spec/Core successor/final canonical and close only when exact Ruff + canonical are green.
2. Consume Backend successor/final canonical; verify `ERR-0043` first because it is a Storage/release invariant regression.
3. Verify a workflow-lineage fix for `ERR-0044` with a candidate that deletes Core/test paths and another that modifies normal Core/test files.
4. Consume UI and Develop canonical results and classify only exact remaining failures.
