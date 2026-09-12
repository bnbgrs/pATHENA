# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@146fb7280dbfe30f2bec129aec8ee77f015ce040` (`feat(release): add fail-closed readiness assessment`).
- Error-worker source used for this reconciliation: `postmerge/errors@e33839260e5582e972aa6e311c9631afbe08fe24`.
- Current workers at reconciliation start: Spec/Core `a35a67f1afe2789d8a568fa3484ef5fe29f46de9`; Backend `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`; UI `9e9227dc722d7d771ae4ce4e45a75983330fed97`.
- Exact-current Develop canonical Quality: `34697870543@146fb7280dbfe30f2bec129aec8ee77f015ce040 = FAILURE`; only Ruff failed. Specification validator, mypy, full pytest (`4982 passed, 17 skipped`), Windows Path Safety, Linux Storage Regressions and Local Install Smoke succeeded.
- Backend exact `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`: Backend Focused `34700396671 = SUCCESS`; canonical Quality `34700396666 = IN_PROGRESS` at observation, with specification validator, Ruff, mypy, Windows, Linux storage and local install already green and full pytest still running.
- Spec/Core exact `a35a67f1afe2789d8a568fa3484ef5fe29f46de9`: Core Focused `34698818610 = SUCCESS`; canonical Quality `34698818608 = FAILURE` only because it inherits current Develop ERR-0042. Canonical specification validator, mypy, full pytest (`4989 passed, 17 skipped`), Windows, Linux storage and local install succeeded.
- UI exact `9e9227dc722d7d771ae4ce4e45a75983330fed97`: UI Focused `34699977144 = SUCCESS`; canonical `34699977161` carries inherited ERR-0042; Core Focused `34699977166 = FAILURE` due ERR-0043.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: none.
- IN_PROGRESS: `ERR-0042`, `ERR-0043`.
- FIXED_PENDING_VERIFY: `ERR-0041`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0043 — Core Focused candidate selector treats deleted files as runnable paths

- Severity: P1 CI/integration blocker.
- Status: `IN_PROGRESS`.
- Exact reproducer: UI synchronization head `postmerge/ui@9e9227dc722d7d771ae4ce4e45a75983330fed97`, Core Focused run `34699977166 = FAILURE`.
- Root cause 1: `.github/workflows/core-focused-candidate.yml` uses `git diff --name-only` without a diff filter, so paths deleted from the candidate are passed to Ruff and pytest. The reproducer selected deleted `src/athena/knowledge/orphan_knowledge.py` and `tests/unit/test_orphan_knowledge.py`, producing Ruff `E902 No such file or directory` and pytest `file or directory not found`.
- Root cause 2: the diagnostic remediation creates `.focused-evidence/` and then checks `git status --porcelain`, so its own intentionally untracked diagnostics make the candidate appear dirty and block remediation.
- Repair candidate: PR `#122`, branch `manual/core-focused-deletion-harness-20260912`, documented exact head `69dde85574960860a01b4eba8f31318231627d71`, stacked only on ERR-0042 repair to avoid inherited baseline pollution.
- Repair policy: all three changed-file selectors use `--diff-filter=ACMRT`, excluding deleted paths while preserving added/copied/modified/renamed/type-changed candidate files; remediation uses `git status --porcelain --untracked-files=no` before and after; final Ruff + focused pytest enforcement remains unchanged.
- Contract coverage: `tests/unit/test_core_focused_workflow_contract.py` locks deletion-aware selection, tracked-cleanliness checks and dual enforcement.
- Closure requirement: exact repaired Develop integration plus evidence that the updated Core Focused contract no longer fails on deleted candidate paths. Do not restore deleted product/test files merely to satisfy the old harness.

## ERR-0042 — Develop release-readiness import-format Ruff baseline failure

- Severity: P1 integration blocker.
- Status: `IN_PROGRESS`.
- Exact reproducer: `develop/pathena-next@146fb7280dbfe30f2bec129aec8ee77f015ce040`, canonical Quality `34697870543 = FAILURE`.
- Exact isolation: specification validator `SUCCESS`; Ruff `FAILURE`; mypy `SUCCESS`; full pytest `SUCCESS` with `4982 passed, 17 skipped`; Windows Path Safety `SUCCESS`; Linux Storage Regressions `SUCCESS`; Local Install Smoke `SUCCESS`.
- Ruff reports exactly two `I001` errors: `src/athena/release_readiness.py:3:1` and `tests/unit/test_release_readiness.py:1:1`. Both are formatting-only import-block defects; the release-readiness product tests themselves pass.
- Independent corroboration: current Backend head `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8` carries Ruff-green versions of those exact two blobs without changing release-readiness behavior.
- Bounded repair candidate: PR `#121`, `manual/develop-release-readiness-ruff-20260912@22f7b640cccad1a65ccc6a32e46778b47e2a697e`. It ports only the two Ruff formatting corrections plus bot handoff; Backend Schedule Recovery code is deliberately excluded.
- Exact candidate verification at observation: canonical `34700566097` has specification validator, Ruff, mypy, Windows, Linux storage and local install green; full pytest is still running.
- Closure requirement: exact #121 head canonical SUCCESS, controlled merge into current Develop, then post-merge canonical SUCCESS on the resulting exact Develop SHA.

## ERR-0041 — Spec/Core provenance explanation import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical exact reproducer: `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`; Core Focused `34696122597 = FAILURE`, canonical `34696122599 = FAILURE`, caused by Ruff `I001` in `src/athena/knowledge/provenance_explanation.py`.
- Current repair SHA: `postmerge/spec-core@a35a67f1afe2789d8a568fa3484ef5fe29f46de9` (`fix(core): satisfy provenance explanation Ruff contract`). Current file has the organized standard-library import block.
- Exact focused verification: Core Focused `34698818610 = SUCCESS`.
- Canonical `34698818608` no longer reports the provenance explanation import defect; it fails only on inherited Develop ERR-0042. Its specification validator, mypy, full pytest (`4989 passed, 17 skipped`), Windows, Linux storage and local install are green.
- Final closure requirement: after ERR-0042 is integrated, refresh/sync Spec/Core against the repaired Develop baseline and obtain exact-current canonical evidence without reintroducing the provenance import failure.

## ERR-0040 — Scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical exact reproducer: `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`; canonical Quality `34691380019 = FAILURE` with five setup errors in `tests/unit/test_scheduled_materialization.py` caused by a `sqlite3.connect(":memory:")` fixture hitting the fail-closed v37->v38 physical-cleanup journal-mode invariant.
- Root-cause repair exact worker SHA: `postmerge/backend@359b675a37b5b59210399bee1506afddc6ccee13`; file-backed temporary SQLite fixture, canonical schema initializer retained, no Storage/Recovery/Security guard relaxation.
- Exact worker verification: Backend Focused `34693685313 = SUCCESS`; canonical Quality `34693685375 = SUCCESS`.
- Integrated closure SHA: `develop/pathena-next@cfdcac0bd51973bc18343006a9fb02f6c098a3c0`.
- Exact integrated canonical closure: `34694827693@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-052; integrated repair by Integrator.
- Integrated closure SHA: `develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71`.
- Exact integrated canonical Quality `34680853488@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-046.
- Exact integrated Develop closure remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

## ERR-0039 — Historical Spec/Core exact-head Ruff import-format blocker

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Historical exact reproducer `58b8040f84d5cac2530aaaac349c695361a78996` is superseded. Reopen only with a current exact-SHA reproduction.

## ERR-0038 — Historical Spec/Core exact-head Ruff failure

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Historical exact reproducer `53c3824e214b66e989cba1f425bfe7881190e12f` is superseded. Reopen only with a current exact-SHA reproduction.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature or a removed release guard is current.
