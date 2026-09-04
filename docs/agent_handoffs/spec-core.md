# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@fefe26b9fdc972b5e6950cd535397eae1067d5ea`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE sync merge: `c3e67ae74c10c1b3fa33f67c41e5698c87f50287`, parents `0948f3e432f9b909cae01711a5fd6beaf4dffc8b` and `fefe26b9fdc972b5e6950cd535397eae1067d5ea`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Spec anchors

Primary source: `docs/beta/11_Exhaustive_Research.md` §§35-39 and §§49-52.

- Coverage keeps explicit candidate/processed/successful/irrelevant/failed/unavailable/excluded counters.
- Coverage ratio is based on eligible units and successful/irrelevant completion; exact formula is result data.
- §37 requires source-internal coverage for multipart Sources.
- Unavailable and failed areas must remain visible; no synthetic 100% coverage.
- ResearchResult must preserve Coverage, Failed/Unavailable Areas, and Evidence references without silently promoting the artifact to canonical Knowledge.

## Verified predecessor slice

Storage-ready per-source payload composition is verified and READY:

- product: `4c5b1364bce18f572c949f3134df7d9b61947242`
- focused tests: `27e3f3e444e9caf164f6a34c82b4dc041950be38`
- exact green worker head: `0948f3e432f9b909cae01711a5fd6beaf4dffc8b`
- canonical Quality: `33882785879 = success`

The verified helper derives deterministic source coverage only from real `ResearchCandidateRecord` / `ResearchWorkItemRecord` identity and delegates arithmetic to `SourceCoverage.result_payload()`.

## Current product slice — reserved ResearchResult source-coverage content

Product commit: `4418162af598e7ac2e2e8ea6c843c1f41808600b`.
Focused-test commit: `b93b3255e4ce9eed53bde34866290f3a6e414be9`.
Status: `IMPLEMENTED / EXACT QUALITY PENDING`.

`src/athena/research/source_coverage_composition.py` now defines the Core-owned result key `source_coverage` and `research_result_content_with_source_coverage()`.

Contract:

- semantic/model content cannot override the Core-owned `source_coverage` key;
- payloads are computed from real Candidate/Work records, not caller-supplied counters;
- source identity and formula identity are retained;
- failed/unavailable units remain visible but do not count as coverage-positive;
- semantic fields are preserved unchanged;
- no schema, transaction, snapshot, recovery, fence, provider, transport, security, provenance, PALLAS, or UI behavior is broadened.

Focused tests lock deterministic truthful payload insertion and fail-closed semantic override rejection.

## Repository finalization trace / bounded remaining gap

`ResearchRepository.finalize_result_fenced()` currently reserves only `coverage`, `problem_sources`, and `snapshot_commit_seq`, then constructs `ResearchResult.content_json` inside the fenced write transaction. It does not yet insert `source_coverage`.

The exact repository blob on the synchronized worker is `142c98f8ada90d5ea7266a5a8aeeb83bffe618dc`. The available authenticated existing-file mutation action accepts complete-file replacement only, while full `repository.py` retrieval is truncated by the connector response budget. Reconstructing this large persistence file from partial ranges would violate the Core safety rule and risk overwriting foreign work. Local checkout was also attempted this run and failed DNS resolution. Therefore this run did not perform an unsafe repository reconstruction.

This blocker is narrowed to the final wiring only: the reserved-field composition contract itself is now real code plus focused acceptance tests. The next run must use a non-truncating authenticated blob/patch path to insert the already-bounded call into `finalize_result_fenced()`, or move to another disjoint Core gap if that mutation primitive remains unavailable.

## Ownership / collision avoidance

- Backend retains deep storage/runtime/recovery/system ownership; no Backend-owned contract was changed.
- UI styling and Qt paths were untouched.
- No fake Source, Claim, Evidence, Provenance, Archive/Protected scope, or PALLAS data was introduced.

## Integrator handoff

READY predecessor: storage-ready source coverage helper at `0948f3e432f9b909cae01711a5fd6beaf4dffc8b`, Quality `33882785879 = success`.

NOT READY current slice until exact canonical Quality for the product-containing head is green. Integrator should review `4418162af598e7ac2e2e8ea6c843c1f41808600b` + `b93b3255e4ce9eed53bde34866290f3a6e414be9` only after that exact verification.

## Next Alpha/Beta gap

Consume exact Quality for the current reserved-field composition. If green, wire `research_result_content_with_source_coverage()` into `ResearchRepository.finalize_result_fenced()` using real scope Candidate/Work rows inside the existing fenced transaction, add `source_coverage` to the repository-owned reserved set, persist it in `ResearchResult.content_json`, and run the smallest ResearchResult/repository regressions plus canonical Quality. Preserve idempotent existing-result behavior, snapshot fencing, failed/unavailable visibility, provenance, and schema.
