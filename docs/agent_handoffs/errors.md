# Error worker handoff

## Exact source of truth

- Develop: `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`; canonical `34785279278 = SUCCESS`.
- Error worker before this handoff update: `ac049c2bd02c1ed0f78e299df2fd1e56c77c9770`; exact canonical `34785825895 = FAILURE` only on stale inherited 48px Send-button geometry. No queued/in-progress Error-worker run existed before this mutation.
- Spec/Core: `36452888894de49fdcd9b1968d1eaf83bc4412b0`; canonical `34786426851 = SUCCESS`, Core Focused `34786426823 = FAILURE` on the new focused mypy contract.
- Backend: `e4e1244e8482ac7d78e557ded5f91252cccc0347`; canonical `34786818234 = SUCCESS`.
- UI: `de4efa5d3814948d47d83484c4a27ac0c2daf64c`; Core Focused `34779940800 = SUCCESS`, UI Focused `34779940824 = SUCCESS`, canonical `34779940794 = SUCCESS`; visual review remains fail-closed.

## ERR-0062 — OPEN — Spec/Core-owned test typing

Current Spec/Core product fix for the prior planner tuple inference is canonical-green, but the strengthened focused gate now exposes a distinct test-typing failure.

Exact Core Focused run `34786426823` on `36452888894de49fdcd9b1968d1eaf83bc4412b0` executes Ruff, mypy and focused pytest. Ruff and pytest pass; the downloaded exact diagnostics report four mypy errors in `tests/unit/test_knowledge_merge_split_policy.py`:

- the call-line ignores on `plan_knowledge_merge(` and `plan_knowledge_split(` are unused;
- `left_entity_id="not-a-uuid"` is intentionally a `str` where `UUID` is declared;
- `result_entity_ids=[...]` is intentionally a `list[UUID]` where `tuple[UUID, ...]` is declared.

The tests are valid negative-runtime tests; the ignore placement is wrong for current mypy.

Bounded Spec/Core action: keep runtime-invalid values and assertions unchanged, move/narrow `# type: ignore[arg-type]` onto the exact invalid argument expressions (or equivalent narrow typing accommodation), then require exact Core Focused success while preserving canonical success. Do not disable mypy, remove tests, broaden ignores, weaken signatures or change planner runtime semantics.

## ERR-0060 — FIXED — planner tuple inference

Spec/Core successor `36452888894de49fdcd9b1968d1eaf83bc4412b0` is exact canonical-green (`34786426851 = SUCCESS`). The old planner mypy failure is closed. The current Focused red is `ERR-0062`, not a recurrence.

## ERR-0061 — FIXED — focused mypy qualification blind spot

Develop `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5` is exact canonical-green (`34785279278 = SUCCESS`). Current Spec/Core Core Focused run `34786426823` proves the added mypy step is active and fail-closed: final enforcement rejects the candidate when mypy evidence is not successful. No guard relaxation was introduced.

## ERR-0054 — OPEN — UI/Visual Review-owned

Do not create or accept a baseline from the Error worker. Current UI handoff remains `PAIRS_VERIFIED_0_OF_11`; closure still requires all eleven exact reference/render pairs reviewed and an exact-SHA 11-Surface Visual final verdict success.

## ERR-0059 — FIXED

Do not revisit unless a new exact-SHA manifest-truth regression reproduces.

## Green clusters

- Develop canonical: SUCCESS.
- Backend current exact canonical: SUCCESS.
- UI current exact Core Focused, UI Focused and canonical: SUCCESS.

Do not reopen these clusters without a new matching exact-SHA failure signature.

## Stale cascade

The Error worker's own canonical red on inherited 48px Send geometry remains `STALE`; current Develop preserves the authoritative 44px contract. Do not patch this stale UI baseline on `postmerge/errors`.

## Next root cause

1. Consume the Spec/Core successor for `ERR-0062`; no parallel test mutation.
2. Keep `ERR-0054` handed to UI/Visual Review until 11/11 pairs are actually reviewed and the exact visual verdict is green.
3. Scan only for new current exact-SHA Error-owned failures. `ERR-0059`, `ERR-0060` and `ERR-0061` are closed and remain untouched absent a new regression.