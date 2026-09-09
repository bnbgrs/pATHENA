# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Current shared baseline reviewed this run: `develop/pathena-next@c830b96a12d25914c52a0abc7749a6724b19cfae`.
- Worker at run start: `postmerge/spec-core@eb352369d5477c8b67fab5a76811916bfa28769b`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.
- Current Errors/Backend/UI/Integrator handoffs, Beta Exhaustive Research, capability coverage, relevant Research/Job validation code and acceptance tests were re-read before repair.
- Current Develop is one commit ahead of the prior Delta baseline and changes only Integrator evidence plus the Windows two-EXE packaging contract test; those Develop changes are preserved in this synchronized candidate.

## Bounded Core slice: explicit-source Delta Research repair

Beta Exhaustive Research requires that Sources arriving after a frozen snapshot are not silently absorbed, permits a Delta Research job for newly relevant data, defines Delta Research as processing data added since an earlier snapshot, and requires a Delta acceptance test.

The first Delta candidate `eb352369d5477c8b67fab5a76811916bfa28769b` added `athena.research.delta.enqueue_delta()` and `tests/unit/test_research_delta.py`, but canonical Quality `34356969100` failed on exact SHA for two candidate-owned reasons:

- mypy rejected the runtime `str`/`bytes` sequence guard as statically unreachable because the public argument is typed `Sequence[UUID]`;
- the fail-closed durable `research.exhaustive` payload validator had not yet admitted `mode=delta`, so the positive Delta acceptance path failed before persistence.

All other canonical lanes on that exact candidate were green: specification validator, Ruff, Linux storage regressions, Local install smoke and Windows path safety. Full pytest had exactly one failure: the new Delta positive-path acceptance test.

This repair keeps the runtime sequence/type guard while evaluating it through an `object` boundary so mypy can validate the defensive runtime check. The durable Research payload validator now explicitly admits `delta` and additionally requires a non-empty canonical `explicit_source_ids` list for Delta mode. This strengthens the fail-closed boundary rather than bypassing or weakening it.

The existing acceptance coverage remains authoritative: it proves that a Source captured after an original Research snapshot is frozen into a fresh Delta scope without silently absorbing the original Source, and that an empty explicit Source set is rejected before job persistence.

## Test / CI evidence

- Focused local execution was attempted first, but the local runner still could not resolve `github.com`; no local PASS is claimed.
- Exact failed evidence consumed first: Quality `34356969100@eb352369d5477c8b67fab5a76811916bfa28769b = FAILURE`, bounded to mypy plus the single Delta acceptance failure described above.
- This repair candidate is not Integrator-ready until its own exact-SHA canonical Quality completes successfully.
- Once canonical Quality starts on the repair candidate, no further `postmerge/spec-core` commit is permitted until that exact-SHA result is consumed.

## Closed / retained contracts

- Adaptive DirectChat 2048-context/output-reserve behavior remains closed absent new exact-current regression evidence.
- Normal/Hybrid Search Core API composition remains closed absent new exact-current regression evidence.
- Contradiction-review enqueue remains unchanged without a concrete current production bypass.
- No fake Sources, Claims, Knowledge, Evidence, Provenance or PALLAS state is introduced.

## Ownership boundaries / persistent guards

- No Backend/Storage schema, WAL, transport, recovery, security or UI styling work is duplicated.
- Current Develop's Windows two-EXE packaging contract is preserved unchanged.
- pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock/path-safety and duplicate-column/Core-startup/storage-bootstrap guards remain unchanged and binding.
- No force push, history rewrite, Skip/XFail or guard weakening.

## Readiness

`CANDIDATE_PENDING_EXACT_SHA`: bounded Delta product + acceptance-test repair is synchronized history-preservingly with current Develop. Integrator-ready requires exact-SHA Quality success and a still-compatible Develop baseline.
