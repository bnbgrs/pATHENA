# pATHENA Error Hunter Handoff

## Current exact state

- Develop: `a9aaf5f414b7a030598d1735244bcbf6407e6bcb`; canonical Quality `34772777276 = SUCCESS`; second exact-SHA Quality run `34774341613 = SUCCESS`.
- Error worker: implementation candidate lineage now includes `ed1ea5c9aadcb06f1b71e5ae9eec2173080a7e72` plus the subsequent ledger/handoff refresh commits only.
- Spec/Core: `af5283d7a6c6c5f1e256af1b2f07678ab52cd87b`; canonical Quality `34774353839 = SUCCESS`.
- Backend: `7516c67e1c19fded96239639aa2182c65b236b69`; Backend Focused `34774634769 = SUCCESS`, canonical Quality `34774634757 = SUCCESS`.
- UI: `b3066df5be557047c59331476ea1de4e79045e67`; UI Focused `34770820473 = SUCCESS`, Core Focused and canonical Quality green; Visual `34770817654 = FAILURE` only at final verdict.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — ERR-0059 bounded implementation completed

Status: `FIXED_PENDING_VERIFY`

Commit `ed1ea5c9aadcb06f1b71e5ae9eec2173080a7e72` modifies only `scripts/render_pathena_ui_snapshot.py` and only the two false manifest fields:

- `"captured_reference_surfaces": [capture["label"] for capture in captures]`
- `"captured_reference_count": len(captures)`

The commit preserves:

- `assigned_reference_count = 11`;
- the existing fail-closed PASS predicate requiring no capture errors and exactly eleven captures;
- route-identity enforcement;
- baseline handling and final visual verdict;
- comparator behavior;
- all Test, Security, Storage and Recovery guards.

Exact commit diff confirms no unrelated product change.

## ITERATION-2 — ERR-0059 verification boundary

The existing regression test `tests/qa/test_visual_capture_manifest_truth.py` already requires both actual-capture expressions and rejects both stale constant forms. Exact source inspection on `ed1ea5c9...` satisfies that contract.

However, `postmerge/errors` has no open PR and no workflow run on the candidate SHA. Therefore there is not yet executed focused/canonical evidence and the status must remain `FIXED_PENDING_VERIFY`, not `FIXED`.

Integrator/next runner should execute the focused regression on this exact candidate or on a bounded successor containing exactly this harness diff. After a real green execution, close `ERR-0059`; do not modify the implementation again unless a new regression reproduces.

## ITERATION-3 — Develop/Spec-Core/Backend requalification

No new independent Error-owned failure is present on these current exact heads:

- Develop `a9aaf5f4...`: exact canonical Quality is terminal `SUCCESS`.
- Spec/Core `af5283d7...`: exact canonical Quality is `SUCCESS`.
- Backend `7516c67e...`: exact Backend Focused and canonical Quality are both `SUCCESS`.

Per green-stays-green, none is a diagnosis target this run.

## ITERATION-4 — ERR-0054 review ownership retained

Status: `OPEN`, UI/Visual-review-owned.

Current UI exact SHA remains `b3066df5...`. Its visual run reaches all eleven captures, route identity, compare/proposal and artifact upload, then fails only at final visual verdict because a reviewed Windows baseline is absent.

Error worker must not generate or accept a baseline in parallel. UI/Visual owner must review all eleven exact reference/render pairs first; only then may a reviewed baseline be committed and exact-SHA Visual Regression rerun.

## ITERATION-5 — next-error scan

No fresh exact-SHA canonical failure on current Develop, Spec/Core, Backend or UI establishes another independent Error-owned root cause. Persistent release-guard signatures remain closed without a current reproduction.

Do not manufacture work from historical red runs. Consume only new exact-SHA failure evidence.

## Integrator handoff

For `ERR-0059`, the bounded implementation commit is:

`ed1ea5c9aadcb06f1b71e5ae9eec2173080a7e72`

Required verification before closure:

1. run `tests/qa/test_visual_capture_manifest_truth.py` on the exact candidate or bounded successor;
2. keep all assertions unchanged;
3. if integrated elsewhere, require relevant exact-SHA regression/canonical evidence;
4. then set `ERR-0059 → FIXED` and stop touching it unless a new exact-SHA regression appears.

For `ERR-0054`, remain UI/Visual-review-owned. No automatic baseline acceptance.

## Next root cause

1. `ERR-0059` verification only; implementation is complete.
2. `ERR-0054` closure evidence only, no Error-worker mutation.
3. Otherwise wait for the next fresh exact-SHA Error-owned failure and prioritize by severity/integration impact.
