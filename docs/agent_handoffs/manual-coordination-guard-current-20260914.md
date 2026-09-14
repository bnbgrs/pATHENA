# Manual coordination-guard hardening handoff — 2026-09-14

## Exact lineage

- Integration target: `develop/pathena-next`.
- Exact base: `1530c1e8f17f53a6cbfbda7b7c53b8ee50afe2b5`.
- Base canonical Quality: `34785279278 = SUCCESS`.
- Isolated branch: `manual/coordination-guard-current-20260914`.
- Historical validated source: PR #90 / `manual/integrator-coordination-guard-hardening-20260910`.
- `main` and `bnbgrs/ATHENA` remain untouched and read-only.

## Current problem reproduced on Develop

The current `scripts/coordination_guard.py` still validates the outer JSON shape and mutation coverage but accepts candidate-diff evidence whose internal identity can be incomplete or contradictory:

1. a commit may provide an empty `paths` array;
2. a path entry may be blank or whitespace-only;
3. `candidate_sha` may differ from `base_sha` while no commits are supplied;
4. a non-empty commit sequence may declare `candidate_sha == base_sha`;
5. the final supplied commit SHA does not have to equal the declared `candidate_sha`.

Cases 3–5 are candidate-identity failures: mutation coverage can be evaluated over one supplied commit set while the artifact claims a different candidate head. A fail-closed coordination guard must reject that evidence before claim coverage is trusted.

## Bounded repair

Owned paths are exactly:

- `scripts/coordination_guard.py`
- `tests/unit/test_coordination_guard.py`
- `docs/agent_handoffs/manual-coordination-guard-current-20260914.md`

The parser now:

- requires every commit `paths` value to be a non-empty JSON array;
- requires every path to be a non-blank string;
- permits an empty commit list only when `candidate_sha == base_sha`;
- requires a non-empty commit list to advance beyond the base SHA;
- requires the final supplied commit SHA to equal `candidate_sha`.

Existing claim matching, completed-claim semantics, product/non-product classification allowlists, stale-ledger checks, and mutation-coverage behavior remain unchanged.

The code and focused regression logic are intentionally identical to the previously reviewed PR #90 blobs. They are recreated on the current green Develop base rather than merging the stale historical branch.

## Regression coverage

The existing coverage remains and the focused suite additionally proves fail-closed behavior for:

- empty commit paths;
- whitespace-only paths;
- changed candidate with no commits;
- final-commit / candidate-head mismatch;
- supplied commits that do not advance beyond the base.

Normal test fixtures derive their candidate head from the final supplied commit so valid evidence is internally self-consistent.

## Fresh collision review

Worker heads were refreshed immediately before this slice:

- Backend `postmerge/backend@e4e1244e8482ac7d78e557ded5f91252cccc0347` is tree-synchronous with Develop and has no product delta.
- Spec/Core `postmerge/spec-core@52b4e322041547e9039a0f3026f6747583605914` changes only its handoff plus Merge/Split policy and tests.
- Errors `postmerge/errors@e8247f46fd2bc685fae10d5bfbd2efceb5a19904` changes only error handoff/ledger plus visual-capture truth paths.
- UI `postmerge/ui@99dff1710ca5184138e888e2b3416a05a543afca` changes UI/Desktop/visual-evidence paths.

None touches the three paths owned here. This slice does not modify product runtime, Storage, Core, UI, Security, provider code, canonical workflows or worker handoffs.

## Verification contract

No local full-suite PASS is claimed from the connector-only execution environment. Required before integration:

1. canonical Specification Validator PASS;
2. canonical Ruff PASS;
3. canonical mypy PASS;
4. canonical full pytest PASS;
5. Linux Storage PASS;
6. Windows release-guard lane PASS;
7. Local install smoke PASS;
8. fresh Develop/worker collision review if any relevant branch advances.

Do not weaken the new identity invariants, add Skip/XFail, relax claim coverage, or widen the non-product allowlists merely to make a candidate pass.

## Bot consumption

This is an Integrator/coordination-maintenance slice. Bots should not recreate PR #90 again or mutate these three paths while this exact candidate is under verification. Any failure outside this ownership surface must be classified before scope is widened.
