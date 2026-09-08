# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@e9c931f5ae00e2db70e8a42ac6110b78cf35b789`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE baseline synchronization: `196360097cbb0e6b457231862b64972b4fde9629`.
- Current Spec/Core head reviewed: `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`.
- Current Backend head reviewed: `c964506791611da78dd3959aa64c12b2614e253b`.
- Current UI head reviewed: `352b4c72c39d5cafe866c604a050a1b93df71940`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0021`, `ERR-0022`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0020`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0022 — Spec/Core Ruff-only failure

Exact Spec/Core SHA `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823` failed canonical Quality `34173373152` only on Ruff. Local install, Windows path safety, Linux storage, Validator, mypy and full pytest all passed. Diagnostics artifact `canonical-quality-diagnostics-0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`, id `10037037421`, exists and is unexpired.

The exact head commit changes only `tests/unit/test_exhaustive_research_large_archive.py`, raising source-count/expected-count from 12 to 40. The immediately preceding commit `527ee5e1b23247b8babbb9c5aa86e572d8eea505` also changes that same harness and its canonical run was cancelled, so no exact-green immediate parent isolates the lint line. The connector does not expose the diagnostics zip payload; no Ruff rule is invented.

Classification: harness-owned; full pytest is green, so this signal does not establish a product defect. Hold Spec/Core `0d0fe488...` from READY. Owner should apply only the exact Ruff correction once the diagnostic is available, then rerun Ruff, focused large-archive regression and canonical Quality.

## ERR-0021 — shared-baseline exact full-pytest failure

Canonical Quality `34170211496` on Develop SHA `d40dc421585193db7bda039d113d7d81ccfb9c03` failed only in full pytest; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy passed.

This run materially narrowed the error scope. Develop SHA `4e18f75beeaa1c5b57bca28dcad5a062ac498051` already showed the same full-pytest-only split in Quality `34166952158`, so UI-GAP-0071 is not established as the primary cause. The signal also reproduced on Backend SHA `d6fd803cae4e444f6cdc193d49c93197b457604e` via Quality `34170446906` and on UI SHA `aa9a705bac548753be4adc0ee27a998c981dc93e` via Quality `34170876155`. These are treated as shared-baseline reproductions, not separate Backend/UI errors, unless distinct traceback evidence appears.

The canonical diagnostics artifact for `d40dc...` exists as `canonical-quality-diagnostics-d40dc421585193db7bda039d113d7d81ccfb9c03`, artifact id `10035722162`, size 10080 bytes, and was still unexpired. The available connector exposes metadata but not the zip payload, so no assertion, test path or product-vs-harness classification is fabricated.

Root-cause scope is narrowed to a shared Develop/full-suite failure introduced no later than `4e18f75beeaa1c5b57bca28dcad5a062ac498051`. Current Develop `e9c931f5ae00e2db70e8a42ac6110b78cf35b789` has no exact completed canonical run established and ERR-0021 remains `IN_PROGRESS`.

## Current worker evidence

- Spec/Core `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`: Quality `34173373152 = failure`; Ruff FAIL, full pytest PASS. Tracked as ERR-0022, not as ERR-0021 reproduction.
- Backend `c964506791611da78dd3959aa64c12b2614e253b`: Quality `34173582002` in progress.
- UI `352b4c72c39d5cafe866c604a050a1b93df71940`: Quality `34174030199` in progress.
- Previous Backend `d6fd803cae4e444f6cdc193d49c93197b457604e`: Quality `34170446906 = failure`, full-pytest-only after non-pytest gates passed.
- Previous UI `aa9a705bac548753be4adc0ee27a998c981dc93e`: Quality `34170876155 = failure`.

## ERR-0020 closure remains valid

ERR-0020 remains `FIXED`: error fix `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9` was byte-identically verified by Spec/Core `80915e1e8c7dff42fc998e9035df41273bdb08ca` with canonical Quality `34166094972 = success`.

## Integrator handoff

- HOLD promotion-ready claims for Develop while `ERR-0021` is unresolved and current Develop lacks exact completed canonical success.
- HOLD Spec/Core `0d0fe488...` because ERR-0022 is exact-red despite full pytest passing.
- Do not attribute ERR-0021 to UI-GAP-0071, current Backend WAL work, or current UI Jobs work without exact traceback evidence; the same failure predates and crosses those slices.
- Consume `34173582002` and `34174030199` on the next run. A green exact successor must be compared against the failed shared baseline to identify the minimal delta before ERR-0021 is closed or staled.
- For ERR-0022, consume the exact Ruff diagnostic or a minimally corrected Spec/Core successor and verify Ruff + focused large-archive + canonical Quality before closure.
- Do not re-open historical Windows/runtime crash classes without matching exact-current signatures.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume current Backend and UI canonical completions for ERR-0021.
2. Consume exact Ruff diagnostics or a corrected Spec/Core successor for ERR-0022.
3. Finalize ERR-0021 from exact pytest diagnostics or compare the first exact-green successor against the shared failed baseline to identify the clearing delta.
4. Inspect exact current Develop/runtime evidence next; do not manufacture errors.
5. Before Beta/release promotion, run the known-crash matrix on the exact candidate SHA.
