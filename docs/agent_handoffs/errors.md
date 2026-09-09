# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba`.
- Error worker pre-run head: `postmerge/errors@28dc066f04d90b5e942fd3cdd2f710db4bc9906c`.
- Current workers: Spec/Core `6b833fdbe9066dbd17f8a54272b0543d7c5d5ece`; Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`; UI `0ba6811f939dc464f2ba78c4b8494da16f5eefab`.
- Current Develop canonical Quality `34353904087@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba = IN_PROGRESS`; no competing run was started.
- Immediate parent Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` is exact canonical green by Quality `34343282932 = SUCCESS`.
- Exact Backend canonical Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; diagnostics artifact `10100384616`.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0026 integration impact reclassified

`ERR-0026` remains `IN_PROGRESS` on exact Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`, but it no longer blocks the current Develop integration candidate.

Exact Backend Quality `34340662717` reports one autofixable Ruff `I001` in `src/athena/storage/schema.py`; Backend still carries the old red file blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76`.

New exact evidence resolves the integration ambiguity: exact-green Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` carries Ruff-formatted `schema.py` blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`. Compare `ee7803f9...` to current Develop `5e7426e2...` shows only `docs/agent_handoffs/integrator.md` and `tests/unit/test_quality_workflow_contract.py` changed. Therefore current Develop retains the exact-green formatter-clean `schema.py` and must not be held solely for Backend's stale branch-local I001.

Do not mark the Backend defect itself `FIXED` yet. Its current branch still reproduces the I001. Closure requires Backend synchronization onto the formatter-clean source or exact Ruff 0.15.22 `--fix` output plus focused Ruff PASS. The Error worker runtime has no Ruff 0.15.22 binary/cache available, so no hand-sorted substitute was committed.

## Other active root causes

### ERR-0028 — v41 legacy fixtures/current-version assertions

Grounded-response-receipt, backup-retention, operational-error physical-cleanup and deletion-ledger subclusters remain CLOSED from their exact passing evidence. Overall `ERR-0028` stays `IN_PROGRESS`: exact Backend diagnostics still report 19 independent failures, principally stale `0040_grounded_response_receipts` current-version assertions, legacy fixtures retaining v41-only `research_delta_boundaries`, and storage-bootstrap cascades from those fixture defects. Closed subclusters must not be reopened without exact-current regression.

### ERR-0029 — WAL exact-type harness drift

Production exact-type fail-closed guards remain authoritative. No current focused/assertion-level PASS has been consumed for remaining WAL harness cases; keep `IN_PROGRESS`.

### ERR-0027 — schema contract boundary

Remains `FIXED` on exact Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`: canonical diagnostics show `tests/unit/test_schema_contract_boundary.py` 5/5 PASS, including dynamic verification of every uppercase schema-contract constant re-export. Do not reopen absent exact-current regression.

## Integrator handoff

- Current Develop `5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` has canonical Quality `34353904087` already `IN_PROGRESS`; do not start a competing run or mutate Develop while it runs.
- Parent Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` is exact-green by Quality `34343282932 = SUCCESS`.
- `ERR-0026`: `IN_PROGRESS` only on the stale Backend worker; **not a current Develop integration blocker** because the exact-green Develop parent contains formatter-clean `schema.py` and the current child does not modify that file. Backend should synchronize before its next integration candidate.
- HOLD Backend v41 / Research-dependent integration for still-current independent `ERR-0028` / `ERR-0029` evidence, not for `ERR-0026` alone.
- `ERR-0027`: `FIXED`; schema contract boundary 5/5 PASS on exact Backend.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume canonical Quality `34353904087@5e7426e2fbf3f2b7008adaae1c1b5677d65e56ba` when it completes. Then select the highest still-current independent Backend root cause. Do not spend another run re-proving `ERR-0026`'s integration impact unless Backend synchronizes or an exact-current Develop regression appears.