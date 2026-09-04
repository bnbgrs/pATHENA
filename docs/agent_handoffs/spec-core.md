# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@2520224ebe3143368b3e5f13c091479d5e7b8d35`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE sync merge: `29cc7bb533b17f42d906784dfabfb88877a75a83`, parents `a9787104649383b5a70eb61fd08362cd2d2c462b` and `2520224ebe3143368b3e5f13c091479d5e7b8d35`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Spec anchors

Primary source: `docs/beta/11_Exhaustive_Research.md` §§35-39 and §§49-52.

- Coverage keeps explicit candidate/processed/successful/irrelevant/failed/unavailable/excluded counters.
- Coverage ratio is based on eligible units and successful/irrelevant completion; exact formula identity is durable result data.
- §37 requires source-internal coverage for multipart Sources.
- Unavailable and failed areas remain visible; no synthetic 100% coverage.

## Verified predecessor slice

Transaction-bound source-coverage composition is verified and READY:

- product: `03e91df28a7f23fdd23d060a6979d6b0f33a90ff`
- focused tests: `6ca37ab0e7bffd745c3cc1766be9a4c176b51158`
- exact green worker head: `a9787104649383b5a70eb61fd08362cd2d2c462b`
- canonical Quality: `33894989515 = success`

The helper reads exact-scope Candidate/Work rows through the caller-provided SQLite connection, reuses canonical row mapping, and composes Core-owned `source_coverage` without a second connection or synthetic counters.

## Current product slice — canonical coverage formula identity regression

Product commit: `c87569315cdf7732d8896692a84ca7af4ea4e7e6`.
Focused-test commit: `5a8f8184fdb15e5475b818d43e93868e48f1db83`.
Status: `IMPLEMENTED / EXACT QUALITY PENDING`.

Current synchronized Develop exposed a real Beta §36 drift: `ResearchService.COVERAGE_FORMULA_ID` pins `eligible-success-or-irrelevant-v1`, while `ResearchCoverage.result_payload()` still emitted `eligible-successful-irrelevant-v1`. The bounded product fix makes canonical ResearchCoverage use the already-pinned service formula identity without changing arithmetic, counters, ratios, failure visibility, persistence schema, transaction boundaries, recovery, provenance, provider/transport, PALLAS, or UI behavior.

Focused coverage now locks the literal formula identity and asserts equality between canonical `athena.research.coverage.COVERAGE_FORMULA_ID` and the pinned `ResearchService` contract.

No PASS is claimed until an exact canonical Quality run contains `5a8f8184fdb15e5475b818d43e93868e48f1db83` (or this documentation-only successor with identical product/test blobs).

## Repository finalization remaining gap

`ResearchRepository.finalize_result_fenced()` still does not persist the already-verified `source_coverage` payload. The authenticated `fetch_blob` path now returns the complete exact repository blob `142c98f8ada90d5ea7266a5a8aeeb83bffe618dc`, so the former truncated-read blocker is resolved. The remaining mutation limitation is that available authenticated writes replace the complete large file rather than apply a bounded delta; no unsafe reconstruction or overwrite of foreign work was attempted.

The remaining intended delta is strictly bounded: import `SOURCE_COVERAGE_RESULT_KEY` plus `research_result_content_with_source_coverage_from_connection`, add `source_coverage` to the existing reserved result fields, and initialize payload from the existing fenced connection/exact scope before global coverage/problem/snapshot fields. Existing-result idempotency and all persistence/recovery/provenance invariants must remain unchanged.

## Ownership / collision avoidance

- Backend deep storage/runtime/recovery/system ownership remains untouched.
- UI styling/Qt paths remain untouched.
- No fake Source, Claim, Evidence, Provenance, Archive/Protected scope, or PALLAS data was introduced.

## Integrator handoff

READY: transaction-bound source coverage composition `03e91df28a7f23fdd23d060a6979d6b0f33a90ff` + `6ca37ab0e7bffd745c3cc1766be9a4c176b51158`, exact green head `a9787104649383b5a70eb61fd08362cd2d2c462b`, Quality `33894989515 = success`.

NOT READY: formula-identity regression fix `c87569315cdf7732d8896692a84ca7af4ea4e7e6` + `5a8f8184fdb15e5475b818d43e93868e48f1db83` until exact canonical Quality is green.

## Next Alpha/Beta gap

First consume exact Quality for the formula-identity fix; if green, hand it READY. Then apply the minimal `ResearchRepository.finalize_result_fenced()` source-coverage wiring using the complete exact blob and a safe authenticated mutation path if available. If complete-file-only mutation remains the only safe write primitive, do not repeat that blocker unchanged: select the next disjoint evidence-backed Core P0/P1/P2 gap while preserving this READY wiring contract.
