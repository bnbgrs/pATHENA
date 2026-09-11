# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7`.
- Error worker entered this run at `postmerge/errors@4134bb4ff3ab48b7e57fbfa86d92d6fd0e38cc2b`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `dcfe263eaf4c23fc9513b362dada138ae3108854`.
- Exact-current Develop canonical Quality: `34572000094@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7 = IN_PROGRESS`. The previous exact Develop canonical `34567856833@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e = SUCCESS` is fully completed.
- The sole Develop delta from `e6ba3d7557bd46094ad4e8f067a238e1c2375f8e` to `b58964d577aba5d4fcb6c2969f48b445f3a1d4d7` changes only `.github/workflows/ui-snapshot.yml` and `docs/agent_handoffs/integrator.md`; EmergencyReserve product/test source is unchanged.
- `postmerge/errors@4134bb4ff3ab48b7e57fbfa86d92d6fd0e38cc2b` had zero canonical Quality runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0033 — Emergency-reserve mutation identity binding gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current source verification: `develop/pathena-next@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7`; the one-commit delta from the previous canonical-green Develop changes only UI workflow diagnostics and Integrator documentation, so EmergencyReserve product/tests are unchanged.
- Existing focused coverage still contains adversarial parent-directory replacement tests only for POSIX. `test_posix_store_creation_does_not_publish_into_replaced_reserve_root` and `test_posix_store_release_does_not_unlink_replacement_root_file` skip when `os.name != "posix"`; native-Windows parent-swap coverage is absent.
- POSIX creation/release binds `reserve_root` to a directory descriptor for relative create/unlink and directory fsync. Windows/non-POSIX creation instead opens `self.path` by pathname, compares the opened file's `fstat` with pathname `stat`, then returns to pathname-based parent resolution for cleanup/durability; normal release is entirely pathname-based.
- Parent-directory binding alone is insufficient. In non-POSIX failure cleanup, `self.path.stat()` plus `samestat(created_identity)` is followed by a separate `self.path.unlink()`; a same-parent filename substitution between those operations can therefore cause unlink of a different file than the identity that was validated. Normal non-POSIX release has an even wider `exists/is_file/stat -> unlink` pathname window and does not bind the target file identity at all.
- POSIX release also closes the opened reserve-file descriptor before the later name-based `os.unlink(..., dir_fd=root_fd)`. The directory identity is bound, but the filename can still be replaced inside that same directory between file inspection and unlink.
- New exact-current refinement this run: POSIX *failure cleanup* has the same destructive target-identity discontinuity and is currently broader than release. `_ensure_posix()` records only `created = True`; on any later exception it closes the created descriptor and, if `created`, unconditionally executes `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)` followed by `os.fsync(root_fd)`. There is no `fstat`/identity comparison of the pathname immediately before unlink and the original file descriptor is already closed. A same-directory replacement of `emergency.reserve` after creation but before cleanup can therefore cause the cleanup path to delete the replacement file even though the parent directory itself remains correctly identity-bound.
- Existing `test_store_cleans_partial_file_when_allocation_fails` exercises ordinary cleanup only and asserts that the path disappears; it does not inject a same-parent filename substitution. The two adversarial POSIX tests exercise parent-directory replacement at create/release boundaries, not same-parent target replacement during the failure-cleanup boundary. Thus this newly identified POSIX cleanup seam is not covered by the focused regression suite on the exact current source.
- Backend handoff still marks BE-046 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED` and has no tested bounded product candidate. No competing Errors product mutation is justified.
- Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics.
- Closure requires a bounded Backend candidate plus focused adversarial tests for: native-Windows parent substitution over create-success/failure-cleanup/release; same-parent reserve-name substitution between identity check and unlink in non-POSIX cleanup/release; POSIX same-parent filename substitution on release; and POSIX same-parent filename substitution during `_ensure_posix()` failure cleanup after the created descriptor loses continuity. Then obtain exact-SHA canonical evidence as appropriate.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Current source evidence remains applicable: `SQLiteDatabase.start()` performs read-only preflight against the configured path and later independently opens the writable SQLite connection by pathname, without carrying an identity token/handle/descriptor from preflight into writer establishment.
- `src/athena/storage/recovery.py` preflight returns path/existence/application/schema/WAL/SHM facts but no filesystem identity capable of fencing the later writer open. A pathname replacement between preflight and writer establishment therefore remains an identity-continuity gap.
- Distinct from `ERR-0033`: ERR-0033 concerns EmergencyReserve filesystem-object identity across mutation; ERR-0035 concerns the primary SQLite database object between startup preflight and live writer open.
- Backend marks the same root cause BE-052 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED`; Errors makes no parallel product mutation.
- Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, WAL/SHM checks and fail-closed Recovery/Storage semantics. A second pathname-only preflight is insufficient.
- Closure requires a bounded Backend candidate plus focused cross-platform identity-swap regression evidence, followed by exact-SHA canonical evidence when integration/closure requires it.

## ERR-0037 — startup event filter teardown/partial-init lifecycle race

- Severity: P1 while it blocked canonical Develop.
- Status: `FIXED`.
- Exact reproduction: canonical Quality `34556269271@b1e77f8a4b90c12fe75e257b96303cc137d760a9 = FAILURE`; Windows path safety, Linux storage and Local-install remained green, while Python quality failed only at pytest.
- Diagnostic artifact records exactly `1 failed, 4830 passed, 3 skipped`; failing test `tests/unit/test_pathena_transient_dialog_shortcuts.py::test_tab_and_backtab_stay_inside_transient_surfaces` raised `AttributeError` from `PathenaStartupExperience.eventFilter()` because teardown/partial initialization could invoke the filter before `chat_messages` existed.
- Bounded correction: Develop `95b636c982a800d75f7d219162a04f6c87976e9f` guards the lifecycle-sensitive attribute with `getattr(self, "chat_messages", None)` before identity comparison. No test, Storage, Recovery, Security or release guard was weakened.
- Closure evidence: canonical Quality `34560421777@95b636c982a800d75f7d219162a04f6c87976e9f = SUCCESS`.
- Additional direct regression evidence: canonical Quality `34567856833@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e = SUCCESS`; this exact SHA includes the regression test that deletes `chat_messages` after initialization and requires `eventFilter()` to return `False`.

## ERR-0036 — stale UI typography assertion after intentional hierarchy promotion

- Severity: P1 while it blocked canonical Develop.
- Status: `FIXED`.
- Exact reproduction: canonical Quality `34539454111@4634bdf28c98bc114e0369701122818d474f99d9 = FAILURE`; only Python pytest failed. Diagnostics: `1 failed, 4830 passed, 3 skipped`; the stale test expected `(14, 11, 34)` while the integrated product/design-token contract is `(15, 12, 42)`.
- Bounded repair: Develop `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c` aligned only the stale exact tuple plus Integrator documentation. No assertion was removed or generalized; no Skip/XFail and no product/runtime/Security/Storage/Recovery code changes.
- Closure evidence: canonical Quality `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.

## ERR-0034 — native Windows durable-filesystem regression exposed by canonical coverage

- Severity: P1 when reproduced on canonical Develop.
- Status: `FIXED`.
- Exact failing reproduction: canonical Quality `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = FAILURE`, with Windows path safety failing at Windows storage regressions; Linux storage, Local install and full Python quality were otherwise green.
- Root cause: the CI-only Develop delta added POSIX-specific durable-FS contracts wholesale to `windows-latest`.
- Bounded correction: Develop `7fa2108d820cfc5b48a9f92d42ffa61697b74818` runs Windows-applicable durable filesystem regressions with `tests/unit/test_durable_fs.py -k "not test_posix"` and leaves POSIX parent-identity coverage in Linux. No Skip/XFail, assertion weakening or product behavior change.
- Closure evidence: canonical Quality `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`.

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
