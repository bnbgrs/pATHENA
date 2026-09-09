# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@843466d00e67232aeac43da8c3797a5b1f0d65ef`.
- Error worker pre-run head: `postmerge/errors@cac5d91212d8583e0db85c323e18996bf52e8ea7`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `8fae7273dbf61f2ab891c6b5e003e87a8d969c9a`.
- Exact Develop Quality `34403733459@316a3733b9f1db5948255fd3469d0b3df5c1806a = SUCCESS`.
- Current Develop Quality `34409340769@843466d00e67232aeac43da8c3797a5b1f0d65ef = IN_PROGRESS`; no competing run was started.
- Current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`; diagnostics artifact `10115789607` supplied new assertion-level Ruff evidence this run.
- `postmerge/errors` had no canonical Quality run before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0026 exact Ruff root cause isolated

Status: `IN_PROGRESS`.

Exact Backend canonical Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` has one and only one Ruff finding. Diagnostics artifact `10115789607` reports `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/storage/schema.py:3:1`, followed by `Found 1 error` and `1 fixable with the --fix option`.

Exact file comparison makes the formatter cause concrete. Backend `schema.py` blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76` keeps the new `research_delta_migration` import ahead of one large grouped `schema_contract` re-export block. Current Develop `843466d00e67232aeac43da8c3797a5b1f0d65ef` already carries Ruff-normalized blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`, where schema-contract re-exports are split into Ruff's canonical import form.

This is therefore a bounded formatter-owned Backend branch drift, not a production schema/storage defect and not a current Develop blocker. Do not hand-sort imports or weaken Ruff. Backend owner should synchronize/apply pinned Ruff 0.15.22 autofix to this single import block, run focused Ruff first, and only then seek exact canonical closure.

## Other active root causes

### ERR-0028 — remaining v41 legacy fixtures

`IN_PROGRESS`, P2. Closed bounded subclusters remain closed. Exact Backend diagnostics continue to show stale v40 `last_migration_id` expectations in legacy upgrade tests plus independent `research_delta_boundaries already exists` fixture collisions. Handle one primary cluster per run and deduplicate storage-bootstrap cascades.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

## Integrator handoff

- `ERR-0026 = IN_PROGRESS`, but now precisely isolated to a single Backend formatter-owned Ruff I001 on `844d65a85ecb611d5060bf311c6346c810d2247e`; current Develop already carries formatter-clean `schema.py` blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`.
- Do not treat `ERR-0026` as a current Develop blocker. Keep Backend HOLD until its own exact Ruff/full-pytest evidence is green.
- Current Develop `843466d00e67232aeac43da8c3797a5b1f0d65ef` already has canonical Quality `34409340769` in progress; consume it before any Develop action.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First consume `34409340769@843466d00e67232aeac43da8c3797a5b1f0d65ef`. If Develop remains green, prefer exact Backend evidence produced by the owner for `ERR-0026`; absent that, continue exactly one remaining `ERR-0028` or `ERR-0029` primary cluster without duplicating active worker product changes.