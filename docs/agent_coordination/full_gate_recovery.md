# pATHENA Full Gate Recovery

Single source of truth for recovery of the complete required quality/CI gate on `agent/pathena`.

Canonical Ownership values: `QUALITY`, `BACKEND`, `UI`, `SECURITY`, `FEATURE`, `MIXED`, `EXTERNAL`.
Status values: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `VERIFIED`, `STALE`, `BLOCKED`.

## Current recovery baseline

- Candidate HEAD: `31b580609527f828b87854207bd1c33c3a4bfec6`.
- Required GitHub Actions run: `#2936` / `32684297152` on that exact SHA.
- Run conclusion: **FAILURE**. Recovery state therefore remains **P0 ACTIVE / NOT GREEN**.
- Same-SHA required jobs:
  - `Python 3.12 quality` / job `97306396000`: **FAIL** at step `Run ATHENA quality gate`.
  - `Linux storage regressions`: **PASS**.
  - `Windows path safety`: **PASS**.
  - `Local install smoke`: **PASS**.
- Historical PASS values are not transferred to this SHA. Only the three same-SHA job successes above are accepted as current evidence.
- The GitHub connector exposes the central job/failed step, but decoded log text for job `97306396000` was not retrievable in this run. The central failure is therefore tracked separately as unclassified rather than guessed.

## Active blockers

### FGATE-002 — Native Qt/PySide PALLAS crash

- Priority: P0
- Evidence: historical runs #2677 and #2771 terminated pytest with native SIGSEGV / exit `-11` in the PALLAS target-binding/page-selection path.
- Candidate-SHA evidence: current UI fix/coverage is present, but run #2936 central Quality job is red and its decoded sub-check log was unavailable; no same-SHA full-pytest PASS is claimed.
- Root-cause class: product code / native UI lifecycle or re-entrancy crash.
- Ownership: UI.
- Components: PALLAS ASCII target binding, desktop page-selection integration, presentation/lifecycle tests.
- Required fix invariant: target binding/page selection must not re-enter or access invalid Qt object state; full pytest must exit normally; tests must not be skipped or weakened.
- Status: FIXED_PENDING_VERIFY.
- Targeted verification: `tests/unit/test_pathena_pallas_target_lifecycle.py`, `tests/unit/test_pathena_command_palette_presentation.py`, then full pytest under Qt offscreen.
- Last gate status: run #2936 central Quality job FAIL; exact pytest outcome not decoded.

### FGATE-003 — Research model typing failures

- Priority: P0
- Evidence: run #2771 reported two mypy diagnostics in `src/athena/research/models.py`; Backend queue `BE-048` remains READY on the candidate generation.
- Root-cause class: lint/typecheck.
- Ownership: BACKEND.
- Components: `src/athena/research/models.py`.
- Required fix invariant: keep runtime validation semantics while making scalar narrowing and validation-loop locals type-stable.
- Status: ASSIGNED.
- Targeted verification: mypy on the module plus Research model boundary tests.
- Last gate status: run #2936 central Quality job FAIL; exact mypy outcome not decoded.

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
  - `FGATE-008-QA` — Owner: QUALITY — execute deterministic native-Windows regressions and integrative storage/full-gate verification after implementation. Status: ASSIGNED.
- Status: ASSIGNED.
- Targeted verification: deterministic native-Windows parent-replacement/reparse regression plus Windows storage lane.

### FGATE-009 — Candidate-SHA central Quality job failure

- Priority: P0
- SHA/run/job/step: `31b580609527f828b87854207bd1c33c3a4bfec6` / #2936 / `97306396000` / `Run ATHENA quality gate`.
- Evidence: required job conclusion is FAILURE while the three independent required jobs on the same SHA are PASS.
- Error excerpt: decoded job log unavailable through the connector in this run; no Ruff/mypy/pytest primary error is invented.
- Reproduction: `uv run --locked --extra dev --extra desktop python scripts/quality.py --keep-going` with `QT_QPA_PLATFORM=offscreen` on Ubuntu/Python 3.12.
- Root-cause class: unclassified central gate failure pending decoded Ruff/mypy/pytest evidence.
- Ownership: QUALITY.
- Fix invariant: isolate the first real failing sub-check/diagnostic, then reassign any product failure to its canonical owner; no check may be skipped or weakened.
- Status: IN_PROGRESS.
- Targeted verification: retrieve/decode #2936 central log or reproduce the exact command; then run the affected targeted check followed by the complete required gate.
- Last gate status: **FAIL**.

## Verified on candidate SHA

### FGATE-001 — Productive Core extraction composition

- Priority: P0
- Historical failure: missing required `chat` dependency when constructing `ChatKnowledgeExtractionService`.
- Ownership: BACKEND.
- Fix invariant: productive `AthenaApplication` must pass its live `ChatService`; no test bypass.
- Status: VERIFIED.
- Same-SHA verification: run #2936 `Local install smoke` **PASS** on `31b580609527f828b87854207bd1c33c3a4bfec6` using `athena-local-smoke --restart-cycles 1`.

### FGATE-007 — Post-refactor durable filesystem identity lane

- Priority: P1
- Ownership: QUALITY.
- Fix invariant: durable-filesystem identity regressions execute independently of the UI/full-suite path.
- Status: VERIFIED.
- Same-SHA verification: run #2936 `Linux storage regressions` **PASS**. The workflow for this SHA explicitly includes `tests/unit/test_durable_fs.py` and `tests/unit/test_durable_fs_parent_identity.py` in that required job.

## Fixed pending exact sub-check verification

### FGATE-004 — Research idempotency typing failures

- Priority: P0
- Ownership: BACKEND.
- Current code evidence: `_research_input_sequence(value: object)` explicitly rejects text-like sequences and narrows to `Sequence`; Backend `BE-049` is DONE.
- Status: FIXED_PENDING_VERIFY.
- Targeted verification: mypy on `src/athena/research/idempotency.py` plus idempotency boundary tests.

### FGATE-005 — Semantic persisted-integer typing failures

- Priority: P0
- Ownership: BACKEND.
- Current code evidence: `_persisted_int(value: object, ...)` now rejects bool/non-int values, applies range checks, and returns a statically narrowed `int`; Backend `BE-047` is DONE.
- Status: FIXED_PENDING_VERIFY.
- Targeted verification: mypy on semantic retrieval plus persisted-state numeric boundary tests.

### FGATE-006 — Quality workflow import ordering

- Priority: P1
- Ownership: QUALITY.
- Last known fix: `008647cf4e20617c70ff8f9918b3d53632c99b62`.
- Status: FIXED_PENDING_VERIFY.
- Targeted verification: Ruff on `tests/unit/test_quality_workflow_contract.py`; central #2936 log must be decoded before promotion.

## Coordination rules currently applied

- Product implementation remains with BACKEND/UI/SECURITY/FEATURE owners; QUALITY performs integrative verification.
- `MIXED` slices use explicit primary/secondary/verification roles and stable owner-specific sub-slices.
- `docs/agent_coordination/coordination_conflicts.md` is the conflict SSOT.
- `CONFLICT-002` is an escalated product-policy decision but is not currently a Full-Gate blocker.
- No historical error log is rewritten merely to normalize legacy ownership labels.

## Recovery next action

1. Preserve candidate SHA `31b580609527f828b87854207bd1c33c3a4bfec6` as the last fully job-classified integration point until a newer integrated HEAD is selected.
2. Decode or reproduce the central #2936 Quality failure and split `FGATE-009` into the first real Ruff/mypy/pytest primary blocker.
3. If the primary blocker is QUALITY-owned, fix it here; otherwise assign the stable FGATE slice to the relevant product owner and remain read-only on product code.
4. Re-run targeted verification, then all required jobs on one exact SHA.
5. Declare GREEN only when every required job on that same SHA succeeds.
