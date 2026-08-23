# pATHENA Full Gate Recovery

Single source of truth for recovery of the complete required quality/CI gate on `agent/pathena`.

Status values: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `VERIFIED`, `STALE`, `BLOCKED`.

## Current recovery baseline

- Observed remote HEAD before this document mutation: `0ab4cb2fb3883122571634e64fbdf66e4cf8b5e2`.
- Current-head GitHub Actions run: `#2869` / `32668547243`, status `pending` at observation time; no jobs had started, so no current-head PASS/FAIL is claimed.
- Newest fully decoded multi-job baseline remains run `#2771` on historical head `a683577c5e69b85308588b0b6b7b1675faae91ee`: specification PASS 63/63; Ruff FAIL 14 diagnostics; mypy FAIL 25 errors/16 files; pytest native SIGSEGV/-11 around 65%; focused Linux storage PASS 157; Linux API runtime boundaries PASS 12; Windows locality PASS; Windows selected storage PASS 109; Windows API runtime boundaries PASS 12; local install smoke FAIL before Core start.
- Historical PASS values do not transfer to the current HEAD.
- Recovery state: **P0 ACTIVE / NOT GREEN** until every required current-head job completes successfully.

## Active blockers

### FGATE-001 — Productive Core extraction composition

- Priority: P0
- Current evidence: run #2771 Local install smoke; historical mypy from the same run.
- Exact failure: `TypeError: ChatKnowledgeExtractionService.__init__() missing 1 required keyword-only argument: 'chat'`.
- Reproduction: Local install smoke / productive `AthenaApplication` construction.
- Root-cause class: product code composition error.
- Ownership: BACKEND.
- Components: `src/athena/core/application.py`, chat knowledge extraction composition.
- Required fix invariant: productive construction must pass the same live `ChatService` dependency required by `ChatKnowledgeExtractionService`; no test bypass.
- Status: FIXED_PENDING_VERIFY.
- Latest static evidence: current `application.py` now constructs `ChatKnowledgeExtractionService(chat=self.chat, chat_generation=..., provider=..., runs=..., snapshots=...)`; the historical missing dependency is therefore statically fixed, but no current-head Local install smoke has completed yet.
- Targeted verification: application construction/extraction composition tests, then `athena-local-smoke --restart-cycles 1`.
- Last full-gate status: historical FAIL; current-head run #2869 pending.

### FGATE-002 — Native Qt/PySide PALLAS crash

- Priority: P0
- Current evidence: runs #2677 and #2771.
- Exact failure: pytest process terminates with native SIGSEGV / exit `-11` in the PALLAS target-binding path (`ascii_panel._bind_pallas_target()` / page selection), previously reached from `test_pathena_command_palette_presentation.py`.
- Reproduction: Linux full pytest under the Quality workflow; independently reproduced in two historical runs.
- Root-cause class: product code / native UI lifecycle or re-entrancy crash.
- Ownership: UI.
- Components: PALLAS ASCII panel target binding, desktop page-selection integration, related presentation tests.
- Required fix invariant: target binding/page selection must not re-enter or access invalid Qt object state; full pytest must complete normally without process signal termination. Tests must not be skipped or weakened.
- Status: FIXED_PENDING_VERIFY.
- UI fix: commit `6de4746c978b68eeea700f4c441d6bc2cfc54d52` removes application-global `QApplication.allWidgets()` target binding and scopes both PALLAS canvas lookup and semantic sampling to the owning top-level window. Cross-window target binding is rejected explicitly before paint interception.
- Regression coverage: commit `be9da30da3f3f874a985d8fdc999a641e2c746dd` adds two-window ownership coverage, repeated page/context switching, and semantic-sampling isolation.
- Targeted verification observed in this automation environment: **NOT EXECUTABLE** because a local checkout could not be obtained (`Could not resolve host: github.com`). No pytest/Ruff/mypy PASS is claimed. The separate Full Gate Recovery bot must execute focused Qt-offscreen coverage and the full pytest lane.
- Targeted verification: `tests/unit/test_pathena_pallas_target_lifecycle.py`, historical `tests/unit/test_pathena_command_palette_presentation.py`, then full pytest under Qt offscreen.
- Last full-gate status: historical FAIL; current-head verification pending.

### FGATE-003 — Research model typing failures

- Priority: P0
- Current evidence: run #2771 reconfirmed two mypy diagnostics in `src/athena/research/models.py`.
- Root-cause class: lint/typecheck.
- Ownership: BACKEND.
- Components: `src/athena/research/models.py`.
- Required fix invariant: narrow persisted/untyped values before comparison/conversion and remove loop-variable type conflict without changing runtime validation semantics.
- Status: ASSIGNED.
- Targeted verification: mypy on the module plus its boundary/model tests.
- Last full-gate status: historical mypy FAIL; current-head run #2869 pending.

### FGATE-004 — Research idempotency typing failures

- Priority: P0
- Current evidence: run #2771 reconfirmed three mypy unreachable diagnostics in `src/athena/research/idempotency.py`.
- Root-cause class: lint/typecheck.
- Ownership: BACKEND.
- Components: `src/athena/research/idempotency.py`.
- Required fix invariant: align annotations and runtime rejection of string/bytes-like values so mypy and runtime contract agree; do not remove validation merely to satisfy typing.
- Status: ASSIGNED.
- Targeted verification: mypy on the module plus idempotency boundary tests.
- Last full-gate status: historical mypy FAIL; current-head run #2869 pending.

### FGATE-005 — Semantic persisted-integer typing failures

- Priority: P0
- Current evidence: run #2771 reconfirmed `_persisted_int()` `int(object)` overload and `no-any-return` diagnostics.
- Root-cause class: lint/typecheck.
- Ownership: BACKEND.
- Components: `src/athena/retrieval/semantic.py`.
- Required fix invariant: explicit supported-type narrowing/parser returning a statically known `int`, while continuing to reject bool/invalid objects and preserving nonnegative/positive range rules.
- Status: ASSIGNED.
- Targeted verification: mypy on semantic retrieval plus persisted-state numeric boundary tests.
- Last full-gate status: historical mypy FAIL; current-head run #2869 pending.

## Secondary recovery items

### FGATE-006 — Quality workflow import ordering

- Priority: P1
- Root-cause class: lint/typecheck.
- Ownership: QUALITY.
- Component: `tests/unit/test_quality_workflow_contract.py`.
- Required fix invariant: Ruff-clean canonical imports without weakening workflow-contract coverage.
- Status: FIXED_PENDING_VERIFY.
- Last known fix: Quality commit `008647cf4e20617c70ff8f9918b3d53632c99b62`.
- Targeted verification: Ruff on the file / workflow-contract test; current-head full gate still required.

### FGATE-007 — Post-refactor durable filesystem identity lane

- Priority: P1
- Root-cause class: regression verification / platform boundary.
- Ownership: QUALITY verification; BACKEND for any product failure.
- Components: `tests/unit/test_durable_fs.py`, `tests/unit/test_durable_fs_parent_identity.py`, focused Linux storage job.
- Required fix invariant: parent-identity protections remain deterministic and pass independently of UI full-suite state.
- Status: IN_PROGRESS.
- Targeted verification: focused Linux storage job on current code.

### FGATE-008 — Windows durable-write parent identity

- Priority: P1
- Root-cause class: platform difference / race / TOCTOU.
- Ownership: MIXED.
- Primary implementation owner: BACKEND.
- Secondary reviewers: SECURITY.
- Verification owner: QUALITY.
- Components: Windows durable filesystem publication used by migration journal.
- Required fix invariant: mutation/publication must be bound to or revalidate the intended parent directory identity across the operation, rather than trusting only path-based prechecks before `MoveFileExW` publication.
- Security review evidence: current Windows `durable_write_bytes()` creates the temporary by pathname and current Windows `durable_replace()` publishes through pathname-based `MoveFileExW`; unlike the POSIX implementation, no opened parent-directory identity is held across creation/publication. Static symlink/junction/reparse checks alone therefore do not close concurrent parent replacement.
- Sub-slices:
  - `FGATE-008-BE` — Owner: BACKEND — implement Windows HANDLE-backed or equivalently identity-bound create/publication semantics without weakening durability or reparse protection. Status: ASSIGNED.
  - `FGATE-008-SEC` — Owner: SECURITY — define/review the security invariant and adversarial parent-replacement, junction/reparse and fail-closed regression cases; do not implement Backend product I/O. Status: IN_PROGRESS.
  - `FGATE-008-QA` — Owner: QUALITY — execute deterministic native-Windows regressions and the required integrative storage/full-gate verification on the relevant HEAD. Status: ASSIGNED.
- Status: ASSIGNED.
- Targeted verification: deterministic Windows parent-replacement/reparse regression plus native Windows storage lane.

## Verified historical infrastructure properties

- Keep-going gate behavior is verified by historical runs #2677 and #2771: later mypy/pytest checks executed despite earlier Ruff failures.
- Focused Linux storage, Local install smoke, and native Windows jobs execute independently of the Linux full-suite process.
- Historical infrastructure verification is not a substitute for current-head green status.

## Recovery next action

1. Wait for/start from the first current-head-equivalent run that actually obtains runners; decode every required job and step.
2. If a newer agent commit supersedes the pending run, move the baseline to the new remote HEAD and never claim the older run as current green evidence.
3. Close `FGATE-001` only after current-code targeted construction/Local smoke PASS.
4. Verify `FGATE-002` with focused Qt-offscreen PALLAS lifecycle tests and the full pytest lane; close only after the native process exits normally.
5. For the first current red job, classify the primary failure before consequences, update the stable FGATE entry, and hand off by ownership; Quality-owned harness/workflow/fixture defects may be fixed here.
6. Full recovery is complete only when all required jobs for the relevant development HEAD are successful and no required check is skipped.
