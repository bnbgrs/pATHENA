# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@e51e805266b625c008812ae5ab79435655ff1ca5`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE sync merge: `4081e0dd0581f011ad97cea613a0e5cd089d1e44`, parents `921c6868c8813c92da200cdd68a0ba12df583e9c` and `e51e805266b625c008812ae5ab79435655ff1ca5`.
- The merge tree is current Develop plus exactly the five still-Core-owned worker deltas: `docs/agent_handoffs/spec-core.md`, `src/athena/research/coverage.py`, `src/athena/research/source_coverage_composition.py`, `tests/unit/test_research_coverage.py`, and `tests/unit/test_research_source_coverage_composition.py`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Spec anchors

Primary source: `docs/beta/11_Exhaustive_Research.md` §§35-39 and §§49-52.

- Coverage keeps explicit candidate/processed/successful/irrelevant/failed/unavailable/excluded counters.
- Coverage ratio is based on eligible units and successful/irrelevant completion; exact formula identity is durable result data.
- §37 requires source-internal coverage for multipart Sources.
- Unavailable and failed areas remain visible; no synthetic 100% coverage.

## Verified predecessor slices

Transaction-bound source-coverage composition is verified and already integrated on Develop:

- product: `03e91df28a7f23fdd23d060a6979d6b0f33a90ff`
- focused tests: `6ca37ab0e7bffd745c3cc1766be9a4c176b51158`
- exact green worker head: `a9787104649383b5a70eb61fd08362cd2d2c462b`
- canonical Quality: `33894989515 = success`
- Develop integration: `57788317d068ccbcfa22ecb4fada9ef3855d1636` + `c6d89fa6c7dad3614e63981c3b2bc7cdcce2575c`

The helper reads exact-scope Candidate/Work rows through the caller-provided SQLite connection, reuses canonical row mapping, and composes Core-owned `source_coverage` without a second connection or synthetic counters.

## Current READY slice — canonical coverage formula identity

Product commit: `c87569315cdf7732d8896692a84ca7af4ea4e7e6`.
Focused-test commit: `5a8f8184fdb15e5475b818d43e93868e48f1db83`.
Exact verified head: `921c6868c8813c92da200cdd68a0ba12df583e9c`.
Canonical Quality: `33900087353 = success`.
Status: `VERIFIED / INTEGRATOR_READY`.

The bounded fix makes canonical `ResearchCoverage.COVERAGE_FORMULA_ID` equal the already-pinned `ResearchService.COVERAGE_FORMULA_ID` value `eligible-success-or-irrelevant-v1`. Arithmetic, counters, ratios, failure visibility, schema, transaction/fence/snapshot/recovery/idempotency, provider/transport, provenance, PALLAS and UI behavior are unchanged. Focused coverage locks both the literal identity and cross-surface Service/Coverage equality.

## Repository finalization remaining gap

`ResearchRepository.finalize_result_fenced()` still does not persist the already-verified `source_coverage` payload.

The exact current repository blob is `142c98f8ada90d5ea7266a5a8aeeb83bffe618dc`. Complete authenticated blob retrieval is available and the target finalization function was re-read from the synchronized branch. The intended delta remains strictly bounded:

1. import `SOURCE_COVERAGE_RESULT_KEY` and `research_result_content_with_source_coverage_from_connection`;
2. reserve `source_coverage` together with the existing Core-owned result fields;
3. initialize result payload from `research_result_content_with_source_coverage_from_connection(semantic_content, connection, scope_id)` inside the existing fenced transaction before adding global coverage/problem/snapshot fields;
4. preserve existing-result idempotency and all transaction/fence/snapshot/recovery/provenance behavior.

Available authenticated write primitives still require complete-file replacement for this 110 KB file rather than a bounded patch. Local checkout/raw retrieval again failed DNS resolution. No unsafe reconstruction from partial/chunked reads and no foreign-file overwrite was attempted. The blocker is now narrowed to mutation transport, not file visibility or patch design.

## Ownership / collision avoidance

- Backend deep storage/runtime/recovery/system ownership remains untouched.
- UI styling/Qt paths remain untouched.
- Error handoff reports no active stable error root cause.
- No fake Source, Claim, Evidence, Provenance, Archive/Protected scope, or PALLAS data was introduced.

## Integrator handoff

READY: formula identity product `c87569315cdf7732d8896692a84ca7af4ea4e7e6` + focused tests `5a8f8184fdb15e5475b818d43e93868e48f1db83`, exact green head `921c6868c8813c92da200cdd68a0ba12df583e9c`, Quality `33900087353 = success`.

The synchronized worker continuation starts at merge `4081e0dd0581f011ad97cea613a0e5cd089d1e44`; Integrator should independently review/import the READY formula-identity slice rather than merge the worker wholesale.

## Next Alpha/Beta gap

Next run must not repeat repository-finalization analysis. First attempt the minimal `finalize_result_fenced()` source-coverage wiring through a safe non-truncating authenticated mutation route. If the connector still exposes only unsafe complete-file replacement and local DNS remains unavailable, immediately take the next disjoint evidence-backed Core P0/P1/P2 gap rather than restating this blocker. Preserve all persistence/recovery/provenance invariants and keep PALLAS strictly data-driven.
