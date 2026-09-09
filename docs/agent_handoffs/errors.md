# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@24364b858e15fd9e3b06a9ee2eaf1f580b51364c`.
- Error worker pre-run head: `postmerge/errors@f861634387527da1894c73b5edf84ccee30c3644`.
- Current workers: Spec/Core `0c9189954047306cfea947209b51e1a4d0a50aa3`; Backend `844d65a85ecb611d5060bf311c6346c810d2247e`; UI `5a168625987fe7096472d81df3261508ec6a1f56`.
- Current Develop Quality `34379757715@24364b858e15fd9e3b06a9ee2eaf1f580b51364c = FAILURE` after two attempts. Both attempts pass specification validator, Ruff and mypy and fail only full pytest in the Python 3.12 quality job. Local-install/pypdf packaging, Windows path safety and Linux storage jobs pass.
- Current Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e = FAILURE`; Ruff and pytest fail, while the independent platform/storage/install lanes pass.
- `postmerge/errors` had no canonical Quality run before mutation, so no competing run existed.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0030`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`.
- OPEN / BLOCKED: none at top level.

## Hard progress this run — ERR-0030 current Develop full-pytest regression

Status: `IN_PROGRESS`; severity `P1` because it is the highest current integration blocker.

Exact current Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c` is reproducibly red in canonical Quality `34379757715`: attempt 1 and attempt 2 both fail only `Quality — pytest` in the Python 3.12 quality job. Spec-validator, Ruff and mypy pass on both attempts; Local-install/pypdf packaging, Windows path safety and Linux storage lanes are green.

Exact previous Develop `c830b96a12d25914c52a0abc7749a6724b19cfae` was green in canonical Quality `34360516307`. The one-commit delta to the red current Develop is bounded to `src/athena/jobs/payload_validation.py`, new `src/athena/research/delta.py`, new `tests/unit/test_research_delta.py`, and `docs/agent_handoffs/integrator.md`.

This is enough to establish and prioritize a reproducible post-integration pytest cluster, but not enough to name the failing assertion. Do not infer that `test_research_delta.py` itself is failing merely because it is new: the Spec/Core candidate had exact-green Quality before integration, and the connector-visible current run metadata does not expose assertion-level diagnostics.

No Product/Develop mutation was made by this worker. The next owner action is to consume the exact failing assertion from Quality `34379757715`, run that focused test first, and then the smallest relevant Delta/Research regression set. Develop remains read-only for the error worker.

## Other active root causes

### ERR-0026 — Backend Ruff

Still `IN_PROGRESS`: exact Backend Quality `34378587885@844d65a85ecb611d5060bf311c6346c810d2247e` reports Ruff failure. Preserve the exact Ruff-0.15.22 autofix/focused-PASS closure requirement. It is P2 and currently lower priority than ERR-0030 because Develop itself is red.

### ERR-0028 — v41 fixtures/current-version

Overall `IN_PROGRESS`. `knowledge-schema-current-version` remains `FIXED_PENDING_VERIFY`: the source correction exists on exact Backend `844d65a…`, and Backend Quality has completed, but the connector-visible aggregate result does not expose assertion-level status for that individual test. Do not convert aggregate pytest failure into either PASS or FAIL for this bounded subcluster. Independent legacy `research_delta_boundaries already exists` fixtures remain separate primaries.

### ERR-0029 — WAL exact-type harness drift

Still `IN_PROGRESS`. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed this run.

### ERR-0027 — schema contract boundary

Remains `FIXED` from exact Backend 5/5 PASS evidence. Do not reopen absent exact-current regression.

## Integrator handoff

- Current Develop is not promotion/integration-green: `34379757715@24364b858e15fd9e3b06a9ee2eaf1f580b51364c` is reproducibly pytest-red across two attempts.
- Treat `ERR-0030` as the current P1 blocker and obtain assertion-level diagnostics before any fix. Do not revert or weaken Delta behavior based only on aggregate pytest failure.
- Backend remains non-ready independently because `ERR-0026`, `ERR-0028`, and `ERR-0029` are still active on its worker line.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

First obtain the exact failing test/assertion from Develop Quality `34379757715` and reproduce it focused on exact Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`. Only then choose the minimal owner/fix. Do not start a competing canonical run while an exact-SHA run is already queued/in progress, and do not reopen closed historical errors without exact-current evidence.
