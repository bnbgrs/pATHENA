# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@146fb7280dbfe30f2bec129aec8ee77f015ce040`.
- Error worker entered this run at `postmerge/errors@82590b517a736f3b90709ee16a85e5ac15aeb911`.
- Current workers: Spec/Core `23dc4c79f1e44cd099992eb23636b2c95014c790`; Backend `51ab9c428bfd69a6aa6fde5e8be6241de7873dca`; UI `11890ef6216ae44b9e4c222bc8d9016784792e74`.
- Develop canonical Quality `34697870543@146fb7280dbfe30f2bec129aec8ee77f015ce040 = IN_PROGRESS`; exact integrated parent `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`.
- Backend exact `51ab9c428bfd69a6aa6fde5e8be6241de7873dca`: Backend Focused `34696535725 = SUCCESS`; canonical Quality `34696535722 = SUCCESS`.
- Spec/Core exact `23dc4c79f1e44cd099992eb23636b2c95014c790`: Core Focused `34696122597 = FAILURE`; canonical Quality `34696122599 = FAILURE`.
- UI exact `11890ef6216ae44b9e4c222bc8d9016784792e74`: UI Focused `34697505423 = SUCCESS`; canonical Quality `34697505416 = IN_PROGRESS` at observation time.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0041`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- `ERR-0040 = FIXED` after exact integrated Develop canonical success.
- `ERR-0033` and `ERR-0035 = FIXED`.
- `ERR-0038` and `ERR-0039 = STALE`.
- BLOCKED: none.

## Hard progress this run — ERR-0041 root cause isolated on current exact Spec/Core SHA

### ERR-0041 — provenance explanation import-order Ruff blocker

Status: `OPEN / P1 integration blocker`.

Current exact reproducer is `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`.

Exact CI evidence:

- Core Focused Candidate `34696122597 = FAILURE`;
- canonical ATHENA Quality Gate `34696122599 = FAILURE`;
- both runs are on exact Spec/Core SHA `23dc4c79f1e44cd099992eb23636b2c95014c790`.

Canonical Quality isolates the failure to Ruff. Specification validation succeeds, mypy succeeds, full pytest succeeds with `4973 passed, 17 skipped`, Windows Path Safety succeeds, Linux Storage Regressions succeeds, and Local Install Smoke succeeds.

The canonical job log gives the exact root cause: Ruff `I001` at `src/athena/knowledge/provenance_explanation.py:3:1` reports an unsorted/unformatted import block. The standard-library imports place `import uuid` after `from dataclasses import dataclass` and `from datetime import UTC, datetime`, so Ruff requires the import block to be organized.

This is a small, bounded Spec/Core-owned formatting defect. The active specialist worker owns the exact file/slice, so Errors did not mutate product code in parallel.

### Required owner fix and verification

1. Organize only the imports in `src/athena/knowledge/provenance_explanation.py`; no behavioral changes.
2. Run focused Ruff on that file first.
3. Run the smallest relevant provenance explanation regression set.
4. Use exact-head Core Focused/canonical Quality for promotion evidence when appropriate.
5. Mark `FIXED` only from a current or superseding exact Spec/Core SHA carrying the repair and successful relevant verification.

Do not weaken Ruff, tests, quality enforcement, Storage, Recovery, Security or release guards.

## Consumed prior verification — ERR-0040

The pending integrated verification has completed: canonical Quality `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`. This is the exact Develop SHA that integrated Backend repair `359b675a37b5b59210399bee1506afddc6ccee13`. `ERR-0040` is therefore `FIXED`; reopen only with a new current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@82590b517a736f3b90709ee16a85e5ac15aeb911` had zero workflow runs before the ledger mutation.
- After ledger commit `8290d0857b5ab5e63a15bb13522e18ab3f819376`, the Error branch again had zero workflow runs before this handoff mutation.
- No canonical Quality run was started by Errors.
- The running Develop and UI canonical jobs were not duplicated or disturbed.
- No mutation was made to Develop, Backend, Spec/Core, UI, `main`, or `bnbgrs/ATHENA`.

## Integrator handoff

- Current Develop: `146fb7280dbfe30f2bec129aec8ee77f015ce040`; canonical `34697870543 = IN_PROGRESS` at observation time.
- `ERR-0041 = OPEN / P1` on Spec/Core exact `23dc4c79f1e44cd099992eb23636b2c95014c790`.
- Root cause: Ruff `I001`, unsorted/unformatted import block in `src/athena/knowledge/provenance_explanation.py:3:1`.
- Exact evidence: Core Focused `34696122597 = FAILURE`; canonical `34696122599 = FAILURE`; canonical full pytest itself is green (`4973 passed, 17 skipped`).
- Do not integrate that Spec/Core head until owner remediation has current exact-SHA evidence.
- Backend `51ab9c428bfd69a6aa6fde5e8be6241de7873dca` is focused+canonical green.
- `ERR-0040 = FIXED` by exact integrated Develop canonical `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
