# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@4634bdf28c98bc114e0369701122818d474f99d9`.
- Error worker entered this run at `postmerge/errors@f7f8d1d2f86743dac87538ca4ce99d34f1c0d145`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `b411e75a3481649b33edc70b74c22f64ab71c6d4`; UI `d55877cd353f7ee598df8213b9508fb143e51e15`.
- Latest exact current Develop canonical Quality: `34539454111@4634bdf28c98bc114e0369701122818d474f99d9 = IN_PROGRESS`; no failure is inferred from the incomplete run.
- Last completed exact Develop canonical Quality: `34534330414@29540b7a1f2cb09e3a1be9aee2a29e357c8a8724 = SUCCESS`.
- Current Develop commit `4634bdf2...` changes the bounded UI typography hierarchy plus its focused test and Integrator handoff; Storage/Recovery product source is unchanged.
- `postmerge/errors@f7f8d1d2f86743dac87538ca4ce99d34f1c0d145` had zero canonical Quality runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- New exact-current source verification: `src/athena/storage/database.py` at Develop `4634bdf28c98bc114e0369701122818d474f99d9` calls `inspect_database_read_only(self.path)` and then independently opens the writable connection with `sqlite3.connect(self.path, ...)`. No identity token, handle or verified descriptor from the preflight is carried into that writer open.
- `src/athena/storage/recovery.py` at the same exact SHA confirms the preflight returns only path/existence/application/schema/WAL/SHM facts. It resolves and opens a read-only SQLite connection for integrity checks, closes that connection, and returns no filesystem identity capable of fencing the later writer open. A pathname can therefore be replaced between preflight completion and writer connection establishment without the preflight identity being cryptographically or handle-bound to the object subsequently opened for writes.
- This is a distinct TOCTOU/root-identity cluster from `ERR-0033`: ERR-0033 concerns EmergencyReserve directory identity across create/release mutation; ERR-0035 concerns the canonical SQLite database object between startup preflight and live writer open.
- Current Backend handoff independently marks BE-052 `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE` and has no bounded candidate. Errors therefore makes no parallel product mutation.
- Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, WAL/SHM checks and fail-closed Recovery/Storage semantics. Do not replace this with a second pathname-only preflight.
- Closure requires a bounded Backend candidate plus focused cross-platform identity-swap regression evidence showing the object accepted by preflight is the same object opened as the live writer, followed by exact-SHA canonical evidence when integration/closure requires it.

## ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

- Severity: P1 when reproduced on canonical Develop.
- Status: `FIXED`.
- Exact failing reproduction: canonical Quality `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = FAILURE`, with Windows path safety failing at `Run Windows storage path regressions`; Linux storage, Local install and full Python quality were otherwise green.
- Root cause: the CI-only Develop delta added `tests/unit/test_durable_fs.py` and `tests/unit/test_durable_fs_parent_identity.py` wholesale to `windows-latest`. `test_durable_fs.py` contains explicit `test_posix_*` contracts that force POSIX-only `dir_fd` / directory-fsync behavior, while `test_durable_fs_parent_identity.py` skips every test unless `os.name == "posix"`. The failing lane therefore mixed POSIX-specific contracts into native Windows coverage; no production regression was required to explain the failure.
- Bounded correction: Develop `7fa2108d820cfc5b48a9f92d42ffa61697b74818` restored the prior Windows-applicable storage command, added a dedicated `Run Windows durable filesystem regressions` step executing `tests/unit/test_durable_fs.py -k "not test_posix"`, and left the POSIX parent-identity module in Linux storage coverage. No Skip/XFail was added; no test assertion or product behavior changed.
- Focused exact-SHA verification: canonical Quality `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`; Windows path safety, `Run Windows storage path regressions`, `Run Windows durable filesystem regressions`, Linux storage, Local install and full Python quality all completed successfully.
- Closure: `FIXED`. Reopen only if the same platform-selection signature is reproduced on a then-current exact SHA. A different future failure receives a separate root-cause cluster.
- Preserve HANDLE-bound rename, reparse/symlink rejection, write-through durability, directory identity and Storage/Recovery fail-closed semantics.

## ERR-0033 — Windows emergency-reserve directory-identity binding gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current source verification remains applicable on current Develop because `src/athena/storage/emergency_reserve.py` is unchanged by `4634bdf2...`. POSIX reserve creation/release binds mutation to an opened parent directory FD; the non-POSIX branch still relies on pathname-based create/stat/unlink/fsync sequencing and does not carry reserve-directory identity as a bound handle across the Windows mutation/release operation.
- Current Backend handoff marks BE-046 `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE` and has no bounded candidate. Errors therefore makes no parallel product mutation.
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
