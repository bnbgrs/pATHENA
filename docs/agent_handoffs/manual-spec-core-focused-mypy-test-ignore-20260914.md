# Manual Spec/Core focused-mypy test-harness repair — 2026-09-14

## Purpose

Isolated repair for the current `postmerge/spec-core` candidate after the strengthened Core Focused gate correctly exposed candidate-owned mypy errors in negative runtime-boundary tests.

## Exact lineage

- Source worker head: `36452888894de49fdcd9b1968d1eaf83bc4412b0` (`fix(core): resolve merge split tuple typing`).
- Source Core Focused run: `34786426823 = FAILURE`.
- Source canonical Quality run at audit time: `34786426851`, still running when this repair was created.
- Manual branch: `manual/spec-core-focused-mypy-test-ignore-20260914`.
- Product code is unchanged.

## Root cause

The source candidate's product typing repair succeeded, Ruff succeeded, and focused pytest passed all 9 merge/split tests. The remaining focused failure was mypy in `tests/unit/test_knowledge_merge_split_policy.py`.

The two negative tests intentionally pass runtime-invalid values so the planner's fail-closed type checks are exercised. Their `# type: ignore[arg-type]` comments were attached to the function-call lines, while mypy 2.3.0 reports each `arg-type` error on the specific invalid argument line. That produced both `unused-ignore` and `arg-type` errors.

## Bounded repair

Move each existing `# type: ignore[arg-type]` to the exact intentionally invalid argument:

- `left_entity_id="not-a-uuid"` in the merge negative test;
- list-valued `result_entity_ids=[...]` in the split negative test.

No assertion, exception expectation, product signature, merge/split identity policy, persistence behavior, security rule, storage rule, or release guard is changed or weakened.

## Consumption rule

This branch is a worker-assistance/validation slice. Do not merge it directly into `develop/pathena-next`. Prefer the Spec/Core worker to consume the one-file test-harness delta, or merge this branch into `postmerge/spec-core` only after exact-head CI verifies the repair and current worker drift is rechecked.

No Skip/XFail, test deletion, product bypass, or type-contract weakening is permitted.
