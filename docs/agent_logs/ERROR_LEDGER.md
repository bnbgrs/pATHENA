# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`; canonical Quality `34785279278 = SUCCESS`.
- `postmerge/errors@ac049c2bd02c1ed0f78e299df2fd1e56c77c9770` before this ledger update; exact canonical `34785825895 = FAILURE` only on the inherited historical 48-vs-44 Send-button geometry of this diverged worker baseline. No Error-worker run is queued/in-progress before this mutation.
- `postmerge/spec-core@36452888894de49fdcd9b1968d1eaf83bc4412b0`; canonical Quality `34786426851 = SUCCESS`; Core Focused `34786426823 = FAILURE` in the new mypy-enforced focused contract.
- `postmerge/backend@e4e1244e8482ac7d78e557ded5f91252cccc0347`; canonical Quality `34786818234 = SUCCESS`.
- `postmerge/ui@de4efa5d3814948d47d83484c4a27ac0c2daf64c`; Core Focused `34779940800 = SUCCESS`, UI Focused `34779940824 = SUCCESS`, canonical Quality `34779940794 = SUCCESS`. Visual review remains separately fail-closed.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0062 — P2 — Core Merge/Split negative-runtime tests violate focused mypy contract

Status: `OPEN`

Owner: Spec/Core. Error worker is evidence-only for this cluster and must not parallel-edit the owner test slice while Spec/Core holds it.

Exact reproduction: `postmerge/spec-core@36452888894de49fdcd9b1968d1eaf83bc4412b0`, Core Focused `34786426823 = FAILURE`; exact canonical Quality on the same SHA is `34786426851 = SUCCESS`.

Focused diagnostic artifact `core-focused-diagnostics-36452888894de49fdcd9b1968d1eaf83bc4412b0` reports four mypy errors in `tests/unit/test_knowledge_merge_split_policy.py` while Ruff and the focused pytest slice pass (`9 passed`):

- line 113: unused `# type: ignore[arg-type]` on the `plan_knowledge_merge(` call line;
- line 114: `left_entity_id="not-a-uuid"` has incompatible type `str`; expected `UUID`;
- line 120: unused `# type: ignore[arg-type]` on the `plan_knowledge_split(` call line;
- line 122: `result_entity_ids=[...]` has incompatible type `list[UUID]`; expected `tuple[UUID, ...]`.

The tests intentionally exercise fail-closed runtime validation with statically invalid values. The existing call-level ignores do not cover argument diagnostics under current mypy and are themselves rejected as unused.

Bounded owner fix:

1. Keep both negative runtime assertions unchanged.
2. Move/narrow `# type: ignore[arg-type]` to the exact invalid argument expressions (`left_entity_id=...` and `result_entity_ids=...`) or use an equally narrow typed cast/fixture that preserves the intentionally invalid runtime values.
3. Do not disable mypy, remove the negative tests, broaden ignores, weaken signatures, or alter Merge/Split runtime validation.
4. Require exact-SHA Core Focused success and retain canonical Quality success before marking `FIXED`.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Current state:

- `postmerge/ui@de4efa5d3814948d47d83484c4a27ac0c2daf64c` remains Core-Focused, UI-Focused and canonical-green.
- Current UI handoff still records `PAIRS_VERIFIED_0_OF_11` for its exact-candidate visual evidence; eleven approved reference/render pairs are not established.
- No baseline may be created or accepted by the Error worker.

Required closure: exact current render evidence for all eleven surfaces, visual review of all eleven authoritative reference/render pairs, reviewed baseline only after approval, then exact-SHA 11-Surface Visual final verdict success. Never relax comparator tolerances, route identity, capture truth or verdict enforcement.

## FIXED

### ERR-0060 — P2 — Spec/Core merge-split planner mypy tuple inference

Status: `FIXED`

Spec/Core successor `36452888894de49fdcd9b1968d1eaf83bc4412b0` contains the bounded tuple-typing repair and exact canonical Quality `34786426851 = SUCCESS`. The prior planner mypy failure is not current. The remaining red Core Focused run is a distinct test-typing cluster (`ERR-0062`), not a recurrence of `ERR-0060`.

### ERR-0061 — P2 — Core Focused omitted mypy and could report false-green candidates

Status: `FIXED`

Develop `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5` is exact canonical-green (`34785279278 = SUCCESS`). More importantly, Spec/Core run `34786426823` on current SHA executes the new `Mypy changed Core Python files` step and fails closed in final enforcement when mypy evidence is not successful. The qualification blind spot is therefore closed without selector/test/Security/Storage/Recovery/release-guard relaxation.

### ERR-0059 — P2 — visual manifest falsely reported full capture after partial failure

Status: `FIXED`

Integrated and canonical-green on Develop; do not revisit unless a new exact-SHA manifest-truth regression reproduces.

Also fixed and retained: `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE / DEDUPLICATED CASCADES

### Historical Send-button 48px failure on Error worker

Status: `STALE`

The Error-worker baseline remains diverged and red on inherited 48px Send geometry. Current Develop retains the authoritative 44px contract and canonical-green history, so this does not reopen `ERR-0053` and is not an Error-worker UI patch target.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Current Develop, Backend and UI exact canonical runs are green.

## Next root cause

1. `ERR-0062` is the highest current technical failure but is Spec/Core-owned; consume the owner successor and do not parallel-edit its tests.
2. `ERR-0054` remains UI/Visual-review-owned; do not create or accept a baseline in parallel.
3. Backend, Develop and UI canonical-green clusters are not diagnosis targets without a new exact-SHA matching failure.
4. `ERR-0059`, `ERR-0060` and `ERR-0061` are closed; do not revisit absent a new exact-SHA regression.
5. If no new Error-owned exact-SHA failure appears, do not manufacture work from historical red runs.