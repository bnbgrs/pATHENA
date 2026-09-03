# pATHENA Feature Integrator Handoff

## Current branch state

- `main` (strict read-only): `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `f76911dfef6530041d62fb6c2e0ddec242d64231`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `757827e2e5b7ed08dd2367645f94ee32f3063781`; spec-core `2ad502603b78c2ae39ff9deaff2c1c9324d9ed7c`; backend `9083ca691b804962e136006745b07622bb95d84e`; ui `131e5128c8266531ae48667359e1f01bb7a3bfbc`.

## READY assessment

No worker product commit satisfies READY in this run.

### Error worker

`postmerge/errors@757827e2e5b7ed08dd2367645f94ee32f3063781` reports no new product/harness fix to integrate. Existing `ERR-0001`, `ERR-0002`, and `ERR-0003` remain closed on Develop.

### Core worker

`postmerge/spec-core@2ad502603b78c2ae39ff9deaff2c1c9324d9ed7c` is synchronized with current Develop but still contains only the versioned normal-Hybrid Search composition patch/acceptance evidence. The actual `CoreApiFacade <-> AthenaApplication` product mutation is absent and no green execution exists. NOT READY.

### Backend worker

`postmerge/backend@9083ca691b804962e136006745b07622bb95d84e` is synchronized with current Develop but still contains only the versioned ExternalAccessGateway runtime-boundary patch/evidence. The product mutation remains unapplied and unverified. NOT READY.

### UI worker

`postmerge/ui@131e5128c8266531ae48667359e1f01bb7a3bfbc` is a strict descendant of current Develop (`ahead_by=31`, `behind_by=0`). Its candidate includes UI-GAP-0004 product/test changes in `pathena_offline_comprehension_4700.py`, `pathena_startup_experience_2900.py`, and their focused tests.

Canonical Quality run `33785726577` is SHA-bound to synchronized UI commit `b76115748aed53e3502a71eef10a41b11f97f8ae`, which contains the candidate plus current Develop. Windows path safety, Linux storage regressions, local-install smoke, specification validator, and mypy are green. The Python 3.12 quality job has a confirmed Ruff failure while pytest is still running. Therefore UI-GAP-0004 is explicitly NOT READY; a running run containing a confirmed required-check failure is not integration evidence.

Independent diff review found the candidate adds `setattr(window, "_core_transport_ready", False)` to `tests/unit/test_pathena_startup_experience_2900.py`. Ruff configuration enables the `B` family, so this line is a concrete likely B010 location; exact Ruff diagnostics must still be taken from the completed workflow diagnostics before assigning a definitive root cause or fix.

## Integrated this run

No worker commit was integrated. No conflict resolution was required.

## Cross-cutting work this run

The Integrator converted the UI candidate from generic `pending verification` to a concrete quality-blocked handoff based on exact SHA-bound CI evidence:

- independently reviewed the UI worker ancestry and changed-file set against Develop;
- verified Windows path safety, Linux storage and local-install jobs are green on `b7611574...`;
- verified specification validator and mypy are green;
- identified a required Ruff failure in the Python 3.12 quality job;
- isolated the newly added constant-name `setattr(...)` test line as a likely Ruff B-family failure location without claiming the exact diagnostic before workflow completion;
- rejected UI-GAP-0004 for this integration run and handed the failure to UI + Errors for exact diagnostic/fix verification;
- changed no product code, tests, guards, security, storage, recovery, or UI behavior on Develop.

## Product / quality state

- `ERR-0001`: FIXED.
- `ERR-0002`: FIXED.
- `ERR-0003`: FIXED and integrated.
- No new ERR-ID is allocated by the Integrator; `postmerge/errors` owns canonical error allocation after exact failure diagnosis.
- UI-GAP-0001 / 0002 / 0003: technically verified and integrated.
- UI-GAP-0004: `IMPLEMENTED_PENDING_VERIFY` on UI worker, but current synchronized verification is quality-blocked by Ruff and must not be integrated.
- Normal-Hybrid `CoreApiFacade/AthenaApplication` composition: `MISSING`, Core-owned.
- ExternalAccessGateway exact runtime-policy hardening: `MISSING`, Backend-owned.
- Eleven UI reference slots: zero `MATCH`; `VISUAL_REFERENCE_PENDING` remains required where original pixels are unavailable.
- No final-Develop canonical Quality PASS is claimed unless a workflow is bound to the exact final Develop SHA.

## Handoffs / next priorities

1. `postmerge/errors`: inspect completed diagnostics from Quality run `33785726577`; allocate a new `ERR-####` only if the Ruff failure is reproducible/current-lineage and not merely an already-owned UI candidate correction. Do not reopen historical errors without evidence.
2. `postmerge/ui`: finish run `33785726577`, read the exact Ruff diagnostic, minimally correct the UI-GAP-0004 test/product slice without weakening Ruff/tests, rerun focused startup/offline tests and canonical Quality, then hand off an exact green SHA.
3. `postmerge/spec-core`: apply the versioned normal-Hybrid Search product patch, run focused API/application suites plus relevant regressions/Quality, then hand off an applied-and-verified SHA.
4. `postmerge/backend`: apply the versioned ExternalAccessGateway boundary patch, verify bool/NaN/Inf fail-before-side-effect cases plus network/security regressions, then hand off an applied-and-verified SHA.

## Next integration

First bounded applied-and-verified Core, Backend, UI, or Error product/harness slice satisfying all READY rules. UI-GAP-0004 is no longer merely waiting for verification; it is blocked on a confirmed Ruff failure in its synchronized canonical Quality run.

## Next cross-cutting gap

If no READY worker input exists on the next run, first reconcile the completed UI diagnostics/error ownership. Only then take another small unclaimed controller/service/UI glue path after confirming no worker owns the same files. Do not implement Core Search, Backend Gateway, or UI-GAP-0004 competitively while those streams actively own them.

## Rules retained

- `main` remains strictly read-only.
- No force-push, history rewrite, auto-merge or automatic promotion to main.
- Worker commits are integrated only with compatible baseline, bounded scope, real verification, no weakened tests/guards, clear ownership and no confirmed regression.
- Pending/cancelled/unexecuted runs are never PASS evidence; a required check already known to have failed is a rejection condition for the current candidate.
- Integrator avoids competing product mutations in files actively owned by Core/Backend/UI/Error workers.
