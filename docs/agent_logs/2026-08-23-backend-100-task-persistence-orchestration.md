# pATHENA backend 100-task run — persistence and orchestration hardening — 2026-08-23

Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Scope: backend only. No UI/UX, Qt, desktop view, layout, theme, design, GitHub Actions, Quality Gate, `bnbgrs/ATHENA`, or other repository changes.

## Aufgaben 1–100

1. Analysed the central `DurableJobService.create` persistence boundary and identified that only `source.analyze` had pre-persistence semantic validation.
2. Analysed `JobRepository.create` and confirmed malformed canonical JSON contracts can otherwise become durable job rows before worker validation.
3. Analysed `source.process` enqueue output and pinned the current new-job contract to `source-process-v2`.
4. Analysed the `source.process` worker decoder and preserved its ability to read already-persisted legacy pipeline state while making new persistence stricter.
5. Searched for indexed `source-process-v1` creation paths and found no current new-job producer using that legacy version; legacy worker support was left untouched.
6. Analysed the `source.analyze` producer contract and its requested scope/pinned configuration fields.
7. Analysed the `source.analyze` worker-side pinned configuration checks to align pre-persistence validation with runtime checks.
8. Analysed the `backup.create` scheduler/worker contract, including exact target/schedule scope and quiet-hour configuration.
9. Analysed the `archive.replicate` worker contract, including archive target role and storage retry configuration.
10. Analysed the hierarchical `source.extract` enqueue contract produced by `SourceHierarchicalExtractionService`.
11. Analysed hierarchical extraction pinned-configuration decoding, model-signature verification, context-budget validation and inference-control drift checks.
12. Analysed `CONTROLLED_STRUCTURED_CONTRACT_VERSION` at the model-provider port so the new persistence check uses the canonical structured-output contract identity.
13. Added dependency-light `athena.jobs.payload_validation` so persistence validation does not import worker/service graphs.
14. Wired built-in payload validation into `DurableJobService.create` before local-user actor creation.
15. Normalized built-in contract failures to the existing public `InvalidJobPayloadError` service boundary.
16. Added exact required/optional scope-field validation for new `source.process` jobs.
17. Added canonical UUID validation for `source.process.source_id`.
18. Added canonical UUID validation for optional `source.process.research_work_item_id`.
19. Added exact pinned-configuration field validation for new `source.process` jobs.
20. Pinned new `source.process` persistence to `source-process-v2` while leaving legacy read support in the worker.
21. Pinned the native text parser identity for `source.process`.
22. Required non-empty canonical parser identities for PDF, DOCX and HTML source-processing adapters.
23. Pinned the source-processing chunking profile to `default`.
24. Rejected Python booleans as `source.process.chunk_batch_size` integers.
25. Pinned new source-processing batch size to the durable value `32`.
26. Pinned new source-processing embedding policy to `deferred`.
27. Added exact required/optional scope-field validation for `source.analyze`.
28. Added canonical UUID validation for `source.analyze.source_id`.
29. Added canonical UUID validation for `source.analyze.representation_id`.
30. Added canonical UUID validation for optional `source.analyze.research_work_item_id`.
31. Required a non-empty, already-trimmed durable source-analysis question.
32. Added exact pinned-configuration field validation for `source.analyze`.
33. Pinned new analysis jobs to `source-analysis-v1`.
34. Required non-empty canonical `source.analyze.model_id`.
35. Added canonical UUID validation for the analysis ModelSignature ID.
36. Added lowercase hexadecimal, exactly-32-byte SHA-256 validation for the analysis ModelSignature digest.
37. Added bool-safe minimum validation for analysis effective context limit.
38. Added bool-safe positive validation for analysis output reserve.
39. Added bool-safe non-negative validation for analysis safety margin.
40. Added bool-safe positive validation for analysis maximum hierarchy depth.
41. Added pre-persistence rejection when analysis reserve plus safety margin leaves no positive model input budget.
42. Pinned the analysis token estimator to `utf8-bytes-div3-v1`.
43. Pinned the analysis prompt identity/version to `athena.source_analysis` / `1`.
44. Added exact requested-scope validation for `backup.create`.
45. Added canonical UUID validation for backup target identity.
46. Added bool-safe non-negative validation for backup schedule-slot timestamps.
47. Added exact pinned-configuration validation for scheduled backup jobs.
48. Pinned scheduled backup jobs to `backup-scheduler-v1`.
49. Added bool-safe 0–23 UTC quiet-hour validation.
50. Added exact archive replication scope validation and pinned target role to `archive_root`.
51. Added exact archive replication configuration validation and pinned `archive-replication-v1`.
52. Added bool-safe positive storage-retry validation for archive replication.
53. Added exact hierarchical `source.extract` scope validation.
54. Added canonical UUID validation for hierarchical analysis and final-artifact identities.
55. Added exact outer pinned-configuration field validation for hierarchical extraction.
56. Pinned new hierarchical extraction jobs to `source-analysis-knowledge-extraction/3`.
57. Required non-empty canonical hierarchical extraction model identity.
58. Added canonical ModelSignature UUID plus lowercase 32-byte SHA-256 validation for hierarchical extraction.
59. Required hierarchical extraction to persist a non-empty model snapshot object.
60. Required provider context length to equal the pinned effective context limit before persistence.
61. Added bool-safe context/reserve/margin/depth scalar validation for hierarchical extraction.
62. Added pre-persistence rejection when hierarchical reserve plus margin leaves no positive input budget.
63. Pinned the hierarchical extraction token estimator to `utf8-bytes-div3-v1`.
64. Pinned hierarchical extraction prompt identity/version to the current hierarchical prompt / version `6`.
65. Pinned source-extraction, merge and pair-audit schema identities to their current durable contracts.
66. Required a non-empty persisted controlled-structured provider transport identity.
67. Pinned hierarchical reasoning mode to `off`.
68. Added finite-number validation and pinned hierarchical temperature to `0.0`.
69. Added finite-number validation and pinned hierarchical `top_p` to `0.95`.
70. Added bool-safe integer validation and pinned hierarchical `top_k` to `40`.
71. Added finite-number validation and pinned hierarchical `min_p` to `0.05`.
72. Added finite-number validation and pinned hierarchical repeat penalty to `1.1`.
73. Added exact boolean validation and pinned hierarchical `store` to `False`.
74. Pinned hierarchical structured-output contract to `athena.controlled_structured_json/1`.
75. Pinned hierarchical structured-validation and provider-instance policies to their current durable identities.
76. Added bool-safe non-negative validation for `create(next_run_at_us=...)`.
77. Added positive, bool-safe limits for active-job queries.
78. Added non-empty canonical worker-ID validation before lease acquisition.
79. Added positive, bool-safe lease duration validation before conversion to microseconds.
80. Added non-negative, bool-safe explicit clock validation for lease acquisition.
81. Added exact 32-byte lease-token validation before heartbeat.
82. Added positive, bool-safe heartbeat extension validation.
83. Added exact 32-byte lease-token validation before constructing canonical write fences.
84. Added lease-token, canonical stage-name and clock validation before checkpoint persistence.
85. Added bool-safe clock validation before startup lease recovery.
86. Added positive, bool-safe job-list limits.
87. Added bool-safe queue clock and positive queue-limit validation before eligible-job discovery.
88. Added fail-closed rejection of unregistered job types supplied as eligible-queue filters.
89. Added positive, bool-safe waiting-job query limits.
90. Added bool-safe clock validation before waking due waiting jobs.
91. Added bool-safe retry timestamp, retry-count and clock validation before retry scheduling.
92. Added lease-token and optional timestamp validation before yielding a job.
93. Added lease-token, canonical blocked-reason and clock validation before durable job failure.
94. Added lease-token and optional timestamp validation before transitioning a job to waiting.
95. Added lease-token and clock validation before job completion.
96. Added lease-token and clock validation before cancellation acknowledgement.
97. Added a broad built-in payload regression suite covering 69 malformed `source.process`, `source.analyze`, `backup.create` and `archive.replicate` contracts, valid current contracts, optional Research work-item IDs, canonical JSON persistence, and proof that invalid payloads reach neither actor creation nor repository writes.
98. Added a hierarchical extraction regression suite covering 47 malformed persisted contracts plus the valid current contract; every invalid case is also checked at `DurableJobService` to prove no actor/repository side effect occurs.
99. Added scheduler/lease scalar regression coverage for 48 malformed service calls plus valid zero-timestamp/retry boundaries, lease-second-to-microsecond conversion, generated 32-byte lease tokens and valid queue type filters.
100. Documented a remaining backend gap from the registry review: generic persistence validation is still not specialized for `source.represent`, `source.chunk`, `search.rebuild`, `embedding.rebuild`, `integrity.sweep` and `research.exhaustive`; these are the next payload-boundary targets rather than silently claiming full registry coverage.

## Änderungen

### Produktion

- `src/athena/jobs/payload_validation.py`
  - new fail-closed durable built-in payload validator;
  - specialized current new-job contracts for `source.process`, `source.analyze`, `source.extract`, `backup.create`, `archive.replicate`;
  - canonical UUID/SHA/text helpers;
  - bool-safe integer checks;
  - finite numeric controls;
  - positive context-budget checks.
- `src/athena/jobs/service.py`
  - validates built-in payloads before actor creation/repository persistence;
  - validates scheduler timestamps, limits, retries, worker IDs and lease tokens before repository calls;
  - validates eligible queue job-type filters against the registered durable job set.

### Gezielte Backend-Tests

- `tests/unit/test_job_builtin_payload_validation.py`
- `tests/unit/test_job_source_extract_payload_validation.py`
- `tests/unit/test_job_service_scalar_validation.py`

## Validierung / Ausführung

A local checkout/test execution was attempted with:

`git clone --depth 1 --branch agent/pathena https://github.com/bnbgrs/pATHENA.git ...`

The execution environment failed before checkout with:

`Could not resolve host: github.com`

Therefore, in this run:

- pytest: **NOT EXECUTED** (environment DNS blocked checkout)
- Ruff: **NOT EXECUTED**
- Mypy: **NOT EXECUTED**
- Full Gate: **NOT EXECUTED by design**
- GitHub Actions / Quality Gate triage: **NOT PERFORMED by design**

No test result is inferred or invented from the static checks.

## Commits created with connector-confirmed SHAs during the latter slices

- `423a36c925ac78fbf868623fd17edebf6dabce45` — `jobs: validate hierarchical extraction payload before persistence`
- `78805c8cee27c6d0db117dd19a9ae96e9cb84d62` — `test: fence malformed hierarchical extraction jobs before persistence`
- `4b03e6f90223bc3928e598f48796e9f88d8360c2` — `jobs: harden scheduler and lease scalar boundaries`
- `1de52902a6eec88fb730251a79688c94e38a234c` — `test: cover scheduler lease and scalar boundary validation`

Earlier slices in the same run also committed the initial payload validator, central `DurableJobService.create` integration and the broad built-in payload test suite. Their changes are present on `agent/pathena`; the final branch HEAD is recorded by the documentation commit returned for this file.

## Verbleibende Risiken / nächster Backend-Slice

1. Add specialized new-job persistence contracts for the remaining registered built-ins: `research.exhaustive`, representation/chunk processing, rebuilds and integrity sweep.
2. Compare every specialized persistence contract against both producer and worker decoder to retain restart/backward-read behavior while rejecting malformed new writes.
3. Extend service-boundary validation to any API endpoints that bypass `DurableJobService` for durable job creation or state transitions.
4. Exercise the new targeted suites in an environment with a usable repository checkout before claiming pytest/Ruff/Mypy success.
5. Continue into repository-level lease/recovery invariants after the service-boundary suite is executable.
