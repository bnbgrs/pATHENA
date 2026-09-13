# Error worker handoff

## Exact source of truth

- Develop: `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`; canonical `34785279278 = IN_PROGRESS`. Validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are already green; full pytest is still running.
- Error worker before this handoff update: `db47bc9d89633034d2897367caee86b96f945fd8`; latest exact canonical `34783072166 = FAILURE` only on stale inherited 48px Send-button geometry. No queued/in-progress Error-worker run existed before this mutation.
- Spec/Core: `93358a1c7a310a2da4279fb51b1e99a1bde505ab`; Core Focused `34783221743 = SUCCESS`, canonical `34783221804 = FAILURE` solely in mypy.
- Backend: `dda2dd74c0989f7ec453e8a2b7d8122f85a9251c`; canonical `34784000745 = SUCCESS`.
- UI: `de4efa5d3814948d47d83484c4a27ac0c2daf64c`; current focused lanes are green and visual review remains fail-closed.

## ERR-0060 — OPEN — Spec/Core-owned

Exact current failure from canonical diagnostics on `93358a1c...`:

`src/athena/knowledge/merge_split_policy.py:83`

mypy reports `tuple[UUID, UUID]` assigned to a variable inferred as `tuple[UUID]`; exactly one mypy error is reported across 445 checked source files. Current code still permits the one-element tuple inference before the two-element branch.

Everything else relevant is green: Specification Validator, Ruff, Core Focused, canonical pytest, Linux Storage, Windows release guards and Local Install/pypdf.

Bounded owner action: type `superseded` explicitly as `tuple[uuid.UUID, ...]` without semantic changes, run focused merge/split tests plus mypy, then require exact-SHA Core Focused and canonical success. Error worker must not parallel-edit this Spec/Core product slice.

## ERR-0061 — FIXED_PENDING_VERIFY — Harness-owned qualification blind spot

The previous Core Focused workflow could be green while canonical failed solely in mypy. Develop `1530c1e8...` now runs mypy over exact changed Core Python files, retains `.focused-evidence/mypy.txt`, and requires Ruff + mypy + focused pytest before focused success.

This is a bounded harness fix with no selector/test/Security/Storage/Recovery/release-guard relaxation. Develop canonical `34785279278` is still running; mark `FIXED` only after terminal `SUCCESS`.

## ERR-0054 — OPEN — UI/Visual Review-owned

Do not create or accept a baseline from the Error worker. Current UI handoff still does not prove 11/11 approved exact reference/render pairs. Closure requires all eleven pairs reviewed, a baseline accepted only after review, and an exact-SHA 11-Surface Visual final verdict success. No comparator, route identity, manifest truth or verdict relaxation.

## ERR-0059 — FIXED

Do not revisit unless a new exact-SHA manifest-truth regression reproduces. The bounded capture-manifest fix is integrated and canonical-green on prior Develop.

## Stale cascade

The Error worker's own canonical red on inherited 48px Send geometry remains `STALE`; current Develop preserves the authoritative 44px contract. Do not patch this stale UI baseline on `postmerge/errors`.

## Next root cause

1. Consume the Spec/Core successor for `ERR-0060`; no parallel product mutation.
2. Consume Develop canonical `34785279278`; if `SUCCESS`, close `ERR-0061` and do not revisit absent regression.
3. Keep `ERR-0054` handed to UI/Visual Review until 11/11 pairs are actually reviewed and the exact visual verdict is green.
4. Backend is canonical green; do not reopen it without a new matching failure signature.
5. Scan only for new current exact-SHA Error-owned failures. Green clusters and historical red runs are not diagnosis targets.
