# Error worker handoff

## Exact source of truth

- Develop: `ba6bc224cc152c144d13ca21730dad6620610abe`; canonical `34781654173 = SUCCESS`.
- Error worker before this handoff update: `20b489a739b64e276affa2cf2d6490ee4183b614`; latest exact canonical `34779840281 = FAILURE` only on stale inherited 48px Send-button geometry.
- Spec/Core: `b35033657b2809febb491235bb284b6219975cb2`; Core Focused `34780613663 = SUCCESS`, canonical `34780613667 = FAILURE` only in mypy.
- Backend: `82321f9acb6e542b11afa6b0b64568818f2432d1`; canonical `34780789750 = SUCCESS`.
- UI: `de4efa5d3814948d47d83484c4a27ac0c2daf64c`; current Core/UI focused and canonical lanes are green. UI handoff still reports `PAIRS_VERIFIED_0_OF_11` and visual integration readiness `NO`.

## ERR-0060 — OPEN — Spec/Core-owned

Exact current failure:

`src/athena/knowledge/merge_split_policy.py:77`

mypy reports that `(left, right)` has type `tuple[UUID, UUID]` while `superseded` was inferred from the one-element branch as `tuple[UUID]`.

Evidence around the failure is otherwise green:

- Specification Validator: success.
- Ruff: success.
- Core Focused: success.
- canonical pytest: `5109 passed, 17 skipped`.
- Linux Storage: success.
- Windows release guards: success.
- Local Install/pypdf: success.

Bounded owner action: annotate `superseded` as a variable-length UUID tuple such as `tuple[UUID, ...]` without semantic changes, run the merge/split focused tests and mypy, then require exact-SHA Core Focused plus canonical success. Error worker must not parallel-edit this Spec/Core product slice while the owner branch remains active.

## ERR-0054 — OPEN — UI/Visual Review-owned

Do not create or accept a baseline from the Error worker.

Current UI handoff still has `PAIRS_VERIFIED_0_OF_11`, visual readiness `NO`, integrator readiness `NO`. The older visual verdict failures are historical for older SHAs; current UI is technically canonical green but the eleven reference/render pairs are not approved.

Required UI closure: capture the exact current candidate, review all 11 reference/render pairs, approve a baseline only after review, and then require the exact-SHA 11-Surface Visual final verdict to pass. Do not relax comparator tolerances, route identity, manifest truth or verdict enforcement.

## ERR-0059 — FIXED

Do not revisit unless a new exact-SHA manifest-truth regression reproduces.

Current Develop `ba6bc224...` contains the bounded fix:

- `captured_reference_surfaces = [capture["label"] for capture in captures]`
- `captured_reference_count = len(captures)`
- `assigned_reference_count = 11` unchanged
- fail-closed capture/verdict behavior retained

Develop canonical `34781654173 = SUCCESS`, so the integrated implementation is green.

## Stale cascade

The Error worker's own canonical red on inherited 48px Send geometry remains `STALE`; current Develop is canonical green with the authoritative 44px contract. Do not patch this stale UI baseline on the Error worker.

## Next root cause

1. Consume Spec/Core successor evidence for `ERR-0060`; no parallel product mutation.
2. Keep `ERR-0054` handed to UI/Visual Review until 11/11 pairs are actually reviewed and exact visual verdict is green.
3. Scan only for new current exact-SHA Error-owned failures. Green Develop/Backend/UI clusters are not diagnosis targets.
