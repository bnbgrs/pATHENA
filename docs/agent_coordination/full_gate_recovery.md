# pATHENA Full Gate Recovery

Single source of truth for recovery of the complete required quality/CI gate on `agent/pathena`.

Canonical Ownership values: `QUALITY`, `BACKEND`, `UI`, `SECURITY`, `FEATURE`, `MIXED`, `EXTERNAL`.
Status values: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `VERIFIED`, `STALE`, `BLOCKED`.

## Current recovery baseline

- Candidate HEAD: `c59778dcd90b11dd8ee2176b381db0af06848725`.
- Required GitHub Actions run: `#2940` / `32688019606` on that exact SHA.
- Run conclusion: **FAILURE**. Recovery state remains **P0 ACTIVE / NOT GREEN**.
- Same-SHA required jobs:
  - `Python 3.12 quality` / job `97317379431`: **FAIL** at `Run ATHENA quality gate`.
  - `Linux storage regressions` / job `97317379351`: **PASS**.
  - `Windows path safety` / job `97317379417`: **PASS**.
  - `Local install smoke` / job `97317379343`: **PASS**.
- Central quality sub-checks on the same SHA:
  - Specification validator: **PASS** (`63/63`).
  - Ruff: **FAIL**.
  - mypy: **FAIL** (`40 errors in 11 files`, 193 source files checked).
  - pytest: **FAIL**, native `SIGSEGV` / exit `-11` at about 65% of the suite.
- Keep-going behavior is verified: mypy and pytest still executed after Ruff failed.
- Historical PASS values are not transferred to this SHA.

## Active blockers

### FGATE-002 — Historical PALLAS native crash pending exact verification

- Priority: P0
- Evidence: historical runs #2677 and #2771 terminated pytest with native SIGSEGV / exit `-11` in the PALLAS target-binding/page-selection path.
- Candidate-SHA evidence: run #2940 progressed to a different native UI crash in the image-preview path. That does not prove the historical PALLAS reproducer is fixed because the full suite never completed.
- Root-cause class: product code / native UI lifecycle or re-entrancy crash.
- Ownership: UI.
- Components: PALLAS ASCII target binding, desktop page-selection integration, presentation/lifecycle tests.
- Required fix invariant: target binding/page selection must not re-enter or access invalid Qt object state; targeted lifecycle tests and full pytest must exit normally.
- Status: FIXED_PENDING_VERIFY.
- Targeted verification: `tests/unit/test_pathena_pallas_target_lifecycle.py`, `tests/unit/test_pathena_command_palette_presentation.py`, then full pytest under Qt offscreen.
- Last gate status: run #2940 full pytest did not complete because FGATE-010 crashed first/later in suite execution.

### FGATE-003 — Research model typing failures

- Priority: P0
- SHA/run evidence: `c59778dcd90b11dd8ee2176b381db0af06848725` / #2940 / central quality mypy.
- Error excerpt: `src/athena/research/models.py` still reports two `no-any-return` diagnostics in functions declared to return `str`.
- Root-cause class: lint/typecheck.
- Ownership: BACKEND.
- Components: `src/athena/research/models.py`.
- Required fix invariant: preserve runtime validation semantics while returning statically proven strings.
- Status: ASSIGNED.
- Targeted verification: mypy on the module plus Research model boundary tests.
- Last gate status: **FAIL** on #2940.

### FGATE-004 — Research idempotency typing failures

- Priority: P0
- SHA/run evidence: `c59778dcd90b11dd8ee2176b381db0af06848725` / #2940 / central quality mypy.
- Error excerpt: `_persisted` integer conversion still reaches `int(object)`/`Any` return diagnostics and a bytes-assignment mismatch remains in `src/athena/research/idempotency.py`.
- Root-cause class: lint/typecheck.
- Ownership: BACKEND.
- Components: `src/athena/research/idempotency.py`.
- Required fix invariant: explicit type narrowing must preserve persisted-value validation and bytes semantics without casts that hide invalid runtime states.
- Status: ASSIGNED.
- Targeted verification: mypy on the module plus idempotency boundary tests.
- Last gate status: **FAIL** on #2940.

### FGATE-005 — Semantic persisted-integer typing failures

- Priority: P0
- SHA/run evidence: `c59778dcd90b11dd8ee2176b381db0af06848725` / #2940 / central quality Ruff+mypy.
- Error excerpt: `src/athena/retrieval/semantic.py` has unused `sys`/`Mapping` imports plus mypy `int(object)` and `Any` return diagnostics.
- Root-cause class: lint/typecheck.
- Ownership: BACKEND.
- Components: `src/athena/retrieval/semantic.py`.
- Required fix invariant: reject unsupported persisted values and return a statically narrowed integer while preserving numeric/range invariants.
- Status: ASSIGNED.
- Targeted verification: Ruff+mypy on semantic retrieval plus persisted-state numeric boundary tests.
- Last gate status: **FAIL** on #2940.

### FGATE-008 — Windows durable-write parent identity

- Priority: P1
- Root-cause class: platform difference / race / TOCTOU.
- Ownership: MIXED.
- Primary implementation owner: BACKEND.
- Secondary reviewers: SECURITY.
- Verification owner: QUALITY.
- Components: Windows durable filesystem publication used by migration journal and API secret publication.
- Required fix invariant: mutation/publication must be bound to or revalidate the intended parent directory identity across the operation rather than trusting pathname-only prechecks before publication.
- Related conflict: `CONFLICT-001`.
- Sub-slices:
  - `FGATE-008-BE` — Owner: BACKEND — implement Windows HANDLE-backed or equivalently identity-bound create/publication semantics. Status: ASSIGNED.
  - `FGATE-008-SEC` — Owner: SECURITY — define/review adversarial parent-replacement, junction/reparse and fail-closed invariants. Status: IN_PROGRESS.
  - `FGATE-008-QA` — Owner: QUALITY — execute deterministic native-Windows parent-identity regressions and integrative storage/full-gate verification after implementation. Status: ASSIGNED.
- Status: ASSIGNED.
- Candidate-SHA evidence: #2940 `Windows path safety` is PASS, but the workflow's Windows job does **not** execute `test_durable_fs.py`, `test_durable_fs_parent_identity.py`, or an equivalent deterministic parent-swap regression. Linux identity coverage PASS cannot be transferred to native Windows semantics.
- Targeted verification: deterministic native-Windows parent-replacement/reparse regression plus Windows storage lane.

### FGATE-010 — Rich-chat image-preview native Qt crash

- Priority: P0
- SHA/run/job/step: `c59778dcd90b11dd8ee2176b381db0af06848725` / #2940 / `97317379431` / pytest inside `Run ATHENA quality gate`.
- Error excerpt: native `SIGSEGV` / exit `-11`; active stack reaches `src/athena/ui/rich_chat.py:eventFilter` -> `insert_attachment` -> `src/athena/ui/main_window.py:_handle_assistant_preview` -> `_handle_model_action` -> `tests/unit/test_main_window_model_actions.py::test_main_window_model_action_handles_image_preview_without_forcing_chat`.
- Reproduction: `QT_QPA_PLATFORM=offscreen uv run --locked --extra dev --extra desktop pytest -q tests/unit/test_main_window_model_actions.py::test_main_window_model_action_handles_image_preview_without_forcing_chat`, then full pytest.
- Root-cause class: product code / native Qt lifecycle, event-filter or re-entrancy crash.
- Ownership: UI.
- Components: `src/athena/ui/rich_chat.py`, `src/athena/ui/main_window.py`, model-action image-preview path.
- Required fix invariant: image preview/attachment insertion must not re-enter or access invalid Qt state; targeted test and full pytest must terminate normally without weakening/skipping UI coverage.
- Status: ASSIGNED.
- Targeted verification: exact reproducer above plus related rich-chat attachment/model-action tests, then full pytest under Qt offscreen.
- Last gate status: **FAIL** on #2940.

### FGATE-011 — Core application lint/typecheck regression cluster

- Priority: P0
- SHA/run evidence: `c59778dcd90b11dd8ee2176b381db0af06848725` / #2940 / Ruff+mypy.
- Error excerpt: `src/athena/core/application.py` has Ruff import ordering, unused `ResourceDecision`, `_MemoryPressureMode` redefinition and E501 diagnostics; mypy additionally reports callable incompatibility, missing `MemoryPressureState` attributes, method-assignment errors and stale `type: ignore` comments.
- Root-cause class: integrated Backend refactor not type/lint complete.
- Ownership: BACKEND.
- Components: `src/athena/core/application.py` and directly coupled resource/memory-pressure integration.
- Required fix invariant: retain productive startup/runtime behavior while making the integrated memory-pressure/extraction/application composition statically coherent; do not suppress real type mismatches with broad ignores.
- Status: ASSIGNED.
- Targeted verification: Ruff+mypy on `src/athena/core/application.py`, focused core/resource-monitor tests, Local install smoke, then full gate.
- Last gate status: **FAIL** on #2940; same-SHA Local install smoke nevertheless PASS.

### FGATE-012 — Additional Backend typing regressions

- Priority: P0
- SHA/run evidence: `c59778dcd90b11dd8ee2176b381db0af06848725` / #2940 / mypy.
- Error excerpt: current mypy also fails in `src/athena/research/assistant.py`, `src/athena/analysis/capabilities.py`, and `src/athena/restart_scenarios.py` with optional datetime, collection-shape/union narrowing, and `Any`-return mismatches.
- Root-cause class: lint/typecheck / incomplete integrated typing contracts.
- Ownership: BACKEND.
- Components: the three modules above.
- Required fix invariant: preserve runtime contracts while making optional/collection/result types explicit and statically valid; no broad ignores.
- Status: ASSIGNED.
- Targeted verification: mypy on the affected modules plus their focused unit tests, then full gate.
- Last gate status: **FAIL** on #2940.

### FGATE-013 — UI lint/typecheck regression cluster

- Priority: P0
- SHA/run evidence: `c59778dcd90b11dd8ee2176b381db0af06848725` / #2940 / Ruff+mypy.
- Error excerpt: current Ruff/mypy failures span `src/athena/ui/assistant_shell.py`, `persistence.py`, `main_window.py`, `settings_panel.py`, `rich_chat.py`, `thumbnail_grid.py` and coupled UI tests; diagnostics include invalid Signal.connect callable typing, wrong keyword/tuple shapes, missing attributes/methods, optional-widget access, import/order/complexity and line-length issues.
- Root-cause class: lint/typecheck / integrated UI refactor not gate-clean.
- Ownership: UI.
- Components: affected UI modules and their owned tests.
- Required fix invariant: preserve current UI behavior and lifecycle safety while restoring Ruff/mypy correctness; do not weaken tests or hide invalid Qt/object contracts with broad ignores.
- Status: ASSIGNED.
- Targeted verification: Ruff+mypy on affected UI modules/tests plus focused UI unit tests, then full gate.
- Last gate status: **FAIL** on #2940.

## Verified on candidate SHA

### FGATE-001 — Productive Core extraction composition

- Priority: P0
- Historical failure: missing required `chat` dependency when constructing `ChatKnowledgeExtractionService`.
- Ownership: BACKEND.
- Fix invariant: productive `AthenaApplication` must pass its live `ChatService`; no test bypass.
- Status: VERIFIED.
- Same-SHA verification: run #2940 `Local install smoke` **PASS** on `c59778dcd90b11dd8ee2176b381db0af06848725` using `athena-local-smoke --restart-cycles 1`.

### FGATE-006 — Quality workflow import ordering

- Priority: P1
- Ownership: QUALITY.
- Last known fix: `008647cf4e20617c70ff8f9918b3d53632c99b62`.
- Status: VERIFIED.
- Same-SHA verification: #2940 Ruff ran across `src tests scripts`; no diagnostic was reported for `tests/unit/test_quality_workflow_contract.py`.

### FGATE-007 — Post-refactor durable filesystem identity lane

- Priority: P1
- Ownership: QUALITY.
- Fix invariant: durable-filesystem identity regressions execute independently of the UI/full-suite path.
- Status: VERIFIED.
- Same-SHA verification: run #2940 `Linux storage regressions` **PASS**. The workflow explicitly includes `tests/unit/test_durable_fs.py` and `tests/unit/test_durable_fs_parent_identity.py` in that Linux job.

## Superseded / stale recovery entries

### FGATE-009 — Previously unclassified central Quality failure

- Ownership: QUALITY.
- Status: STALE.
- Reason: #2940 decoded the central failure into concrete Ruff, mypy and pytest blockers; it is no longer an unclassified CI/harness problem.
- Superseded by: FGATE-003, FGATE-004, FGATE-005, FGATE-010, FGATE-011, FGATE-012 and FGATE-013.

## Coordination rules currently applied

- Product implementation remains with BACKEND/UI/SECURITY/FEATURE owners; QUALITY performs integrative verification.
- `MIXED` slices use explicit primary/secondary/verification roles and stable owner-specific sub-slices.
- `docs/agent_coordination/coordination_conflicts.md` is the conflict SSOT.
- `CONFLICT-002` is an escalated product-policy decision but is not currently a Full-Gate blocker.
- No historical error log is rewritten merely to normalize legacy ownership labels.
- No product implementation was changed during #2940 classification.

## Recovery next action

1. Product owners fix current P0 slices without QUALITY duplicating their implementation: UI first isolates FGATE-010 and UI lint/type errors; BACKEND resolves FGATE-003/004/005/011/012.
2. QUALITY verifies each targeted fix on the new integrated post-UI candidate HEAD.
3. For FGATE-008, add/execute deterministic native-Windows parent-identity coverage before verification; current Windows PASS alone is insufficient.
4. Re-run every required job on one exact SHA.
5. Declare GREEN only when `Python 3.12 quality`, `Linux storage regressions`, `Windows path safety`, and `Local install smoke` all pass on that same SHA and the central sub-checks Spec/Ruff/mypy/pytest are all green.
