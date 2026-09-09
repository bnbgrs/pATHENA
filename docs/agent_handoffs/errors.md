# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@ee7803f9b73140a3789893c25919b011d4e8d23b`.
- Error worker pre-run head: `postmerge/errors@3993a24ae8c855fdcea11ef6f0deb1e7d0fcd4e9`.
- Current workers: Spec/Core `6b833fdbe9066dbd17f8a54272b0543d7c5d5ece`; Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`; UI `a238f85a7e532afc762038610cc0ffafe04e1c00`.
- Exact Develop canonical Quality `34343282932@ee7803f9b73140a3789893c25919b011d4e8d23b = SUCCESS`; the prior bounded Develop Ruff defect is superseded/closed.
- Exact Backend canonical Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba = FAILURE`; diagnostics artifact `10100384616`.
- No queued/in-progress canonical run existed on `postmerge/errors` before the documentation mutation.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0027 CLOSED

`ERR-0027` is `FIXED` on exact Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`.

Canonical Quality `34340662717` diagnostics show `tests/unit/test_schema_contract_boundary.py ..... [86%]`, so all 5 schema-boundary tests pass on the exact worker SHA. This is sufficient assertion-level evidence rather than an aggregate-suite inference.

The relevant contract test is comprehensive: `test_schema_reexports_contract_constants()` dynamically enumerates every uppercase constant exported by `athena.storage.schema_contract` and asserts that `athena.storage.schema` exposes an equal value for every one. Therefore the Research Delta migration constants are covered by the current contract without a special-case assertion. The same exact-green module verifies `DatabaseCompatibilityError` identity/pickle compatibility, `_user_tables` identity, absence of duplicated contract implementation in the facade, and absence of a reverse import cycle.

No product mutation was needed. The previously suspected current schema-facade re-export gap is disproven/closed by exact current Backend evidence. Do not reopen `ERR-0027` absent an exact-current focused or canonical regression.

## Other active root causes

### ERR-0026 — schema Ruff I001

Exact Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba` still contains exactly one Ruff `I001` in `src/athena/storage/schema.py`, reported fixable by `--fix`. Do not commit another hand-sorted import guess; require exact Ruff 0.15.22 `--fix` output plus focused Ruff PASS.

### ERR-0028 — v41 legacy fixtures/current-version assertions

Grounded-response-receipt, backup-retention, operational-error physical-cleanup and deletion-ledger subclusters remain CLOSED from their exact passing evidence. Overall `ERR-0028` stays `IN_PROGRESS`: exact Backend diagnostics still report 19 independent failures, principally stale `0040_grounded_response_receipts` current-version assertions, legacy fixtures retaining v41-only `research_delta_boundaries`, and storage-bootstrap cascades from those fixture defects. Closed subclusters must not be reopened without exact-current regression.

### ERR-0029 — WAL exact-type harness drift

Production exact-type fail-closed guards remain authoritative. No current focused/assertion-level PASS has been consumed for remaining WAL harness cases; keep `IN_PROGRESS`.

## Integrator handoff

- Develop exact head `ee7803f9b73140a3789893c25919b011d4e8d23b` is canonical green by Quality `34343282932 = SUCCESS`.
- HOLD Backend v41 / Research-dependent integration because current Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba` remains canonical red from independent Ruff/full-Pytest failures.
- `ERR-0027`: `FIXED` on exact Backend `db0f5f440fab60b3e66c4d3843c42147a1937aba`; schema contract boundary is 5/5 PASS and dynamically verifies every uppercase contract constant re-export.
- `ERR-0026`: still one autofixable Ruff I001; require formatter-generated fix and focused Ruff PASS.
- `ERR-0028`: overall `IN_PROGRESS`; preserve all already-closed bounded fixture subclusters and address only exact-current remaining failures.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Select the highest still-active independent Backend root cause from exact diagnostics. `ERR-0026` remains a small formatter-owned blocker but must use exact Ruff 0.15.22 autofix output before mutation; `ERR-0028` remains the larger integration-impact fixture family. Do not spend another run on `ERR-0027` unless new exact-current regression evidence appears.