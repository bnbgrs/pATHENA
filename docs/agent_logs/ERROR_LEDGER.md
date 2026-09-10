# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@7fa2108d820cfc5b48a9f92d42ffa61697b74818`.
- Error worker entered this run at `postmerge/errors@aa603d87200b937efce37fcabfa1195a338b78a5`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `baae5dd42195eea1e2a7320d1be813431a3beecf`; UI `2ede7add4d70ee9f11ef2e05103504e9a1838a2a`.
- Exact current Develop canonical Quality: `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = IN_PROGRESS`. Windows path safety is already `SUCCESS`, including `Run Windows storage path regressions` and the dedicated `Run Windows durable filesystem regressions`; Linux storage regressions and Local install smoke are `SUCCESS`; Python spec-validator/Ruff/mypy are green while full pytest is still running.
- Previous exact Develop canonical Quality: `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = FAILURE`, isolated to the Windows storage step after POSIX-only durable-fs contracts were added wholesale to the Windows command.
- Current Develop changes no production Storage/Recovery/Security code and no test assertion. It restores the prior Windows-applicable storage set, runs `tests/unit/test_durable_fs.py -k "not test_posix"` in a dedicated native-Windows step, and leaves the entirely POSIX-gated parent-identity module to Linux coverage.
- `postmerge/errors@aa603d87200b937efce37fcabfa1195a338b78a5` had zero canonical Quality runs immediately before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0034`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

- Severity: P1 when reproduced on canonical Develop.
- Status: `FIXED_PENDING_VERIFY`.
- Exact failing reproduction: canonical Quality `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = FAILURE`, with Windows path safety failing at `Run Windows storage path regressions`; Linux storage, Local install and full Python quality were otherwise green.
- Root cause: the CI-only Develop delta added `tests/unit/test_durable_fs.py` and `tests/unit/test_durable_fs_parent_identity.py` wholesale to `windows-latest`. `test_durable_fs.py` contains explicit `test_posix_*` contracts that force POSIX-only `dir_fd` / directory-fsync behavior, while `test_durable_fs_parent_identity.py` skips every test unless `os.name == "posix"`. The failing lane therefore mixed POSIX-specific contracts into native Windows coverage; no production regression was required to explain the failure.
- Bounded correction: Develop `7fa2108d820cfc5b48a9f92d42ffa61697b74818` restores the prior Windows-applicable storage command, adds a dedicated `Run Windows durable filesystem regressions` step executing `tests/unit/test_durable_fs.py -k "not test_posix"`, and leaves the POSIX parent-identity module in Linux storage coverage. No Skip/XFail was added; no test assertion or product behavior changed.
- Focused exact-SHA verification: in canonical Quality `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818`, Windows path safety completed `SUCCESS`; both `Run Windows storage path regressions` and `Run Windows durable filesystem regressions` completed `SUCCESS`. Linux storage and Local install are also `SUCCESS`; spec-validator, Ruff and mypy are green.
- Closure is pending only the still-running full pytest / final canonical conclusion. If `34522965434` completes `SUCCESS`, promote to `FIXED`. If a different failure appears, open a separate root-cause cluster rather than reusing ERR-0034 unless the same platform-selection signature recurs.
- Preserve HANDLE-bound rename, reparse/symlink rejection, write-through durability, directory identity and Storage/Recovery fail-closed semantics.

## ERR-0033 — Windows emergency-reserve directory-identity binding gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current direct source evidence remains applicable on current Develop because the latest commits are CI/Handoff-only and do not change `src/athena/storage/emergency_reserve.py`. POSIX reserve creation/release binds to an opened reserve-directory FD; the non-POSIX branch still performs create/validation/release through pathname-driven operations, so reserve-directory identity is not carried as a bound handle across the Windows mutation/release operation.
- Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics. Do not replace the requirement with weaker pathname-only checks.
- Closure requires a bounded Backend candidate plus focused native-Windows regression evidence proving reserve-directory identity remains bound across create/release mutation, including an adversarial directory-swap boundary; then consume exact-SHA canonical evidence as appropriate.

## ERR-0032 — schema-reinitialization harness row-shape mismatch

- Severity: P1 when reproduced on Develop.
- Status: `FIXED`.
- First exact reproduction: canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821 = FAILURE`. `initialize_schema()` reached schema verification with tuple rows from the raw test connection, causing `TypeError: tuple indices must be integers or slices, not str` where named-row access is required.
- First bounded correction: Develop `4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3` added `connection.row_factory = sqlite3.Row`. Canonical Quality `34463015234` then exposed the remaining test-only shape mismatch: the two `PRAGMA user_version` assertions still compared `sqlite3.Row` directly with `(SCHEMA_VERSION,)`.
- Final bounded correction: Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` changed only those two existing assertions to scalar comparison through `[0]`; both `initialize_schema()` calls and the same schema-version invariant remained intact.
- Closure evidence: canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`, including full pytest and Windows path safety/storage regressions.
- No production schema, migration, Storage, Recovery, Runtime or Security behavior changed. Do not reopen absent a new exact-current reproduction.

## ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failing Develop reproduction: canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` failed Windows storage regressions while Python quality, Linux storage and Local-install/pypdf passed.
- Root cause: `_ReserveStub.ensure()` in `tests/unit/test_storage_bootstrap.py` returned `EmergencyReserveStatus(path=Path("/tmp/bootstrap-emergency.reserve"), ...)`; on Windows that path is drive-less and correctly fails the production absolute-path invariant.
- Bounded correction: `Path.cwd() / "bootstrap-emergency.reserve"`, test-only; no assertion or production Storage/Recovery semantics changed.
- Develop verification: `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, complete Windows path-safety success including Windows storage regressions.
- Do not reopen absent a new exact-current reproduction of its specific reserve-path signature.

## ERR-0030 — Delta Research freeze prerequisite omitted on Develop

- Severity: P1 when reproduced.
- Status: `FIXED`.
- Failed Develop `24364b858e15fd9e3b06a9ee2eaf1f580b51364c`, canonical Quality `34379757715`, had exactly one failure: `tests/unit/test_research_delta.py::test_delta_research_freezes_only_new_explicit_sources`.
- Root cause: `ResearchRepository.freeze_local_candidates()` omitted `ResearchMode.DELTA` from the supported-mode allowlist.
- Integrator applied the bounded fix to Develop `10d36f23143afdf9050585b3cf7bb1139913fd86`; Quality `34391596966 = SUCCESS`.
- Do not reopen absent new exact-current reproduction.

## ERR-0026 — Backend quality drift

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical worker reproduction carried Ruff `I001` at `src/athena/storage/schema.py:3:1`, but that evidence is not on the current Backend exact SHA.
- Current Backend has no exact-current canonical reproduction of that Ruff signature. No formatter/product mutation is justified on Errors. Reopen only if the Ruff signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical Backend diagnostics decomposed old worker failures into terminal-current-schema assertions, duplicate-v41-table fixture collisions and downstream Storage-startup cascades on worker-only schema history.
- Current Backend has no ERR-0028 signature reproduced on its current exact SHA.
- Never change production v40→v41 migration to `IF NOT EXISTS`, swallow `OperationalError`, or weaken Storage/Recovery fail-closed behavior.
- Reopen only if a specific ERR-0028 signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0029 — WAL harness collaborators incompatible with exact-type runtime guards

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical worker diagnostics associated this cluster with WAL harness collaborators that did not satisfy production exact-type fail-closed guards. That historical worker evidence is not authoritative for the current exact worker head.
- Current Backend has no current exact reproduction of the ERR-0029 signature.
- Production exact-type fail-closed guards remain authoritative and must not be weakened. Reopen only after the same signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Closure evidence: canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.
- Do not reopen absent exact-current regression.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
