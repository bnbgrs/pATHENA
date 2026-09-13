# pATHENA Error Hunter Handoff

## Current exact state

- Develop: `a9aaf5f414b7a030598d1735244bcbf6407e6bcb`; canonical Quality `34772777276 = IN_PROGRESS`.
- Error worker: latest mutation lineage starts at `cf8203ba11c205825363a57a424db8f3a9db2f42` and includes this handoff/ledger refresh only.
- Spec/Core: `7a04a10a6f20b7a780a2f6d2db1d15f7608c08b0`; canonical Quality `34771164034 = SUCCESS`.
- Backend: `fa019ac6017ce24ce826f4ae3cfb3b14a418b5c4`; latest exact canonical remains `34768709258 = SUCCESS`.
- UI: `b3066df5be557047c59331476ea1de4e79045e67`; UI Focused `34770820473 = SUCCESS`, Core Focused `34770820365 = SUCCESS`, canonical Quality `34770820352 = SUCCESS`, Visual `34770817654 = FAILURE` only at final verdict.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — ERR-0058 closed on current exact UI SHA

Status: `FIXED`

Visual run `34770817654` on `b3066df5be557047c59331476ea1de4e79045e67` now succeeds at both native eleven-surface capture and workspace route-identity verification. It continues through baseline comparison/proposal and artifact upload. The older row-5 fallback therefore does not reproduce on the current exact SHA and must not remain OPEN.

No Error-worker UI product patch was made.

## ITERATION-2 — ERR-0054 reopened on current exact UI SHA

Status: `OPEN`

The current visual run now reaches the baseline stage and fails only at `Enforce visual verdict`. `tests/qa/visual-baseline-windows.json` is absent on the exact UI SHA. This is the current exact-SHA reproduction of the missing-reviewed-baseline cluster.

Do not auto-accept the generated proposal. Review all eleven exact renderings against the authoritative references first. Comparator tolerances and final verdict enforcement remain fail-closed.

## ITERATION-3 — ERR-0059 remains current and Error-owned

Status: `OPEN`

Current UI harness still writes `captured_reference_count` from `expected_capture_count` and hard-codes the full eleven-surface list. That remains diagnostically false under partial capture.

Error worker hardened the existing regression contract in commit `cf8203ba11c205825363a57a424db8f3a9db2f42` so it now both requires actual `captures` derivation and explicitly rejects the two stale constant forms.

Implementation closure remains bounded to two manifest fields:

- `"captured_reference_surfaces": [capture["label"] for capture in captures]`
- `"captured_reference_count": len(captures)`

Keep `assigned_reference_count = 11` and the existing PASS requirement for all eleven captures. No route/baseline/tolerance/guard weakening.

## ITERATION-4 — current non-visual workers requalified

Spec/Core current exact SHA is canonical green. Backend current exact SHA remains canonical green. Develop has a newer exact canonical run in progress; no new Develop error is opened before terminal evidence exists.

Persistent release-guard signatures remain closed unless a current exact SHA reproduces them.

## Next root cause

1. Finish `ERR-0059` with the bounded harness implementation and focused verification.
2. For `ERR-0054`, consume the exact eleven-surface artifact and perform deliberate visual review before any baseline commit.
3. Consume Develop canonical `34772777276` when terminal and re-prioritize only from fresh exact-SHA failures.
