# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@54c990285503e5076d31f46408ef530b9f02de28` (`fix(ci): close core focused regression lint`).
- Develop parent `522a01050dba5b4dafa81d60573bd185a8e7e15b` had canonical Quality `34712404459 = FAILURE`; exact classification was Ruff `I001` in `tests/unit/test_core_focused_candidate_workflow.py` while Windows path safety, Linux storage regressions, Local Install and full pytest passed.
- Current Develop canonical Quality: `34715466882@54c990285503e5076d31f46408ef530b9f02de28 = IN_PROGRESS`; Errors started no competing canonical run.
- Error worker entered this run at `postmerge/errors@cc856567b5e7c05c8b36e919cddb7808476f366a`; that exact SHA had zero workflow runs before mutation.
- Current workers: Spec/Core `9f2052b9c10668ad9eeeb2857dbcbb25145cc832`; Backend `365df03a040cb9dffddf6f942ae61a2cdb8dc375`; UI `6bc46a2464344d56ca00461df30ba4a619437498`.
- Spec/Core exact `9f2052b9c10668ad9eeeb2857dbcbb25145cc832`: Core Focused `34713779890 = FAILURE`; canonical `34713779893 = FAILURE`. Focused diagnostics show exactly one Ruff `I001` in `tests/unit/test_revision_change_explanation.py`, six focused tests pass, and Ruff's own remediation diff removes one extra blank line after the import block. Canonical adds the Develop-parent Ruff defect in `test_core_focused_candidate_workflow.py`; full pytest passes.
- Backend exact `365df03a040cb9dffddf6f942ae61a2cdb8dc375`: Backend Focused `34714225610 = SUCCESS`; Storage Focused `34714225608 = SUCCESS`; canonical `34714225599 = SUCCESS`.
- UI exact `6bc46a2464344d56ca00461df30ba4a619437498`: canonical `34714819100 = IN_PROGRESS`; Core Focused `34714819122 = FAILURE`. Its artifact has Ruff `All checks passed!` and only two PySide6-dependent UI modules skipped (`test_pathena_comfyui_shell.py`, `test_pathena_pallas_full_view.py`) in a Core-only environment, exposing a separate focused-harness selection/zero-runnable-test problem rather than a UI product defect.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0042`, `ERR-0046`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0043`, `ERR-0045`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0044`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0046 — Core Focused harness selects UI unit tests without UI runtime

- Severity: P2 CI/harness integration blocker.
- Status: `OPEN`.
- Current exact reproducer: Core Focused Candidate `34714819122` on `postmerge/ui@6bc46a2464344d56ca00461df30ba4a619437498`.
- Exact artifact: Ruff is `All checks passed!`; focused pytest selects `tests/unit/test_pathena_comfyui_shell.py` and `tests/unit/test_pathena_pallas_full_view.py`, and both modules are skipped at collection because `PySide6` is absent. The run then fails at `Enforce focused candidate outcomes`.
- Root-cause boundary: `.github/workflows/core-focused-candidate.yml` currently treats every changed `tests/unit/test_*.py` as a Core-focused test and installs only the locked `dev` environment. UI-specific PySide tests therefore enter a Core lane that does not provide the UI runtime. This is not evidence of a UI product regression.
- Required safe harness repair: narrow Core-focused test selection to actual Core-owned tests or provide an explicit ownership allowlist that excludes UI-only test modules; alternatively, if Core intentionally owns such tests, install the exact runtime needed and require real runnable assertions. Do not turn skipped-only execution into success and do not weaken the final outcome gate.
- Closure requirement: reproduce the UI-change case on an exact candidate where Core Focused no longer fails spuriously, while a genuine Core test failure still fails the lane; then canonical success on the integrated workflow SHA.

## ERR-0045 — Backend absent-sidecar test fixture recreates WAL/SHM during read-only preflight

- Severity: P2 Storage test/harness integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical reproducer: `postmerge/backend@956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`, Storage Focused `34710537370 = FAILURE`, canonical `34710537369 = FAILURE`, with exact pytest `2 failed, 30 passed` in the absent-sidecar fixture.
- Owner repair: `postmerge/backend@365df03a040cb9dffddf6f942ae61a2cdb8dc375` (`test(storage): model validated sidecar-free preflight`). The helper now performs a normal validated read-only preflight first, checkpoints/truncates, closes SQLite, deletes WAL/SHM, then captures the file-set identity directly and constructs a `DatabasePreflightReport` from the previously validated metadata plus the proven sidecar-absent identity. It no longer calls the normal read-only inspector after deleting sidecars, so SQLite cannot republish them before the absence assertion.
- Exact owner verification: Backend Focused `34714225610 = SUCCESS`; Storage Focused `34714225608 = SUCCESS`; canonical Quality `34714225599 = SUCCESS` on the unchanged exact SHA.
- No Storage/Recovery guard was relaxed; the commit changes only `tests/unit/test_storage_database_startup_identity.py`.
- Final closure requirement: integrate the verified Backend successor and require Develop canonical `SUCCESS` before `FIXED`.

## ERR-0043 — Backend SQLite startup revalidation accepts foreign sidecar replacement

- Severity: P1 Storage/release integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical exact reproducer: `postmerge/backend@c5151466928dbe751a2e62c210717d0858a74bd3`, where `test_bound_preflight_rejects_sidecar_mutation_before_writer_open` proved a replaced existing sidecar was accepted.
- Product repair lineage: `postmerge/backend@956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc` restricts sidecar identity changes to the exact absent-both -> published-both transition with unchanged primary DB and a fresh exact-identity confirmation. Existing-sidecar replacement remains fail-closed.
- Strong current owner verification now exists on successor `365df03a040cb9dffddf6f942ae61a2cdb8dc375`: Backend Focused `34714225610 = SUCCESS`, Storage Focused `34714225608 = SUCCESS`, canonical `34714225599 = SUCCESS`. The successor's only mutation from `956cffa...` is the `ERR-0045` test fixture; product guard code is unchanged.
- Final closure requirement: integrated Develop canonical `SUCCESS` containing the verified Backend product lineage before `FIXED`.

## ERR-0042 — Spec/Core Ruff blocker in revision-change slice

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Current owner head: `postmerge/spec-core@9f2052b9c10668ad9eeeb2857dbcbb25145cc832` (`fix(core): close revision explanation Ruff regression`).
- Exact Core Focused `34713779890 = FAILURE`; exact canonical `34713779893 = FAILURE`.
- Downloaded focused artifact: Ruff still reports exactly one `I001` at `tests/unit/test_revision_change_explanation.py:1:1`; six focused tests pass. Ruff's generated remediation diff is one line only: remove the extra blank line between the final import and `KNOWLEDGE_ID`.
- Downloaded canonical artifact: specification validator passes, mypy passes, full pytest passes; Ruff reports two `I001` findings — the same owner-held revision-change file plus `tests/unit/test_core_focused_candidate_workflow.py`. The latter belongs to Develop parent `522a010...` and is independently addressed by current Develop `54c99028...`; it does not replace or close the owner-held revision-change Ruff defect.
- Required owner action: apply the exact one-line Ruff remediation to `tests/unit/test_revision_change_explanation.py`, then require Core Focused + canonical `SUCCESS` on one unchanged exact Spec/Core SHA. Final `FIXED` requires integrated Develop canonical success.

## ERR-0044 — Core Focused harness selects deleted files from PR diff

- Severity: P2 CI/harness integration blocker.
- Status: `FIXED`.
- Historical reproducer: Core Focused Candidate `34709115243` on `postmerge/ui@1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`, where deleted Core paths were incorrectly passed to Ruff/Pytest.
- Repair: all three Core diff selections use `git diff --diff-filter=ACMR --name-only`; remediation cleanliness uses `git status --porcelain --untracked-files=no`, preserving tracked-mutation fail-closed semantics.
- Integrated verification: canonical `34710920451@b8afe9661387c4a1a3d65f539c39ca772f37329c = SUCCESS`.
- `ERR-0046` is distinct: deletion handling is correct there; its root cause is ownership/runtime selection of existing UI test files.

## ERR-0041 — Spec/Core provenance explanation import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical reproducer: `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`; exact root cause Ruff `I001` at `src/athena/knowledge/provenance_explanation.py:3:1`.
- Owner repair verified at `postmerge/spec-core@1f61104959dc6a7d7fcff6051fb013f5f6894706`: Core Focused `34701843776 = SUCCESS`; canonical `34701843759 = SUCCESS`.
- Integrated closure: `34703645964@develop/pathena-next@452547ab46c5d8c678c22c3e1fb9d34652b653fd = SUCCESS`.

## ERR-0040 — Scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical reproducer `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`; repair `postmerge/backend@359b675a37b5b59210399bee1506afddc6ccee13`.
- Exact worker verification: Backend Focused `34693685313 = SUCCESS`; canonical `34693685375 = SUCCESS`.
- Integrated closure: `34694827693@develop/pathena-next@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity

- Severity: P1.
- Status: `FIXED`.
- Integrated closure: `34680853488@develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED`.
- Integrated closure: `34666307002@develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

## ERR-0039 / ERR-0038

Both are `STALE`; historical Spec/Core Ruff failures are superseded and may be reopened only with a new current exact-SHA reproduction.

## Persistent release guards

Historical closed/stale clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent guards remain binding: Windows `pypdf` packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature or removed guard is current.
