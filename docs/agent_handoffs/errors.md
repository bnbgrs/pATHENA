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
- IN_PROGRESS: `ERR-0021`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0020`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0021 — shared-baseline exact full-pytest failure

Canonical Quality `34170211496` on Develop SHA `d40dc421585193db7bda039d113d7d81ccfb9c03` failed only in full pytest; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy passed.

This run materially narrowed the error scope. Develop SHA `4e18f75beeaa1c5b57bca28dcad5a062ac498051` already showed the same full-pytest-only split in Quality `34166952158`, so UI-GAP-0071 is not established as the primary cause. The signal also reproduced on Backend SHA `d6fd803cae4e444f6cdc193d49c93197b457604e` via Quality `34170446906` and on UI SHA `aa9a705bac548753be4adc0ee27a998c981dc93e` via Quality `34170876155`. These are treated as shared-baseline reproductions, not separate Backend/UI errors, unless distinct traceback evidence appears.

The canonical diagnostics artifact for `d40dc...` exists as `canonical-quality-diagnostics-d40dc421585193db7bda039d113d7d81ccfb9c03`, artifact id `10035722162`, size 10080 bytes, and was still unexpired. The available connector exposes metadata but not the zip payload, so no assertion, test path or product-vs-harness classification is fabricated.

Root-cause scope is therefore narrowed to a shared Develop/full-suite failure introduced no later than `4e18f75beeaa1c5b57bca28dcad5a062ac498051`. Exact assertion/file remains unresolved. Current Develop `e9c931f5ae00e2db70e8a42ac6110b78cf35b789` has no exact completed canonical run established and ERR-0021 remains `IN_PROGRESS`.

## Current worker evidence

- Spec/Core `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`: Quality `34173373152` in progress.
- Backend `c964506791611da78dd3959aa64c12b2614e253b`: Quality `34173582002` in progress.
- UI `352b4c72c39d5cafe866c604a050a1b93df71940`: Quality `34174030199` in progress.
- Previous Backend `d6fd803cae4e444f6cdc193d49c93197b457604e`: Quality `34170446906 = failure`, full-pytest-only after non-pytest gates passed.
- Previous UI `aa9a705bac548753be4adc0ee27a998c981dc93e`: Quality `34170876155 = failure`.

## ERR-0020 closure remains valid

ERR-0020 remains `FIXED`: error fix `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9` was byte-identically verified by Spec/Core `80915e1e8c7dff42fc998e9035df41273bdb08ca` with canonical Quality `34166094972 = success`.

## Integrator handoff

- HOLD promotion-ready claims for Develop while `ERR-0021` is unresolved and current Develop lacks exact completed canonical success.
- Do not attribute ERR-0021 to UI-GAP-0071, current Backend WAL work, or current UI Jobs work without exact traceback evidence; the same failure predates and crosses those slices.
- Consume `34173373152`, `34173582002`, and `34174030199` on the next run. A green exact successor must be compared against the failed shared baseline to identify the minimal delta before ERR-0021 is closed or staled.
- If any successor fails, consume its exact diagnostics and finalize the failing assertion/root cause rather than repeating the generic shared-baseline description.
- Do not re-open historical Windows/runtime crash classes without matching exact-current signatures.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume current Spec/Core, Backend and UI canonical completions.
2. Finalize ERR-0021 from exact pytest diagnostics or compare the first exact-green successor against the shared failed baseline to identify the clearing delta.
3. Inspect exact current Develop/runtime evidence next; do not manufacture errors.
4. Before Beta/release promotion, run the known-crash matrix on the exact candidate SHA.
