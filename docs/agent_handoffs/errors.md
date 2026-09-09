# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@ee7803f9b73140a3789893c25919b011d4e8d23b`.
- Error worker pre-run head: `postmerge/errors@ebccfe6987f9f3a6f5ea2a9f56a0890227454ae1`.
- Current workers: Spec/Core `6b833fdbe9066dbd17f8a54272b0543d7c5d5ece`; Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`; UI `21a5a1adb57023d57feae5c13ca247cba5e5cba4`.
- Exact Develop canonical Quality `34337745698@2a90e71bc2c604cd745766a608481fc14106ec07 = FAILURE`, bounded to Ruff `I001` in `tests/unit/test_quality_workflow_contract.py`; Mypy, full Pytest, Windows path safety, Linux storage, Local install smoke and specification validator passed.
- Current Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` contains the bounded Integrator Ruff correction and already has canonical Quality `34343282932` queued; no competing canonical run was started.
- Exact Backend canonical Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; diagnostics artifact `10100384616`.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 deletion-ledger subcluster CLOSED

Backend exact head `db0f5f440fab60b3e66c4d3843c42147a1937aba` completed canonical Quality `34340662717 = FAILURE`. Windows path safety, Local install smoke, Linux storage regressions, specification validator and mypy passed; Ruff and full Pytest remained red. Canonical diagnostics end `19 failed, 4840 passed, 3 skipped`.

Assertion-level evidence resolves the bounded deletion-ledger v41 fixture repair: canonical `pytest.txt` contains all three test families as fully green — `tests/unit/test_deletion_ledger.py ..... [15%]`, `tests/unit/test_deletion_ledger_boundaries.py ...................... [15%]`, and `tests/unit/test_deletion_ledger_targets.py ......... [15%]`. That is 36/36 tests passing on exact SHA `db0f5f440fab60b3e66c4d3843c42147a1937aba`.

The candidate commit is explicitly a harness repair for a v41 legacy fixture. No production schema, Storage, WAL, Recovery, Security or release guard is weakened. Therefore the deletion-ledger subcluster is `FIXED`/CLOSED. `ERR-0028` overall remains `IN_PROGRESS`: the same exact suite still reports independent v41 fixture/current-version failures such as `research_delta_boundaries already exists`, stale `0040_grounded_response_receipts` expectations, and resulting storage-bootstrap cascades in other test families.

Do not reopen grounded-response-receipt, backup-retention, operational-error physical-cleanup, or deletion-ledger subclusters without exact-current regression evidence.

## Other active root causes

### ERR-0026 — schema Ruff I001

Exact Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba` still contains exactly one Ruff `I001` in `src/athena/storage/schema.py`, reported fixable by `--fix`. Do not commit another hand-sorted import guess; require exact Ruff 0.15.22 `--fix` output plus focused Ruff PASS.

### ERR-0029 — WAL exact-type harness drift

Production exact-type fail-closed guards remain authoritative. No current focused/assertion-level PASS has been consumed for remaining WAL harness cases; keep `IN_PROGRESS`.

### ERR-0027 — v41 schema-facade re-export

Current Backend lineage visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration.
- Exact Backend head: `db0f5f440fab60b3e66c4d3843c42147a1937aba`; canonical Quality `34340662717 = FAILURE`; diagnostics artifact `10100384616`.
- `ERR-0028` deletion-ledger subcluster: `FIXED`/CLOSED on exact `db0f5f440fab60b3e66c4d3843c42147a1937aba`, with 36/36 tests passing across the three deletion-ledger files. Overall `ERR-0028` remains `IN_PROGRESS` for other independent v41 fixture/current-version failures.
- `ERR-0026`: still one autofixable Ruff I001; require formatter-generated fix and focused Ruff PASS.
- `ERR-0027`: require focused schema-contract verification before closure.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- Develop `2a90e71bc2c604cd745766a608481fc14106ec07` failed only its bounded Quality-workflow Ruff formatting check; current Develop `ee7803f9b73140a3789893c25919b011d4e8d23b` carries the narrow correction and has canonical Quality `34343282932` queued. Do not supersede or infer its result.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume completed exact-current Develop Quality `34343282932` when available. For Backend error work, select the highest still-active independent root cause from exact diagnostics; do not spend another run on the now-closed deletion-ledger subcluster. `ERR-0026` requires exact Ruff 0.15.22 autofix output before mutation; remaining `ERR-0028` fixture failures require bounded assertion-level evidence before repair/closure.