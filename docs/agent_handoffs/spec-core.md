# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@f886a63ea190cb8d8df202bfd6528a6ef22df317`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `ef3e7f5cbf79184af1654e3c54d8bbd32192db79`, with parents prior Core head `82a08fa22b9cfa235b474e5bc97126c5c51fd6de` and current Develop `f886a63ea190cb8d8df202bfd6528a6ef22df317`.

## Current verified foundation

Develop already verifies normal-Hybrid Search facade/application composition, temporal contradiction composition, canonical Exhaustive Research coverage accounting, and canonical Research coverage formula identity/payload `eligible-successful-irrelevant-v1`.

## Implemented product slice — durable ResearchScope coverage composition

Product commit: `341852850c18766f88833530f9e73565c268c3d0`.
Focused acceptance test already present on synchronized Core lineage: `tests/unit/test_research_coverage_persistence.py` blob `cf887fd0278c67d5e2ca72148d8a9f30b39d0fd5`.
Target product blob changed from exact base `dde58860ae0008b8d24cb0a868fb9420faeef405` to `142c98f8ada90d5ea7266a5a8aeeb83bffe618dc`.
Versioned source patch: `docs/agent_handoffs/spec-core-research-coverage-composition.patch`.

The previous large-file mutation blocker is resolved. The complete exact `repository.py` base was read through the dedicated GitHub blob path and replaced through the SHA-bound existing-file mutation path. Commit inspection confirms the product commit changes only `src/athena/research/repository.py`; the substantive delta matches the versioned patch: canonical `CoverageAccounting` is imported, real SQL candidate/terminal-state facts remain authoritative, duplicate processed/ratio arithmetic is removed, and persisted `processed_count` / `coverage_ratio` now derive from canonical `ResearchCoverage`. Commit inspection also shows one non-semantic blank-line removal in the same file; no foreign file or contract was changed.

Retained invariants:

- failed/unavailable terminal work remains explicit but cannot inflate coverage;
- zero eligible work cannot synthesize 100% coverage;
- real SQL fact counts remain the persistence input;
- no schema, transaction, snapshot, recovery, fencing, idempotency, provider/transport, security, provenance, PALLAS or UI semantics changed.

## Verification state

The synchronized pre-product head `ef3e7f5cbf79184af1654e3c54d8bbd32192db79` started Quality `33857496096`; validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke were observed green before later head movement, while full pytest was still running. This is not product PASS evidence.

Exact product head `341852850c18766f88833530f9e73565c268c3d0` has Quality run `33858170255`, currently pending at this handoff update. No product PASS is claimed until an exact product-containing head completes canonical Quality successfully.

## Coordination

- Backend-owned Research runtime/input boundaries and deeper Storage/Recovery/System contracts remain untouched.
- UI-owned presentation/accessibility/visual files remain untouched.
- No new Core-owned Error Ledger item is asserted.
- `main` remains read-only and unchanged.

## Integrator handoff

NOT READY pending exact product-containing canonical Quality. Review bounded product commit `341852850c18766f88833530f9e73565c268c3d0` plus focused acceptance test blob `cf887fd0278c67d5e2ca72148d8a9f30b39d0fd5`; integrate only after exact verification is green.

## Next Core action

Consume the exact product/final-head Quality result. If green, mark this slice READY and immediately compose canonical `ResearchCoverage.result_payload()` into `ResearchResult` finalization so persisted result content carries formula identity and the same canonical counters without duplicate arithmetic. Preserve existing result idempotency, snapshot, fencing, problem-source visibility and provenance semantics.
