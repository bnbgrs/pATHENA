# Error worker handoff

## Exact source of truth

- Develop: `a2dfc6b381ead94996f319ca06fc65e25992fb70`; canonical `34834496897 = SUCCESS`.
- Error worker before this refresh: `c54e7521da9ae20387312772c7b53b45ddc84b0e`; no exact workflow run exists on that documentation-only SHA.
- Spec/Core: `873c6e3e301d319fa7971cedf76fba0b4bf118a7`; canonical `34832425978 = SUCCESS`; Core Focused `34832426020 = FAILURE`.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; held closed absent a new exact matching failure.
- UI: `a88eac5f05db4128ae21b7c747e95c16a91191c4`; canonical `34819314295 = FAILURE`, UI Focused `34819314285 = FAILURE`, Core Focused `34819314380 = FAILURE`, Visual `34819309682 = FAILURE`; no newer exact UI successor exists.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ERR-0065 — OPEN — Spec/Core-owned focused-candidate enforcement failure

Exact Spec/Core SHA `873c6e3e...` is canonical green but exact Core Focused `34832426020` is red. Ruff, mypy and focused pytest use `continue-on-error`; their visible job-step conclusions are success, while the final `Enforce focused candidate outcomes` step fails. This proves at least one original focused substep outcome is failure and was masked at the step-conclusion level before the final fail-closed enforcement.

Exact diagnostics artifact: `core-focused-diagnostics-873c6e3e301d319fa7971cedf76fba0b4bf118a7`, artifact id `10342533865`.

Candidate product scope is `src/athena/core/application.py` plus `tests/unit/test_knowledge_inspection_application.py`. The focused changed-file selectors include the `test_knowledge*.py` test family but not `src/athena/core/application.py`. Spec/Core must inspect the exact artifact and repair the concrete hidden Ruff/mypy/pytest outcome without weakening enforcement. Error worker must not patch the same Core-owned product/test slice in parallel.

## ERR-0064 — FIXED

Earlier cross-ownership selector contamination remains closed. ERR-0065 is distinct and must not reopen ERR-0064 without a matching selector-contamination signature.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived fields, `assigned_reference_count=11`, and fail-closed exact-eleven PASS contract remain held.

## ERR-0063 — FIXED

No new exact matching eleven-capture/route regression.

## Current UI failures — OPEN / UI-owned

Latest exact UI SHA remains `a88eac5f...`; canonical, UI Focused, Core Focused and Visual are red, with no newer UI successor. Do not patch UI product code from `postmerge/errors`; consume the next UI successor and classify only new exact evidence.

## ERR-0054 — OPEN — UI/Visual Review

No baseline creation or acceptance by Error worker. Closure still requires truthful UI-owned 11/11 reference/render review and final visual-verdict success.

## Green / held clusters

- Current Develop exact canonical is green.
- Backend remains held closed absent a new matching exact-SHA failure.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.
- Error-worker 48px Send geometry remains `STALE`, not a new product root cause.

## Next root cause

1. Consume the Spec/Core successor that resolves ERR-0065; require exact Core Focused success and canonical green on the same candidate lineage.
2. Consume the next exact UI successor and classify only newly reproduced signatures.
3. Keep ERR-0064, ERR-0059 and ERR-0063 closed absent exact regression.
4. ERR-0054 remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
