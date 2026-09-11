# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@1b83466490291fe07dd3d99dd476d0cb6290d307`.
- Error worker entered this run at `postmerge/errors@f493a50e999fcea5811e86b22338b1fcaff137da`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `ac3d3c851186b8caa152d4a22815bd1390998e55`.
- Latest exact current Develop canonical Quality: `34548505498@1b83466490291fe07dd3d99dd476d0cb6290d307 = IN_PROGRESS`; no final PASS/FAIL is inferred while it is running.
- Last completed Develop canonical Quality: `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.
- That completed exact-SHA run closes `ERR-0036`: the bounded typography-contract repair on `7a6b9ee5...` passed the full canonical gate, including full pytest and the Windows/Linux/local-install lanes.
- `postmerge/errors@f493a50e999fcea5811e86b22338b1fcaff137da` had zero canonical Quality runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0036 — stale UI typography assertion after intentional hierarchy promotion

- Severity: P1 while it blocked canonical Develop.
- Status: `FIXED`.
- Exact reproduction: canonical Quality `34539454111@4634bdf28c98bc114e0369701122818d474f99d9 = FAILURE`; only `Python 3.12 quality -> Quality — pytest` failed. Diagnostics: `1 failed, 4830 passed, 3 skipped`; failing test `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales` asserted the pre-hierarchy tuple `(14, 11, 34)` while the integrated product/design-token contract is `(15, 12, 42)`.
- Root cause: duplicate test-contract drift after the intentional UI typography hierarchy promotion, not a Backend/Storage/Recovery regression and not a reason to revert the product hierarchy.
- Bounded repair: Develop `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c` changed only the stale exact tuple in `tests/unit/test_pathena_design_system.py` plus Integrator documentation. No assertion was removed or generalized; no Skip/XFail and no product/runtime/Security/Storage/Recovery code changes.
- Closure evidence: canonical Quality `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.
- Reopen only if this same typography-contract signature is reproduced on a then-current exact SHA.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Current source evidence remains applicable: `SQLiteDatabase.start()` performs read-only preflight against the configured path and later independently opens the writable SQLite connection by pathname, without carrying an identity token/handle/descriptor from preflight into writer establishment.
- `src/athena/storage/recovery.py` preflight returns path/existence/application/schema/WAL/SHM facts but no filesystem identity capable of fencing the later writer open. A pathname replacement between preflight and writer establishment therefore remains an identity-continuity gap.
- Distinct from `ERR-0033`: ERR-0033 concerns EmergencyReserve directory identity across create/release; ERR-0035 concerns the primary SQLite database object between startup preflight and live writer open.
- Backend marks the same root cause BE-052 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED`; Errors makes no parallel product mutation.
- Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, WAL/SHM checks and fail-closed Recovery/Storage semantics. A second pathname-only preflight is insufficient.
- Closure requires a bounded Backend candidate plus focused cross-platform identity-swap regression evidence, followed by exact-SHA canonical evidence when integration/closure requires it.

## ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

- Severity: P1 when reproduced on canonical Develop.
- Status: `FIXED`.
- Exact failing reproduction: canonical Quality `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = FAILURE`, with Windows path safety failing at `Run Windows storage path regressions`; Linux storage, Local install and full Python quality were otherwise green.
- Root cause: the CI-only Develop delta added POSIX-specific durable-FS contracts wholesale to `windows-latest`.
- Bounded correction: Develop `7fa2108d820cfc5b48a9f92d42ffa61697b74818` runs Windows-applicable durable filesystem regressions with `tests/unit/test_durable_fs.py -k "not test_posix"` and leaves POSIX parent-identity coverage in Linux. No Skip/XFail, assertion weakening or product behavior change.
- Closure evidence: canonical Quality `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`.
- Preserve HANDLE-bound rename, reparse/symlink rejection, write-through durability, directory identity and Storage/Recovery fail-closed semantics.

## ERR-0033 — Windows emergency-reserve directory-identity binding gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Current source verification remains applicable: POSIX reserve creation/release binds mutation to an opened parent directory FD; the non-POSIX branch still relies on pathname-based create/stat/unlink/fsync sequencing and does not carry reserve-directory identity as a bound handle across Windows mutation/release.
- Backend marks BE-046 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED` and has no tested bounded product candidate in the current handoff.
- Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics. Do not substitute weaker pathname-only checks.
- Closure requires a bounded Backend candidate plus focused native-Windows adversarial directory-swap evidence over create/release, then exact-SHA canonical evidence as appropriate.

## ERR-0032 — schema-reinitialization harness row-shape mismatch

- Severity: P1 when reproduced on Develop.
- Status: `FIXED`.
- First exact reproduction: canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821 = FAILURE`; `initialize_schema()` reached schema verification with tuple rows while named-row access was required.
- Final bounded correction: Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` aligned the test connection row shape and the two schema-version assertions without weakening the invariant.
- Closure evidence: canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`.

## ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failing Develop reproduction: canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` failed Windows storage regressions while Python quality, Linux storage and Local-install/pypdf passed.
- Root cause: `_ReserveStub.ensure()` returned drive-less `Path("/tmp/bootstrap-emergency.reserve")`, correctly rejected by the Windows absolute-path invariant.
- Bounded correction: `Path.cwd() / "bootstrap-emergency.reserve"`, test-only.
- Develop verification: `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, Windows path-safety success.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715`, had one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`.
- Root cause: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from its supported-mode allowlist.
- Integrator applied the bounded one-line fix to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`; Quality `34391596966 = SUCCESS`.

## ERR-0026 — Backend quality drift

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical worker reproduction carried Ruff `I001` at `src/athena/storage/schema.py:3:1`; current Backend exact SHA does not reproduce it.
- Reopen only if reproduced on a then-current exact Backend or Develop SHA.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical worker evidence covered terminal-current-schema assertions, duplicate-v41-table fixture collisions and downstream Storage-startup cascades on worker-only schema history.
- Never change production v40→v41 migration to `IF NOT EXISTS`, swallow `OperationalError`, or weaken Storage/Recovery fail-closed behavior.
- Reopen only on a new exact-current reproduction.

## ERR-0029 — WAL harness collaborators incompatible with exact-type runtime guards

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical worker evidence is not authoritative for the current worker head.
- Production exact-type fail-closed guards remain authoritative and must not be weakened. Reopen only after exact-current reproduction.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Closure evidence: canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
