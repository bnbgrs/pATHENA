# pATHENA Error Handoff

## Baseline

- Develop: `a26e2c03be10342476e406a18fbfb917a5a47ffe`; canonical Quality `34739022121 = IN_PROGRESS`.
- Workers: Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d`; Backend `7063801bcefc7153f4ef5de4b3d82669861b4208`; UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb`.
- Error worker entered at `2a777c98dd10d22cefc487e0f76d0552415efdf5`; zero workflow runs existed before the Ledger mutation and again on intermediate Error head `e76f89ff9797958c794ed37c4cf5adc63fddf553` before this handoff mutation.
- Current Develop already has Linux Storage, Local Install/pypdf and all Windows release guards `SUCCESS`; Python quality has Specification Validator, Ruff and mypy `SUCCESS` and is still in pytest.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0050`, `ERR-0051`.
- FIXED: prior closures plus `ERR-0047`.

## ITERATION-1 — ERR-0047 closed with integrated runtime evidence

`ERR-0047 = FIXED / P2`.

Develop successor `d7a5bcf6d836c47588b907d666b5541386ca0678` uses the bounded schedule-startup repair and its canonical diagnostics reach `tests/unit/test_schedule_startup.py .....`: all five integrated schedule-startup tests pass.

The remainder canonical suite reaches completion at `1 failed, 5029 passed, 17 skipped`. The sole failure is the unrelated stale workflow-contract assertion for the new Qt controller isolation command. This is sufficient real integrated runtime evidence for the repaired schedule-startup contract; do not reopen without a new current exact-SHA reproduction.

## ITERATION-2 — ERR-0050 moved to FIXED_PENDING_VERIFY

`ERR-0050 = FIXED_PENDING_VERIFY / P1`.

The native Qt root cause is now bounded to process-global PySide state left by earlier tests. The canonical harness keeps `tests/unit/test_desktop_api_controller.py` mandatory but runs its six tests in a dedicated interpreter, then runs every other canonical test exactly once with only that already-executed module ignored in the second invocation. Both PIPESTATUS results are enforced; there is no Skip/XFail, blind retry, assertion weakening or dropped test coverage.

Exact Develop `d7a5bcf6d836c47588b907d666b5541386ca0678` proves the boundary: isolated controller tests are `6 passed`; the remaining suite completes without a native crash and has exactly one ordinary assertion failure in `test_quality_workflow_contract.py`, which still expected the former one-process command.

Current Develop `a26e2c03be10342476e406a18fbfb917a5a47ffe` updates that contract test to verify the fail-closed two-interpreter structure. canonical `34739022121` is still running; close `ERR-0050` only if that exact integrated run succeeds.

## ITERATION-3 — ERR-0051 owner-fixed and integrated

`ERR-0051 = FIXED_PENDING_VERIFY / P2`.

Current Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d` is exact green:

- Core Focused `34737394852 = SUCCESS`
- canonical `34737394871 = SUCCESS`

The prior single Ruff `I001` is therefore no longer current on the owner branch. The corrected `src/athena/api/knowledge_model_disclosure.py` and `tests/unit/test_knowledge_model_disclosure.py` are integrated into Develop `a26e2c03...`, whose integrated canonical is in progress. No parallel Core mutation is warranted.

## ITERATION-4 — ERR-0049 remains the active P1 product blocker

`ERR-0049 = OPEN / P1`.

Current Backend `7063801bcefc7153f4ef5de4b3d82669861b4208` has Storage Focused `34738082478 = FAILURE` and canonical `34738082465 = FAILURE`. Canonical full pytest is `1 failed, 5030 passed, 17 skipped`; every non-pytest canonical family, Linux Storage lane, Windows release guards and Local Install/pypdf are green.

The sole full-suite failure is:

`tests/unit/test_storage_database_startup_identity.py::test_bound_preflight_rejects_invalid_complete_sidecar_rotation`

The test holds the primary DB identity stable, replaces both already-present WAL and SHM objects, proves both filesystem identities changed, then expects startup revalidation to fail closed. `SQLiteDatabase.start()` does not raise.

The current implementation admits any complete->complete transition where both sidecar `device/inode` identities changed as `complete_rotation`, then uses `inspect_database_read_only()` to validate the resulting file set. That proves the new pair is readable/compatible; it does not prove continuity with the accepted preflight pair.

The deeper contract gap is now explicit: `DatabaseFileSetIdentity` stores only presence plus filesystem object identity. Once both sidecars are replaced, this token contains no positive same-generation provenance that can distinguish a legitimate same-database sidecar lifecycle rotation from an arbitrary coherent replacement. Backend must add a positive continuity proof or an equivalently strong fail-closed mechanism; it must not merely broaden or re-label complete->complete acceptance.

Required same-SHA evidence before promotion:

1. foreign simultaneous WAL+SHM replacement raises `DatabaseStartupIdentityChangedError`;
2. legitimate process-separated/concurrent writer startup still succeeds;
3. single-sidecar replacement remains rejected;
4. partial publication/withdrawal remains rejected;
5. complete publication and complete withdrawal remain accepted where already specified;
6. Storage Focused and canonical Quality are green.

## ITERATION-5 — current cascade/release-guard classification

- No historical release-guard signature is reopened. Current Develop already has Linux Storage, Local Install/pypdf and Windows release guards green while canonical pytest runs.
- Current UI has UI Focused `34738565588 = SUCCESS`; its exact canonical `34738565572` is still in progress, so no new UI product cluster is opened.
- Current Spec/Core is owner-green; its previous Ruff blocker is not current.
- Current Backend red is deduplicated to `ERR-0049`; no additional Backend failure is evidenced by the exact canonical diagnostics.

## CI discipline

- No competing canonical run was started.
- `postmerge/errors` had zero workflow runs before both Error-branch mutations.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, recovery/storage/security weakening or guard relaxation occurred.

## Integrator handoff

- `ERR-0049 = OPEN / P1`: hold Backend Storage mutation until positive continuity evidence rejects paired foreign WAL+SHM replacement without regressing the legitimate concurrent writer case.
- `ERR-0050 = FIXED_PENDING_VERIFY / P1`: harness root cause is bounded and exact successor evidence shows the segfault gone; wait for `34739022121@a26e2c03...` integrated canonical completion.
- `ERR-0051 = FIXED_PENDING_VERIFY / P2`: owner exact-green and already integrated; wait for the same Develop canonical completion.
- `ERR-0047 = FIXED / P2`: integrated schedule-startup tests actually ran and passed 5/5 on `d7a5bcf6...`.

## NEXT_ROOT_CAUSE

1. Consume `34739022121@a26e2c03...`; on `SUCCESS`, close `ERR-0050` and `ERR-0051` and inspect the full diagnostics for any newly exposed independent error before changing priorities.
2. Consume the next Backend successor for `ERR-0049`; require both legitimate concurrent rotation and paired foreign replacement behavior to be proved on the same exact SHA.
3. If Develop remains red, classify only the exact new failing signature; do not revive historical IDs by association.
