# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@f886a63ea190cb8d8df202bfd6528a6ef22df317`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `ef3e7f5cbf79184af1654e3c54d8bbd32192db79`, with parents prior Core head `82a08fa22b9cfa235b474e5bc97126c5c51fd6de` and current Develop `f886a63ea190cb8d8df202bfd6528a6ef22df317`.
- The merge retained the Core-only versioned patch `docs/agent_handoffs/spec-core-research-coverage-composition.patch` and focused acceptance test `tests/unit/test_research_coverage_persistence.py` on top of current Develop without touching `main` or foreign-worker product files.

## Current verified foundation

Develop already contains and verifies:

- normal-Hybrid Search facade/application composition;
- temporal contradiction policy and ProposalAcceptanceService composition;
- canonical Exhaustive Research coverage accounting;
- canonical Research coverage formula identity/payload `eligible-successful-irrelevant-v1`.

The current highest Core gap is durable ResearchScope/ResearchResult coverage composition: persisted counters must derive from the same canonical `athena.research.coverage.ResearchCoverage` accounting rather than duplicate arithmetic in `ResearchRepository._recompute_scope_counters()`.

## Current product slice

Versioned patch: `docs/agent_handoffs/spec-core-research-coverage-composition.patch`.
Focused acceptance test: `tests/unit/test_research_coverage_persistence.py`.
Target existing file: `src/athena/research/repository.py`.
Exact current target blob: `dde58860ae0008b8d24cb0a868fb9420faeef405`.

Required bounded mutation:

1. import canonical accounting as `CoverageAccounting`;
2. keep the existing SQL counts for candidate/successful/irrelevant/failed/unavailable/excluded facts;
3. instantiate canonical `CoverageAccounting` from those exact persisted facts;
4. persist `coverage.processed_count` and `coverage.coverage_ratio` rather than independently re-deriving them;
5. leave schema, transaction boundaries, snapshot/recovery, fencing, idempotency, provenance, provider/transport, PALLAS and UI semantics unchanged.

The dedicated GitHub `fetch_blob` path now returns the complete exact `repository.py` blob, so the former truncated-read problem is resolved. The connector also exposes complete-file replacement/create-blob primitives. No unsafe reconstruction from shortened reads is permitted.

## Verification state

ATHENA Quality Gate run `33857496096` is running on exact synchronized head `ef3e7f5cbf79184af1654e3c54d8bbd32192db79`.

Observed current-head evidence at handoff update time:

- specification validator: PASS;
- Ruff: PASS;
- mypy: PASS;
- Windows path safety: PASS;
- Linux storage regressions: PASS;
- local install smoke: PASS;
- full pytest: still running;
- therefore no canonical PASS is claimed for this head.

Because the product hunk is not yet committed, the persistence-composition slice remains NOT READY even if unrelated current-head checks complete green.

## Coordination

- Backend owns Research input/runtime boundaries and deeper Storage/Recovery/Provider/System work; Core does not alter those contracts.
- UI owns presentation/accessibility/visual state; Core does not alter UI files.
- Error owns current ERR diagnostics. No new Core-owned ERR-ID is asserted here.
- Integrator already integrated the verified formula-payload slice and explicitly expects Core to complete the durable composition instead of repeating a handoff-only blocker.

## Integrator handoff

NOT READY for durable Research coverage composition.

The focused acceptance test and exact-base product patch are versioned on Core, but `src/athena/research/repository.py` remains at blob `dde58860ae0008b8d24cb0a868fb9420faeef405` until the bounded product hunk is safely committed and exact verification is green.

## Next Core action

Apply the already-versioned `repository.py` hunk against exact blob `dde58860ae0008b8d24cb0a868fb9420faeef405` using the complete blob/create-blob replacement path. Then run the focused coverage/persistence/repository-result regressions and canonical Quality. If green, update this handoff with the exact product/test READY SHA and immediately take the next highest unclaimed P0/P1/P2 CHAT/KNOWLEDGE/RESEARCH/PALLAS composition gap.
