# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@0b7f428f8679db9391c00b4b9638d85550332c43`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE sync merge: `0bbec37d359b97bc106aa1c6f1ae9aaa01dd43fc`, parents `5e5461a6c0a0a2f2e522d76f48a3870ca8414635` and `0b7f428f8679db9391c00b4b9638d85550332c43`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Spec anchors

Primary source: `docs/beta/11_Exhaustive_Research.md` §§35-39 and §§49-52.

- Coverage keeps explicit candidate/processed/successful/irrelevant/failed/unavailable/excluded counters.
- Coverage ratio is based on eligible units and successful/irrelevant completion; exact formula is result data.
- §37 requires source-internal coverage for multipart Sources.
- Unavailable and failed areas must remain visible; no synthetic 100% coverage.
- ResearchResult must preserve Coverage, Failed/Unavailable Areas, and Evidence references without silently promoting the artifact to canonical Knowledge.

## Verified predecessor slice

Reserved ResearchResult source-coverage content is verified and READY:

- product: `4418162af598e7ac2e2e8ea6c843c1f41808600b`
- focused tests: `b93b3255e4ce9eed53bde34866290f3a6e414be9`
- exact green worker head: `5e5461a6c0a0a2f2e522d76f48a3870ca8414635`
- canonical Quality: `33888920061 = success`

The verified helper owns the `source_coverage` result key, rejects semantic override attempts, and derives deterministic payloads only from real `ResearchCandidateRecord` / `ResearchWorkItemRecord` identity.

## Current product slice — transaction-bound source-coverage composition

Product commit: `03e91df28a7f23fdd23d060a6979d6b0f33a90ff`.
Focused-test commit: `6ca37ab0e7bffd745c3cc1766be9a4c176b51158`.
Status: `IMPLEMENTED / EXACT QUALITY PENDING` (`33894871215`).

`src/athena/research/source_coverage_composition.py` now adds `research_result_content_with_source_coverage_from_connection()`.

Contract:

- composition reads Candidate and Work rows through the caller-provided SQLite connection, so final wiring can use the same fenced transaction as `ResearchRepository.finalize_result_fenced()`;
- Candidate rows are scope-bound through `research_candidate_sets`; Work rows are restricted by exact `scope_id`;
- row mapping reuses canonical `_candidate_from_row()` / `_work_item_from_row()` contracts rather than reconstructing domain state independently;
- source identity, terminal state, exclusion state and stable ordering remain real persisted data;
- failed/unavailable units remain visible and never coverage-positive;
- semantic/model content still cannot override the Core-owned `source_coverage` key;
- no schema, transaction, snapshot, recovery, fence, provider, transport, security, provenance, PALLAS, or UI behavior is broadened.

Focused acceptance coverage uses a real SQLite connection with two scopes and proves that only rows from the requested scope enter the resulting source-coverage payload.

## Repository finalization trace / bounded remaining gap

`ResearchRepository.finalize_result_fenced()` still reserves only `coverage`, `problem_sources`, and `snapshot_commit_seq`, then constructs `ResearchResult.content_json` inside its fenced write transaction. It does not yet insert `source_coverage`.

The previous truncated-read blocker is no longer valid: this run retrieved the complete exact repository blob `142c98f8ada90d5ea7266a5a8aeeb83bffe618dc` through the authenticated GitHub blob path and traced the exact finalization transaction. Local checkout still fails transient DNS resolution. The available authenticated `update_file` mutation is complete-file replacement only, so the 110260-byte repository file was not rewritten merely to add the final import/call/reserved-key delta. Instead this run moved the transaction-sensitive SQL and canonical row mapping into a bounded tested Core helper, reducing the eventual large-file mutation to the smallest possible wiring delta.

The remaining repository delta is now strictly bounded: import `SOURCE_COVERAGE_RESULT_KEY` plus `research_result_content_with_source_coverage_from_connection`, add the key to the existing reserved set, and initialize the payload from that helper inside the already-open fenced transaction before adding global coverage/problem/snapshot fields. No duplicate arithmetic or secondary connection is required.

## Ownership / collision avoidance

- Backend retains deep storage/runtime/recovery/system ownership; no Backend-owned contract was changed.
- UI styling and Qt paths were untouched.
- No fake Source, Claim, Evidence, Provenance, Archive/Protected scope, or PALLAS data was introduced.

## Integrator handoff

READY predecessor: reserved ResearchResult source-coverage content at `5e5461a6c0a0a2f2e522d76f48a3870ca8414635`, Quality `33888920061 = success`.

NOT READY current transaction-bound composition until exact canonical Quality `33894871215` on `6ca37ab0e7bffd745c3cc1766be9a4c176b51158` is green. Integrator should review `03e91df28a7f23fdd23d060a6979d6b0f33a90ff` + `6ca37ab0e7bffd745c3cc1766be9a4c176b51158` only after that exact verification.

## Next Alpha/Beta gap

Consume exact Quality `33894871215`. If green, hand the transaction-bound composition READY and apply the now-minimal `ResearchRepository.finalize_result_fenced()` wiring: reserve `source_coverage`, call `research_result_content_with_source_coverage_from_connection()` with the existing fenced transaction connection and exact scope, preserve global coverage/problem/snapshot composition plus existing-result idempotency, then run focused ResearchResult/repository regressions and canonical Quality. If complete-file repository mutation remains the only authenticated write primitive and cannot be safely performed, do not repeat that blocker unchanged; move to the next disjoint evidence-backed Core gap.
