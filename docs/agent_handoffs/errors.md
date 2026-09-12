# pATHENA Error Handoff

## Baseline

- Develop: `54c990285503e5076d31f46408ef530b9f02de28` (`fix(ci): close core focused regression lint`).
- Current Develop canonical Quality `34715466882@54c990285503e5076d31f46408ef530b9f02de28 = IN_PROGRESS`; no competing run started by Errors.
- Develop parent `522a01050dba5b4dafa81d60573bd185a8e7e15b` canonical `34712404459 = FAILURE`; exact failure is Ruff `I001` in `tests/unit/test_core_focused_candidate_workflow.py`, while Windows path safety, Linux storage regressions, Local Install and full pytest pass. Current Develop fixes formatting only.
- Errors worker entered this run at `cc856567b5e7c05c8b36e919cddb7808476f366a`; ledger evidence commit this run is `e50a2bfb161ed656bf64db36a7d7a5e1cf2a280e`.
- Current workers: Spec/Core `9f2052b9c10668ad9eeeb2857dbcbb25145cc832`; Backend `365df03a040cb9dffddf6f942ae61a2cdb8dc375`; UI `6bc46a2464344d56ca00461df30ba4a619437498`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: `ERR-0042`, `ERR-0046`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0043`, `ERR-0045`.
- FIXED: `ERR-0044`, `ERR-0041`, `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## ITERATION-1 — ERR-0045 owner fixture repair verified

`ERR-0045 = FIXED_PENDING_VERIFY / P2`.

Backend advanced to exact `365df03a040cb9dffddf6f942ae61a2cdb8dc375` (`test(storage): model validated sidecar-free preflight`). The only mutation from the prior Storage product repair is `tests/unit/test_storage_database_startup_identity.py`.

The invalid helper no longer deletes WAL/SHM and then invokes `inspect_database_read_only()`, which could recreate them. It now validates metadata first, checkpoints/truncates, closes SQLite, removes sidecars, captures the file-set identity directly, proves both sidecars absent, and constructs `DatabasePreflightReport` from the already validated metadata plus that exact absent-sidecar identity.

Exact verification on the unchanged SHA is complete:

- Backend Focused `34714225610 = SUCCESS`.
- Storage Focused `34714225608 = SUCCESS`.
- canonical Quality `34714225599 = SUCCESS`.

No Storage/Recovery guard or product identity rule was relaxed. Final `FIXED` still requires integration and Develop canonical success.

## ITERATION-2 — ERR-0043 receives clean successor verification

`ERR-0043 = FIXED_PENDING_VERIFY / P1`.

The original product repair remains the `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc` lineage: existing sidecar replacement is fail-closed; only the exact absent-both -> published-both transition with unchanged primary DB may be accepted, followed by fresh exact-identity confirmation.

Successor `365df03a040cb9dffddf6f942ae61a2cdb8dc375` changes only the `ERR-0045` test fixture, not product guard code. Backend Focused, Storage Focused and canonical are all green there. This is the previously missing globally-green owner proof for the repaired guard.

Do not mark `FIXED` until this verified Backend lineage is integrated and the resulting Develop exact SHA is canonical green.

## ITERATION-3 — ERR-0042 exact remediation narrowed to one line

`ERR-0042 = OPEN / P1`.

Current Spec/Core exact `9f2052b9c10668ad9eeeb2857dbcbb25145cc832` still fails both Core Focused `34713779890` and canonical `34713779893`.

Downloaded focused diagnostics prove:

- Ruff: exactly one `I001` in `tests/unit/test_revision_change_explanation.py:1:1`.
- focused behavior tests: `6 passed`.
- Ruff remediation fixes exactly one thing: remove the extra blank line between the final import and `KNOWLEDGE_ID`.

Canonical diagnostics add one independent inherited Ruff defect in `tests/unit/test_core_focused_candidate_workflow.py`; that file belongs to Develop parent `522a010...` and is separately corrected by current Develop `54c99028...`. Full canonical pytest passes. Therefore the Spec/Core owner defect remains exactly the one-line import-spacing remediation above; the parent Develop lint is a deduplicated cascade, not another Spec/Core root cause.

Required owner action: apply the exact Ruff remediation only, then Core Focused + canonical success on one unchanged Spec/Core SHA, followed by integrated Develop canonical success for final closure.

## ITERATION-4 — ERR-0046 opened from UI-triggered Core lane

`ERR-0046 = OPEN / P2`.

Current UI exact `6bc46a2464344d56ca00461df30ba4a619437498` produced Core Focused `34714819122 = FAILURE`. Exact focused artifact shows Ruff `All checks passed!`, but pytest selects only two UI modules — `test_pathena_comfyui_shell.py` and `test_pathena_pallas_full_view.py` — and both are skipped at collection because PySide6 is absent in the Core-focused environment. The final focused outcome gate then correctly refuses success.

Root cause is harness ownership selection: `.github/workflows/core-focused-candidate.yml` selects every changed `tests/unit/test_*.py` as a Core-focused test while installing only the `dev` environment. UI-only PySide modules therefore enter a lane that cannot run them. This is not a UI product failure and must not be fixed by treating skipped-only execution as success.

Safe repair: narrow Core-focused test selection to Core-owned tests or an explicit ownership allowlist, while preserving deletion filtering, tracked-worktree fail-closed remediation, and final outcome enforcement. If UI modules are intentionally Core-owned, install the exact required runtime and demand runnable assertions instead.

Closure requires an exact UI-change case that no longer fails Core Focused spuriously plus proof that a genuine Core failure still fails the lane, then integrated canonical success.

## ITERATION-5 — UI canonical cascade deduplicated

UI canonical Quality `34714819100@6bc46a2464344d56ca00461df30ba4a619437498 = FAILURE`, but it does not add a UI product root cause. Exact canonical jobs show specification validator, mypy, full pytest, Local Install, Linux storage regressions and Windows path safety all passing; only Ruff fails. Downloaded canonical diagnostics identify the sole Ruff `I001` as `tests/unit/test_core_focused_candidate_workflow.py`, the same inherited Develop-parent defect already addressed by `54c99028...`. Full pytest is `5000 passed, 17 skipped`.

Therefore the canonical red UI SHA is deduplicated against the Develop-parent lint defect, while `ERR-0046` remains separately OPEN because it reproduces in Core Focused selection even though canonical pytest with desktop runtime is healthy.

## Integrator handoff

- `ERR-0043 = FIXED_PENDING_VERIFY / P1`: Backend product guard lineage now has Backend Focused + Storage Focused + canonical success on `365df03a...`; integrate only that verified lineage and require Develop canonical green before `FIXED`.
- `ERR-0045 = FIXED_PENDING_VERIFY / P2`: fixture repair on `365df03a...` exact-green in all three Backend/Storage/canonical lanes; no guard weakening.
- `ERR-0042 = OPEN / P1`: Spec/Core `9f2052b9...`; exact one-line Ruff remediation still unapplied; six behavior tests green.
- `ERR-0046 = OPEN / P2`: Core Focused harness selects UI-only PySide tests under Core-only runtime. Repair ownership selection/runtime, never skip-to-green.
- UI canonical failure on `6bc46a...` is not a UI product defect: full pytest `5000 passed, 17 skipped`; sole canonical Ruff failure is inherited `test_core_focused_candidate_workflow.py` from Develop parent.
- Current Develop `54c99028...` canonical `34715466882` remains in progress; consume it before another Develop mutation.

## CI discipline

- Before mutation, `postmerge/errors@cc856567b5e7c05c8b36e919cddb7808476f366a` had zero workflow runs.
- After ledger commit `e50a2bfb161ed656bf64db36a7d7a5e1cf2a280e`, Errors again had zero workflow runs before this handoff commit.
- No canonical run was started or duplicated by Errors.
- No product code or foreign worker branch was mutated.

## NEXT_ROOT_CAUSE

1. Consume Develop canonical `34715466882@54c99028...`; classify any failure by exact signature before opening anything.
2. Consume the next Spec/Core successor: `ERR-0042` should close owner-side only when Core Focused + canonical are green on one unchanged exact SHA.
3. Follow integration of Backend `365df03a...`; close `ERR-0043` and `ERR-0045` only after integrated Develop canonical success.
4. Follow a workflow successor for `ERR-0046`; require both non-spurious UI-change behavior and a negative Core-failure control before closure.
