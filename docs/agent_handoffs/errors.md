# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@8c342e1b6ea07025983726ec24d48786759c28fa`.
- Error worker entered this run at `postmerge/errors@e1262766de39b06bbe43ea62b9497c3c0100f60e`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c5e750a827de4b353da9873cb38d95b46a119d60`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34452334591@8c342e1b6ea07025983726ec24d48786759c28fa` is still `IN_PROGRESS`. Local-install/pypdf, Linux storage and Windows path safety are already green, including Windows storage regressions and the new Windows Core/API restart smoke; specification validator, Ruff and mypy are green; full pytest is still running.
- Exact current Backend Quality `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60 = FAILURE`; Linux storage, Windows path safety, Local-install/pypdf, specification validator and mypy pass, while Ruff and pytest fail.
- Exact Backend diagnostics artifact `10138548635` reports Ruff `I001` plus `17 failed, 4845 passed, 3 skipped`.
- `postmerge/errors` had no canonical Quality runs before either documentation mutation in this run.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN/BLOCKED: none at top level from exact evidence consumed this run.

## Hard progress this run — ERR-0028 exact-current assertion-level decomposition

### ERR-0028 — Backend v41 harness lineage

Status: `IN_PROGRESS`, P2 worker-local; not a current proven Develop blocker.

The current Backend exact diagnostics are now consumed at assertion level instead of merely carrying historical v41 notes forward. Canonical Quality `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60`, artifact `10138548635`, reports `17 failed, 4845 passed, 3 skipped`.

One bounded primary root-cause cluster consists of **nine stale terminal current-schema assertions**. The v14 and v17-v23 knowledge-schema upgrade tests plus `test_fresh_schema_has_v32_security_tables_without_persistent_unlock_state` successfully arrive at schema version 41, where runtime metadata is `0041_research_delta_boundary`, but still assert the previous terminal migration `0040_grounded_response_receipts`. These are one harness expectation drift, not nine migration defects.

A second independent fixture-reconstruction cluster remains visible but is deliberately not worked in this run: direct `sqlite3.OperationalError: table research_delta_boundaries already exists` occurs in archive-replication v30, knowledge v28/v29/v36, protected-content v31 and protected-source v33 legacy upgrade fixtures. Two `Failed to start service 'storage-bootstrap'` failures are downstream cascades of that impossible reconstructed state and remain deduplicated rather than promoted to separate Storage defects.

This distinction matters for ownership and safety. The authoritative Develop/Error lineage remains on schema v40 for this history, while Backend alone carries the worker-only v41 migration delta. Integrator explicitly holds broad Backend Storage/Migration history. Therefore Errors does **not** apply v41-specific test changes to `postmerge/errors` merely to repair a non-authoritative worker branch.

Required Backend correction for the nine-assertion subcluster, if v41 is preserved: only terminal *post-upgrade current-schema* expectations should use the v41 terminal migration constant. Historical pre-upgrade assertions remain historical. Run the focused failing tests first, then the smallest relevant regression set. Do not weaken the production migration or make `CREATE TABLE research_delta_boundaries` idempotent to mask malformed fixtures.

### ERR-0026 — Backend Ruff/import-layout drift

Status: `IN_PROGRESS`, P2.

The same exact artifact `10138548635` reports exactly one Ruff failure: `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/storage/schema.py:3:1` on Backend `c5e750a827de4b353da9873cb38d95b46a119d60`.

New cross-lineage evidence prevents redundant mutation: `postmerge/errors` already carries `src/athena/storage/schema.py` blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`, the same Ruff-normalized source blob as the current Ruff-green Develop lineage. Backend still carries stale blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76`. Thus there is no separate Error-owned formatter fix to author; Backend must reconcile to the existing normalized lineage and produce real Ruff PASS evidence.

No `FIXED` claim is made for `ERR-0026` until an exact Backend SHA passes Ruff.

## Closed current Develop cluster

### ERR-0031 — Windows storage-bootstrap path portability

Status: `FIXED`.

Develop `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, verified the complete Windows path-safety job green including `Run Windows storage path regressions = SUCCESS`. Current Develop `8c342e1b6ea07025983726ec24d48786759c28fa` again has the complete Windows path-safety lane green, now also including the explicit Windows Core/API restart smoke, so no exact-current recurrence exists.

The bounded fix remained test-only: `_ReserveStub.ensure()` uses a platform-valid absolute reserve path. Production Storage/Recovery/path-safety invariants were not weakened.

## Other worker cluster

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending exact-current assertion-level diagnostics. Preserve production exact-type fail-closed guards.

## Integrator handoff

- Current authoritative Develop: `8c342e1b6ea07025983726ec24d48786759c28fa`; canonical Quality `34452334591` is still running. Completed lanes are green: Local-install/pypdf, Linux storage, Windows path safety including Windows Core/API restart smoke, specification validator, Ruff and mypy. Do not claim global PASS until pytest and the run finish.
- Current Backend: `c5e750a827de4b353da9873cb38d95b46a119d60`; canonical Quality `34441278497 = FAILURE`; exact diagnostics artifact `10138548635` reports one Ruff I001 plus 17 pytest failures.
- `ERR-0028 = IN_PROGRESS`: nine current exact failures are one stale terminal-v41 assertion cluster; six direct duplicate-v41-table fixture collisions are a separate reconstruction cluster; two Storage-startup failures are cascades.
- `ERR-0026 = IN_PROGRESS`: Backend alone retains stale `schema.py` blob `b5658c38...`; Error/Develop already have normalized blob `9d6d9fd4...`. Require Backend reconciliation and exact Ruff PASS rather than a redundant Error-branch source patch.
- Do not integrate broad Backend v41/WAL/Storage history merely to repair worker-local Quality.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume `34452334591@8c342e1b6ea07025983726ec24d48786759c28fa` first on the next run. If Develop finishes green and Backend has advanced, consume that new Backend exact evidence before any further work. If Backend has not advanced, do not count re-reading the same nine assertion failures as progress; the next useful error-owned action is exact decomposition of one different still-current root-cause cluster, not another repetition of this handoff.