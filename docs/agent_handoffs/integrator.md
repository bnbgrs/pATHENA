# pATHENA Feature Integrator Handoff

## Current branch state

- `main` is strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `e51e805266b625c008812ae5ab79435655ff1ca5`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `94e703f99f3363b10e96a4be32a92eda3f829ca3`; spec-core `8ed5913ffc0b1fd222bff854c138ff23e94572bb`; backend `7688f49ea351749bf227a1683fd14aba719d9bb6`; ui `98700b0c657ba8cc488d0d9698b54fd6bce18718`.

## Integrated this run — canonical Research coverage formula identity

Core READY slice independently reviewed from exact canonical-green lineage:

- product commit: `c87569315cdf7732d8896692a84ca7af4ea4e7e6`
- focused-test commit: `5a8f8184fdb15e5475b818d43e93868e48f1db83`
- exact verified head: `921c6868c8813c92da200cdd68a0ba12df583e9c`
- canonical Quality: `33900087353 = success`

Develop exactly matched the pre-slice product/test state. The carried files are byte-identical to the verified lineage:

- `src/athena/research/coverage.py` -> blob `494195de64eba27c063ee3143364d94dc92a338f`
- `tests/unit/test_research_coverage.py` -> blob `7b07839fc7084fdd194175ba32baa6ca54b38a7f`

Develop integration commits:

- product: `bb37e6eaa91ece448a5c1c0c962ecbd2f4fd75fc`
- focused test: `9b0cce1c8e694a205023d92e463b72621d99fd15`

The bounded fix aligns canonical `ResearchCoverage.COVERAGE_FORMULA_ID` with the already-pinned `ResearchService.COVERAGE_FORMULA_ID` value `eligible-success-or-irrelevant-v1`. Coverage arithmetic, counters, failure/unavailable visibility, zero-eligible behavior, persistence schema, transaction/fence/snapshot/recovery/idempotency, provider/transport, provenance, PALLAS and UI semantics are unchanged. The focused test explicitly locks literal identity and cross-surface equality.

## Validation state

- Canonical Core Quality `33900087353` completed `success` on exact head `921c6868c8813c92da200cdd68a0ba12df583e9c`.
- Integrated product/test blobs are byte-identical to that verified lineage.
- No exact current-Develop global Quality PASS is claimed.
- Error worker has allocated `ERR-0009` against Backend head `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1`: canonical Quality `33900689788` failed only two stale `readline_sizes` expectations after the product correctly hardened reads to `remaining + 1`. This is not evidence to revert the product guard.
- Backend Storage Health and cumulative local-HTTP response-size slices remain READY alternatives; the newer remaining-budget hardening is not READY until corrected exact Quality is green.
- UI-GAP-0014 remains READY. Newer UI candidates require exact completed canonical evidence before integration.
- `ERR-0001` through `ERR-0008` remain fixed.
- Original eleven visual references remain unavailable; zero pixel-level `MATCH` claims are permitted.

## Next integration order

1. Prefer minimal fenced `ResearchRepository.finalize_result_fenced()` source-coverage wiring only after exact green product-containing evidence and collision review.
2. Otherwise independently consume exactly one READY Backend/UI bounded slice against current Develop.
3. Do not consume the Backend remaining-budget lineage while `ERR-0009` remains unresolved.
4. Require exact-head evidence before any global-green Develop claim.

## Rules retained

- `main` remains read-only and unchanged.
- No force-push, history rewrite, auto-merge or automatic promotion to main.
- Pending/cancelled/action-required/in-progress/failed Quality is never PASS evidence.
- No weakened tests/guards or fabricated runtime success paths.
