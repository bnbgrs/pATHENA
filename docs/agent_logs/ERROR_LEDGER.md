# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`.
- Error worker entered this run at `postmerge/errors@86a990c600643a25168013ee18dce62fa35b55e1`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous exact Develop canonical Quality: `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58 = SUCCESS`.
- Exact current Develop canonical Quality: `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = IN_PROGRESS` at this checkpoint.
- Exact compare `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58...f29abc4341895f8ecd28ebeb0baa2e80b030fdf7` is exactly one commit and changes only `.github/workflows/quality.yml` plus `docs/agent_handoffs/integrator.md`; no Backend/Storage product source changed.
- Current Backend `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90` handoff keeps BE-046 as `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE` and supplies no bounded product candidate.
- `postmerge/errors@86a990c600643a25168013ee18dce62fa35b55e1` had zero check runs immediately before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0033 — Windows emergency-reserve directory-identity binding gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current direct source evidence: on `develop/pathena-next@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`, `src/athena/storage/emergency_reserve.py` binds POSIX reserve creation to an opened reserve-directory FD and calls `os.open(_RESERVE_FILENAME, ..., dir_fd=root_fd)`; POSIX release similarly opens and unlinks via the same `root_fd` and checks that directory identity remains current around mutation. The non-POSIX branch instead creates via `os.open(self.path, ...)`, verifies the created file against a subsequent pathname stat, and later performs cleanup/release through `self.path.stat()` / `self.path.unlink()` followed by pathname-based directory fsync. The reserve-directory identity is therefore not carried as a bound handle across the Windows mutation/release operation.
- Freshness proof: exact compare from canonical-green Develop `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58` to current `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7` changes only the Quality workflow and Integrator handoff. No relevant Backend/Storage product source changed.
- Canonical state is not misrepresented as a failing test: current Quality `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7` is still running; previous Quality `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58` completed SUCCESS. ERR-0033 stays OPEN because a current exact source trace establishes an uncovered identity-binding invariant, not because a canonical test failure was fabricated.
- Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics. Do not replace the requirement with weaker pathname-only checks.
- Closure requires a bounded Backend candidate plus focused Windows regression evidence proving reserve-directory identity remains bound across create/release mutation, including an adversarial directory-swap boundary; then consume exact-SHA canonical evidence as appropriate.

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
- Current Backend `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90` has no exact-current canonical reproduction of that Ruff signature. No formatter/product mutation is justified on Errors. Reopen only if the Ruff signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical Backend diagnostics decomposed old worker failures into terminal-current-schema assertions, duplicate-v41-table fixture collisions and downstream Storage-startup cascades on worker-only schema history.
- Current Backend is `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`; no ERR-0028 signature is reproduced on that exact SHA.
- Never change production v40→v41 migration to `IF NOT EXISTS`, swallow `OperationalError`, or weaken Storage/Recovery fail-closed behavior.
- Reopen only if a specific ERR-0028 signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0029 — WAL harness collaborators incompatible with exact-type runtime guards

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical worker diagnostics associated this cluster with WAL harness collaborators that did not satisfy production exact-type fail-closed guards. That historical worker evidence is not authoritative for the current exact worker head.
- Current Backend `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90` has no current exact reproduction of the ERR-0029 signature.
- Production exact-type fail-closed guards remain authoritative and must not be weakened. Reopen only after the same signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Closure evidence: canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.
- Do not reopen absent exact-current regression.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
