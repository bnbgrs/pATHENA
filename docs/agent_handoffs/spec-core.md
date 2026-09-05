# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@f630b27ddb7a40f2982f50f79d9f7d9f1322d1b1`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization commit: `9e9d15ff9b4f9b4def6d19683db76089efee11f4`, using the exact current Develop tree and parents previous worker `4df931d3e9ea5d60952c92f9c8b93ef54e3d23e3` plus Develop.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Completed Core coverage

Normal Hybrid Search facade/application composition, production contradiction acceptance, fenced Research source coverage, Scoped Project Research, Historical Backfill enqueue/durable validation, Historical Backfill candidate freeze, and its real persisted-Source inclusive-time/pinned-snapshot regression have already been verified/integrated on Develop. They are not re-opened by this handoff.

## Current gap — truthful Local plus Web Research

Primary source: `docs/beta/11_Exhaustive_Research.md`.

The Beta contract requires external facts to be captured into durable Sources before analysis and Internet access to be explicit/visible rather than implicit. `ResearchMode.LOCAL_PLUS_WEB` exists, and the existing `ExternalAccessGateway` already enforces explicit authorization and capture-before-analysis. The composition defect is downstream: `ExternalResearchService.enqueue()` currently captures authorized URLs and then calls `ResearchService.enqueue_local()`, persisting the job as `local_exhaustive` with null `internet_scope`. The durable `research.exhaustive` payload validator also rejects any Local+Web mode/scope.

## Versioned executable patch

`docs/agent_handoffs/spec-core-local-plus-web.patch` was authored against exact current blobs and committed on the worker. It contains the bounded next mutation plus acceptance tests:

- add `ResearchService.enqueue_local_plus_web()` requiring an explicit UUID authorization and at least one captured external Source;
- persist truthful `mode=local_plus_web` and a canonical non-null `internet_scope` containing the exact authorization id and captured Source ids;
- require `internet_scope.captured_source_ids` to exactly match the persisted explicit Source ids at the durable job-validation boundary;
- change `ExternalResearchService` only after capture has completed to delegate to the truthful Local+Web enqueue path;
- preserve null Internet scope for all non-Web Research modes;
- add real `AthenaApplication`/SQLite durable-persistence acceptance plus fail-before-persistence cases.

The patch deliberately does **not** broaden candidate-freeze behavior yet. Local+Web candidate union/provenance verification remains a separate fail-closed slice and must be implemented with real `external_source_captures` linkage before the overall Local+Web runtime can be marked READY.

## Verification state

The versioned patch itself is committed but has not yet been applied to product/test files, so no focused-test or canonical-Quality PASS is claimed for Local+Web. Under the Core progress rule, the next run must apply this exact patch (or resolve a concrete mismatch if Develop has moved), commit product/tests, run the focused acceptance and canonical Quality, and must not merely re-analyze the same gap.

## Collision avoidance

- Backend storage/disk-pressure work is disjoint.
- UI presentation/navigation work is disjoint.
- ERR-0014 Qt desktop capture failure is unrelated to this Research Core slice.
- No Protected/Archive scope expansion is included.
- No synthetic Sources, Claims, Evidence, provenance, or PALLAS data is introduced.

## Integrator handoff

No new product READY SHA in this run. The current artifact is a versioned executable patch only; Integrator should not integrate it as product behavior until it has been applied and exact tests/Quality are green.

## Next Alpha/Beta gap

Apply `docs/agent_handoffs/spec-core-local-plus-web.patch` against the exact current worker base, commit the bounded product/test changes, run `tests/unit/test_research_local_plus_web.py` plus the smallest relevant Research/External regressions and canonical Quality. If green, version the exact product/test READY SHA. Then implement Local+Web candidate-freeze union semantics using only the exact captured external Sources linked by `external_source_captures` plus eligible local Sources at the pinned snapshot, excluding unrelated historical web captures and preserving all Protected/Archive fail-closed rules.
