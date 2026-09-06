# pATHENA Error Handoff

## Baseline

- Baseline: `develop/pathena-next@8b6c7a2f44104675570152a5b44fa65979493bc9`.
- Error branch history-preserving NON-FORCE sync: `2c8de3800f8ae028f7e8689a24a653a1e5e7cc56` from prior Error `f4208cedd9574e6fddcc4cf47dac2694eeab69c8` plus current Develop.
- Worker heads reviewed: Spec/Core `b8858f986ec96e5973d47f8b74d2a120149a2037`; Backend `77ce30acb409881e00f12a9ab78655b81b0cdd1e`; UI `59b2046d5e127664195f7ecf17245c45f70f00ca`; Integrator/Develop `8b6c7a2f44104675570152a5b44fa65979493bc9`.
- `spec-core.md`, `backend.md`, `ui.md`, `integrator.md`, current worker heads and canonical Quality evidence were reviewed. `main` and `bnbgrs/ATHENA` remained read-only.

## Current state

- OPEN: `ERR-0018`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0018 — third exact verification

Spec/Core correction head `b8858f986ec96e5973d47f8b74d2a120149a2037` was concretely verified with canonical Quality `34051030897`. The run completed `failure` solely because Ruff still reports `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/memory/context.py:3:1`.

Everything else is green on that exact SHA: Local install/Core-API restart PASS; Windows path safety PASS; Linux storage/API path-boundary PASS; Validator 63/63 PASS; mypy PASS; full pytest `4736 passed, 3 skipped, 2 warnings`.

This is the same `ERR-0018`, not a new error and not a Personal Memory semantic/runtime defect.

The two attempted worker fixes are both rejected by exact Quality:

1. `e8f7199f70c56a79403026926430ea56a5177bec` kept `import uuid` before `from dataclasses import dataclass` and changed the 91-character local models import to multiline; Ruff still failed.
2. `b8858f986ec96e5973d47f8b74d2a120149a2037` reversed stdlib order to `from dataclasses import dataclass` before `import uuid` and restored the local import to one line; Ruff still failed.

Ruff/isort default ordering places straight imports before from-imports, so the second attempt's stdlib reversal is not a safe canonical assumption. The next correction must be generated from the exact pinned Ruff (`ruff==0.15.22`) using `ruff check --fix` on the complete import block rather than another guessed permutation, then rerun focused Personal Memory context tests and canonical Quality.

Current Develop does not contain `src/athena/memory/context.py`. Therefore Error must not import this unintegrated Spec/Core feature onto `postmerge/errors` merely to make lint green. The correct mutation remains Spec/Core-owned; this run satisfies the hard progress rule by concretely rejecting the active worker mutation with exact diagnostics and refining the next corrective action.

## Other evidence

- Backend `postmerge/backend@77ce30acb409881e00f12a9ab78655b81b0cdd1e`, Quality `34052064954`, was still in progress at scan time; no confirmed independent primary failure was established.
- UI `postmerge/ui@59b2046d5e127664195f7ecf17245c45f70f00ca` was reviewed; no confirmed independent primary failure was established in this scan.
- Current Develop `8b6c7a2f44104675570152a5b44fa65979493bc9` has no exact completed canonical Quality verified this run and is not promotion-ready by Error criteria.

## Integrator handoff

- Reject Spec/Core `e8f7199f70c56a79403026926430ea56a5177bec` and `b8858f986ec96e5973d47f8b74d2a120149a2037` as ready.
- Have Spec/Core run the repository-pinned `ruff==0.15.22` organizer (`ruff check --fix`) on `src/athena/memory/context.py`, commit only the resulting import-block normalization, and preserve all Personal Memory semantics.
- Require exact corrected SHA: Ruff PASS, focused `tests/unit/test_personal_memory_context.py` PASS, full pytest PASS and canonical Quality SUCCESS before `ERR-0018` becomes FIXED.
- Do not weaken Ruff or import the unintegrated feature into Develop/Error as a workaround.
- Preserve Provider/Transport byte-budget/deadline/poisoning, Personal-Memory provenance/review, Windows path safety, Storage, Security and Recovery guards.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Verify the next Spec/Core descendant after `b8858f986ec96e5973d47f8b74d2a120149a2037`; close `ERR-0018` only on exact Ruff + focused + full canonical evidence.
2. Consume Backend Quality `34052064954` and latest UI Quality to completion.
3. Inspect the next exact current Develop/worker canonical or runtime signal and deduplicate against the ledger/crash matrix.
