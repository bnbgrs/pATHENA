# pATHENA Full Gate Recovery

Single source of truth for recovery of the complete required quality/CI gate on `agent/pathena`.

Canonical Ownership values: `QUALITY`, `BACKEND`, `UI`, `SECURITY`, `FEATURE`, `MIXED`, `EXTERNAL`.
Status values: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `VERIFIED`, `STALE`, `BLOCKED`.

## Current recovery baseline

- Candidate HEAD: `197a4aee545808b8e6c0d31894aa201c79bab2f1`.
- Required GitHub Actions run: `#2972` / `32724974239` on that exact SHA.
- Run conclusion: **FAILURE**. Recovery state remains **P0 / NOT GREEN**.
- Same-SHA required jobs:
  - `Python 3.12 quality` / job `97424104627`: **FAIL** at `Run ATHENA quality gate`.
  - `Linux storage regressions` / job `97424104947`: **PASS**.
  - `Windows path safety` / job `97424104886`: **PASS**.
  - `Local install smoke` / job `97424104708`: **PASS**.
- Exact current central sub-check diagnostics are not available through the connected GitHub job-log surface in this recovery run. The only supported current statement is that the central `Run ATHENA quality gate` step failed. Historical Ruff/mypy/pytest details from #2940 or #2967 are therefore **not transferred** to #2972.
- Predecessor run #2967 is useful only as change-history evidence: its recorded Ruff/pytest state must not be treated as a #2972 PASS.

## Active blockers

### FGATE-014 — Current central quality failure requires exact diagnostic evidence

- Priority: P0
- SHA/run/job/step: `197a4aee545808b8e6c0d31894aa201c79bab2f1` / #2972 / `97424104627` / `Run ATHENA quality gate`.
- Error excerpt: the step conclusion is `failure`; raw current sub-check diagnostics are not exposed by the available connector surface in this run.
- Reproduction: exact checkout of `197a4aee545808b8e6c0d31894aa201c79bab2f1`, then execute the repository's complete quality runner in keep-going mode, or decode the complete #2972 job log with checkout provenance.
- Root-cause class: verification evidence / unresolved central sub-check failure.
- Ownership: QUALITY.
- Components: central quality-run evidence and classification only; no product module is assigned until current diagnostics identify one.
- Required fix invariant: obtain exact-SHA diagnostic provenance before assigning a product owner or changing product/test code; do not infer a #2972 failure from #2940/#2967 diagnostics.
- Related conflicts: `CONFLICT-004`, `CONFLICT-005`.
- Status: IN_PROGRESS.
- Targeted verification: decode or reproduce the exact #2972 central runner, identify the first one or two current primary blockers, then assign only those blockers using canonical ownership.
- Last gate status: **FAIL** on #2972; the other three required jobs are same-SHA PASS.

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
- Candidate-SHA evidence: #2972 `Windows path safety` is PASS, but that general lane PASS does not by itself prove the still-open BE-038/SEC invariant is closed.
- Targeted verification: deterministic native-Windows parent-replacement/reparse regression plus Windows storage lane after implementation.

## Verified on current candidate SHA

### FGATE-001 — Productive Core extraction composition

- Priority: P0
- Historical failure: missing required `chat` dependency when constructing `ChatKnowledgeExtractionService`.
- Ownership: BACKEND.
- Fix invariant: productive `AthenaApplication` must pass its live `ChatService`; no test bypass.
- Status: VERIFIED.
- Same-SHA verification: #2972 `Local install smoke` / job `97424104708` **PASS** on `197a4aee545808b8e6c0d31894aa201c79bab2f1`.

### FGATE-007 — Independent Linux durable-filesystem/storage regression lane

- Priority: P1
- Ownership: QUALITY.
- Fix invariant: storage regressions execute independently of the central UI/full-suite path.
- Status: VERIFIED.
- Same-SHA verification: #2972 `Linux storage regressions` / job `97424104947` **PASS** on `197a4aee545808b8e6c0d31894aa201c79bab2f1`.

## Fixed pending current-candidate verification

### FGATE-006 — Quality workflow import ordering

- Priority: P1
- Ownership: QUALITY.
- Last known fix: `008647cf4e20617c70ff8f9918b3d53632c99b62`.
- Status: FIXED_PENDING_VERIFY.
- Reason: the central #2972 job is red and its current Ruff sub-check detail is unavailable in this recovery run, so the earlier #2940 verification is not transferred to this SHA.

## Superseded / stale recovery entries

### FGATE-002 — Historical PALLAS native crash

- Ownership: UI.
- Status: STALE.
- Reason: the historic failure assignment is not reproducible from the cited repository paths; `CONFLICT-004` established that the old evidence referenced non-existent `src/athena/ui/*` paths while the productive UI tree is `src/athena/desktop/`. Any new current UI failure must receive a new exact-SHA FGATE entry rather than reuse this stale stack.

### FGATE-003 — #2940 Research model typing assignment

- Ownership: BACKEND.
- Status: STALE.
- Reason: line-specific #2940 diagnostics are not current #2972 evidence. Backend queue BE-048 explicitly treats the historical Research-model diagnostic as evidence-blocked until QUALITY supplies current provenance. Superseded for current recovery by FGATE-014.

### FGATE-004 — #2940 Research idempotency typing assignment

- Ownership: BACKEND.
- Status: STALE.
- Reason: the historical code/diagnostic shape no longer matches current source; Backend independently completed BE-049. No #2972 idempotency diagnostic is asserted. Superseded for current recovery by FGATE-014.

### FGATE-005 — #2940 Semantic persisted-integer typing assignment

- Ownership: BACKEND.
- Status: STALE.
- Reason: Backend independently completed BE-047 with exact-int persisted-state validation; the #2940 diagnostic is not transferred to #2972. Superseded for current recovery by FGATE-014.

### FGATE-009 — Previously unclassified #2940 central failure

- Ownership: QUALITY.
- Status: STALE.
- Reason: historical #2940 evidence has been replaced by exact current run #2972. Current classification is FGATE-014.

### FGATE-010 — #2940 rich-chat image-preview Qt crash assignment

- Ownership: UI.
- Status: STALE.
- Reason: `CONFLICT-004` established that its cited `src/athena/ui/*` stack does not map to the repository tree on the cited refs. Do not fabricate a UI fix. A real current UI crash, if present in #2972 diagnostics, requires a new exact-SHA entry against existing `src/athena/desktop/*` paths.

### FGATE-011 — #2940 Core application lint/typecheck cluster

- Ownership: BACKEND.
- Status: STALE.
- Reason: the #2940 line-level cluster is not current #2972 evidence. Local install smoke is same-SHA PASS, which proves productive startup for #2972 but does not prove central lint/typecheck PASS. Any current Backend diagnostic must be re-created from FGATE-014 evidence.

### FGATE-012 — #2940 additional Backend typing cluster

- Ownership: BACKEND.
- Status: STALE.
- Reason: historical diagnostics are not transferred across candidate SHAs. Any current failure must be re-created from exact #2972 diagnostics.

### FGATE-013 — #2940 UI lint/typecheck cluster

- Ownership: UI.
- Status: STALE.
- Reason: `CONFLICT-004` established that the assigned `src/athena/ui/*` paths do not exist on the cited/current repository refs. A current UI diagnostic must reference real `src/athena/desktop/*` paths and exact #2972 evidence.

## Conflict arbitration state

- `CONFLICT-001`: RESOLVED ownership arbitration; FGATE-008 remains active MIXED work.
- `CONFLICT-002`: ESCALATED product-policy decision; **USER DECISION REQUIRED**, but not a current Full-Gate blocker.
- `CONFLICT-003`: RESOLVED ownership arbitration; not promoted to a current gate blocker.
- `CONFLICT-004`: technical resolution determined by this rebaseline — stale #2940 UI assignments are no longer active; conflict SSOT still requires its own status update when CI state next permits a coordination-file mutation.
- `CONFLICT-005`: technical resolution determined by this rebaseline — stale #2940 Backend assignments are no longer active; current central failure remains QUALITY-owned evidence classification FGATE-014 until exact diagnostics exist. Conflict SSOT still requires its own status update when CI state next permits a coordination-file mutation.

## Coordination rules currently applied

- Product implementation remains with BACKEND/UI/SECURITY/FEATURE owners; QUALITY performs integrative verification.
- `MIXED` slices use explicit primary/secondary/verification roles and stable owner-specific sub-slices.
- `docs/agent_coordination/coordination_conflicts.md` is the conflict SSOT.
- Historical error logs are not rewritten merely to normalize legacy ownership labels.
- No product implementation or tests were changed during the #2972 rebaseline.

## Recovery next action

1. Obtain exact #2972 central quality diagnostics or reproduce the complete quality runner on exact SHA `197a4aee545808b8e6c0d31894aa201c79bab2f1`.
2. Classify only the first one or two current primary blockers from those diagnostics and assign them canonically; do not reactivate stale #2940 assignments without current evidence.
3. On the next mutation-safe state, update `coordination_conflicts.md` to mark CONFLICT-004/005 RESOLVED with this rebaseline as evidence.
4. Re-run every required job on one exact integrated SHA after the current central blocker is fixed.
5. Declare GREEN only when `Python 3.12 quality`, `Linux storage regressions`, `Windows path safety`, and `Local install smoke` all pass on that same SHA and the central quality runner itself is successful.
