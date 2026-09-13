# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`; canonical Quality `34785279278 = IN_PROGRESS`. Specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are already green; full pytest is still running.
- `postmerge/errors@db47bc9d89633034d2897367caee86b96f945fd8`; latest exact canonical `34783072166 = FAILURE` on the inherited historical 48-vs-44 Send-button geometry of this diverged worker baseline. No Error-worker run is queued/in-progress before this ledger update.
- `postmerge/spec-core@93358a1c7a310a2da4279fb51b1e99a1bde505ab`; Core Focused `34783221743 = SUCCESS`, canonical Quality `34783221804 = FAILURE` solely in mypy. Full pytest and persistent release-guard lanes are green.
- `postmerge/backend@dda2dd74c0989f7ec453e8a2b7d8122f85a9251c`; canonical Quality `34784000745 = SUCCESS`.
- `postmerge/ui@de4efa5d3814948d47d83484c4a27ac0c2daf64c`; Core Focused `34779940800 = SUCCESS`, UI Focused `34779940824 = SUCCESS`; no new matching canonical failure signature is current. Visual review remains separately fail-closed.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0060 — P2 — Spec/Core merge-split planner mypy tuple inference

Status: `OPEN`

Owner: Spec/Core. Error worker is evidence-only for this cluster and must not parallel-edit the product file while the owner branch holds the slice.

Exact reproduction: `postmerge/spec-core@93358a1c7a310a2da4279fb51b1e99a1bde505ab`, canonical Quality `34783221804 = FAILURE`.

Exact diagnostic artifact `canonical-quality-diagnostics-93358a1c7a310a2da4279fb51b1e99a1bde505ab` reports:

- `src/athena/knowledge/merge_split_policy.py:83: error: Incompatible types in assignment`
- expression type: `tuple[UUID, UUID]`
- variable type: `tuple[UUID]`
- `Found 1 error in 1 file (checked 445 source files)`.

Current code still assigns `superseded = (right,)` or `(left,)` before the two-element `(left, right)` branch, so mypy infers a one-element tuple type. Runtime semantics are not failing: canonical pytest is green, as are Ruff, Specification Validator, Linux Storage, Windows release guards and Local Install/pypdf.

Bounded owner fix:

1. Explicitly type `superseded` as a variable-length UUID tuple, e.g. `superseded: tuple[uuid.UUID, ...]`, without changing planner semantics.
2. Run the merge/split policy focused tests plus mypy.
3. Require exact-SHA Core Focused and canonical Quality success on the Spec/Core successor before marking `FIXED`.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Current state:

- `postmerge/ui@de4efa5d3814948d47d83484c4a27ac0c2daf64c` remains focused-green with no new matching technical failure signature.
- Current UI handoff remains fail-closed at `PAIRS_VERIFIED_0_OF_11` for its candidate evidence and does not establish eleven approved reference/render pairs.
- No baseline may be created or accepted by the Error worker.

Required closure: exact current render evidence for all eleven surfaces, visual review of all eleven authoritative reference/render pairs, reviewed baseline only after approval, then exact-SHA 11-Surface Visual final verdict success. Never relax comparator tolerances, route identity, capture truth or verdict enforcement.

## FIXED_PENDING_VERIFY

### ERR-0061 — P2 — Core Focused omitted mypy and could report false-green candidates

Status: `FIXED_PENDING_VERIFY`

Owner: Integrator/Harness; the bounded harness fix is already on current Develop `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`.

Current evidence:

- Spec/Core `93358a1c...` proves the qualification blind spot: Core Focused `34783221743 = SUCCESS` while canonical `34783221804 = FAILURE` solely in mypy.
- Develop commit `1530c1e8...` changes `.github/workflows/core-focused-candidate.yml` so exact changed Core Python files run mypy, stores `.focused-evidence/mypy.txt`, and requires Ruff + mypy + focused pytest in the final outcome.
- The accompanying regression test was updated; no selector, test, Security, Storage, Recovery or release guard was weakened.
- Develop canonical `34785279278` is still in progress; validator/Ruff/mypy and persistent release-guard lanes are already green.

Closure: mark `FIXED` only if exact Develop canonical `34785279278` terminates `SUCCESS`. Do not mutate Develop while that run is active.

## FIXED

### ERR-0059 — P2 — visual manifest falsely reported full capture after partial failure

Status: `FIXED`

Integrated and canonical-green on Develop `ba6bc224cc152c144d13ca21730dad6620610abe`; do not revisit unless a new exact-SHA manifest-truth regression reproduces.

Also fixed and retained: `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE / DEDUPLICATED CASCADES

### Historical Send-button 48px failure on Error worker

Status: `STALE`

The Error-worker baseline remains diverged and red on inherited 48px Send geometry. Current Develop retains the authoritative 44px contract and canonical-green history, so this does not reopen `ERR-0053` and is not an Error-worker UI patch target.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Current exact Develop has Linux Storage, Windows release guards and Local Install/pypdf green while its full canonical pytest finishes.

## Next root cause

1. `ERR-0060` remains the highest current product failure, but it is Spec/Core-owned. Consume the owner successor; do not parallel-edit its product code.
2. `ERR-0061` is harness-fixed on Develop and awaits only terminal exact canonical verification.
3. `ERR-0054` remains UI/Visual-review-owned; do not create or accept a baseline in parallel.
4. Backend is canonical green and is not a diagnosis target.
5. `ERR-0059` remains closed; do not revisit without a new exact-SHA manifest regression.
6. If no new Error-owned exact-SHA failure appears, do not manufacture work from historical red runs.
