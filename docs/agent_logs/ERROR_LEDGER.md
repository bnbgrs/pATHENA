# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@0d3ca68731ded061b0720bd94d649f3dfed59a45`.
- Error worker entered this run at `postmerge/errors@df3f63e0c0c717f0bbd8a4388535c5cd645e83ee`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Latest exact current Develop canonical Quality: `34486592055@0d3ca68731ded061b0720bd94d649f3dfed59a45 = IN_PROGRESS`. At inspection time Linux storage regressions and Local install smoke/pypdf were green; Windows path safety and Python quality were still running. No failure was yet evidenced on that exact SHA.
- Last completed Develop canonical Quality: `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978 = SUCCESS`.
- Current Backend head `a5e28d3c9d3f215620fe69a7dfa9e024155037cf` is a handoff-only descendant of the last red Backend worker lineage and has no exact-current canonical reproduction. Its handoff explicitly marks broad Storage/Migration/WAL history HOLD and non-authoritative relative to current Develop.
- `postmerge/errors` had zero canonical Quality runs before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- IN_PROGRESS: `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`.
- BLOCKED: none at top level.

## ERR-0032 — schema-reinitialization harness row-shape mismatch

- Severity: P1 when reproduced on Develop.
- Status: `FIXED`.
- First exact reproduction: canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821 = FAILURE`. `initialize_schema()` reached schema verification with tuple rows from the raw test connection, causing `TypeError: tuple indices must be integers or slices, not str` where named-row access is required.
- First bounded correction: Develop `4d37a8276211ab9bb2d1f49ec17c8915d0ba95f3` added `connection.row_factory = sqlite3.Row`. Canonical Quality `34463015234` then exposed the remaining test-only shape mismatch: the two `PRAGMA user_version` assertions still compared `sqlite3.Row` directly with `(SCHEMA_VERSION,)`.
- Final bounded correction: Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` changed only those two existing assertions to scalar comparison through `[0]`; both `initialize_schema()` calls and the same schema-version invariant remained intact.
- Closure evidence: canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`, including full pytest and Windows path safety/storage regressions.
- Newer completed Develop `38586782fd9b615ecd4226a4b0afe674d5520978` is also canonical-green at Quality `34473603186`; there is no exact-current recurrence of the ERR-0032 signature.
- No production schema, migration, Storage, Recovery, Runtime or Security behavior changed. No SQLite exception is swallowed; duplicate-column/additive-migration failures remain visible.
- Do not reopen absent a new exact-current reproduction of this specific row-shape/schema-reinitialization signature.

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
- Current Backend `a5e28d3c9d3f215620fe69a7dfa9e024155037cf` is a docs-only handoff refresh over the older red worker lineage and has no exact-current canonical failure. Under the current-evidence rule, the historical Ruff finding is therefore not active.
- Last completed authoritative Develop `38586782fd9b615ecd4226a4b0afe674d5520978` is canonical-green at Quality `34473603186`, including Ruff; Develop/Error already carry the normalized schema import layout. Backend handoff explicitly says broad worker history is HOLD/non-authoritative against current Develop.
- No formatter/product mutation is justified on Errors. Reopen only if the Ruff signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions

- Severity: P2 on Backend when exactly reproduced; not a current proven Develop blocker.
- Status: `STALE`.
- Historical Backend diagnostics decomposed old worker failures into terminal-current-schema assertions, duplicate-v41-table fixture collisions and downstream Storage-startup cascades on worker-only schema history.
- Current Backend is `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`. The newest Backend Quality is still `34455900467@7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2 = FAILURE`; no canonical run reproduces the ERR-0028 signatures on current Backend head `a5e28d3c...`.
- Backend's current handoff explicitly marks broad schema-v41 / Storage / Migration / WAL history `HOLD / NOT READY` and non-authoritative relative to current Develop.
- Last completed authoritative Develop `38586782fd9b615ecd4226a4b0afe674d5520978` is canonical-green (`34473603186 = SUCCESS`), and the newer exact Develop run `34486592055@0d3ca68731ded061b0720bd94d649f3dfed59a45` had no evidenced failure at inspection time.
- Therefore the old worker fixture failures do not remain active merely because they were once reproducible. No schema fixture or production migration mutation is justified on Errors in this run.
- Never change production v40→v41 migration to `IF NOT EXISTS`, swallow `OperationalError`, or weaken Storage/Recovery fail-closed behavior.
- Reopen only if a specific ERR-0028 signature is reproduced on a then-current exact Backend or Develop SHA.

## ERR-0029 — WAL harness collaborators incompatible with exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS` pending fresh exact-current Backend diagnostics.
- Production exact-type fail-closed guards remain authoritative and must not be weakened.

## ERR-0027 — v41 schema contract constant re-export

- Severity: P2.
- Status: `FIXED`.
- Closure evidence: canonical Backend Quality `34340662717@db0f5f440fab60b3e66c4d3843c42147a1937aba`, with `tests/unit/test_schema_contract_boundary.py` 5/5 PASS.
- Do not reopen absent exact-current regression.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.