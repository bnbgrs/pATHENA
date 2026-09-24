# Independent Handoff — FG-021 Durable Job Dependencies

Status: IMPLEMENTED_PENDING_VERIFY

## Ownership and integration boundary

- Repository: `bnbgrs/pATHENA`
- Independent branch: `independent/fg021-job-dependencies-20260904`
- Draft PR: `#67` targeting `develop/pathena-next`
- Develop baseline: `e51e805266b625c008812ae5ab79435655ff1ca5`
- Last code/test head before this documentation-only handoff: `06f78ce13280b35b5a51eeb5ca09b38ff55609ac`
- Main was not modified.
- Develop was not modified.
- Do not auto-merge. Integrate only the current PR head after the canonical `ATHENA Quality Gate` is green on that exact head.

## Contract implemented

FG-021 adds a durable, restart-safe job dependency graph while preserving the existing durable job state machine and safety semantics.

### Schema v41

- `SCHEMA_VERSION = 41`
- migration id: `0041_job_dependency_graph`
- `job_dependencies(job_id, depends_on_job_id, created_at_us)`
- `job_parent_links(job_id, parent_job_id, completion_policy, cancellation_policy, created_at_us)`
- foreign keys point to canonical `jobs` rows
- self edges are rejected
- production migration remains fail-closed; it intentionally does not use `CREATE TABLE IF NOT EXISTS`
- startup verifies v41 metadata, required tables/columns and `foreign_key_check`

### Dependency semantics

- incomplete dependencies put a queued job into durable `waiting` state with `blocked_reason=dependency`
- completion of dependencies reconciles waiting jobs back to `queued`
- dependency edges survive restart
- dependency mutation is limited to editable job states
- direct dependency count and graph traversal are bounded
- cycles, dangling edges and graph corruption fail closed

### Parent/child semantics

- explicit parent links support `independent` and `require_success` parent-completion policy
- child cancellation supports `independent` and explicit `cascade`
- parent cancellation plus all explicit cascade descendants execute in one SQLite write transaction
- unrelated children are not cancelled

### Transactionality

Job creation and initial graph configuration execute in one SQLite write transaction. A graph-policy failure therefore cannot leave an orphan job row behind.

### Priority inheritance

- a runnable prerequisite may inherit scheduling urgency from jobs blocked on it
- inheritance is transitive and bounded
- inherited urgency is capped at `INTERACTIVE` / P1; `DATA_SAFETY` / P0 is never donated
- the persisted base priority is not mutated
- leasing re-reads the canonical job row, so ResourceManager/P0 admission semantics still see the persisted base priority
- inherited-priority prerequisites are expanded into the scheduler candidate set before the final candidate limit, preventing a low base-priority prerequisite from being truncated out under a tight limit

## Files intentionally changed

Production:

- `src/athena/jobs/dependency_graph.py`
- `src/athena/jobs/service.py`
- `src/athena/storage/job_dependency_graph_schema.py`
- `src/athena/storage/schema.py`
- `src/athena/storage/schema_contract.py`

Primary focused regression coverage:

- `tests/unit/test_job_dependency_graph.py`

Schema-version fixture maintenance required by v41:

- `tests/unit/test_archive_replication.py`
- `tests/unit/test_backup_retention.py`
- `tests/unit/test_deletion_ledger.py`
- `tests/unit/test_grounded_response_receipt.py`
- `tests/unit/test_knowledge_schema.py`
- `tests/unit/test_news_audit.py`
- `tests/unit/test_operational_error_physical_cleanup.py`
- `tests/unit/test_protected_content.py`
- `tests/unit/test_protected_source_blob.py`
- `tests/unit/test_protected_source_semantic_schema.py`
- `tests/unit/test_protected_source_transition.py`

The fixture changes remove v41 additive tables when a test deliberately reconstructs a historical schema boundary from a freshly-created current database and update assertions that intentionally mean “latest migration”. They do not relax production migration behavior.

## Review findings fixed during validation

1. The first implementation caused excessive churn in `src/athena/storage/schema.py`; it was reset to the Develop baseline and reduced to the small v41 integration hooks only.
2. Canonical Ruff failures caused by that import churn were removed.
3. Canonical mypy reported one real `sqlite3.Row` typing error in `JobDependencyGraph._require_job`; this is fixed with an explicit typed cast, not an ignore.
4. `JobDependencyGraph.__init__` initially accessed `repository.database` eagerly, breaking existing fail-before-write validation tests that intentionally use storage-free fake repositories. Database resolution is now lazy, preserving validation-before-storage behavior.
5. Job row creation and graph configuration were initially separate transactions; they are now atomic.
6. Parent cancellation and cascade were initially separate transitions; they are now atomic.
7. Initial scheduler candidate limiting could hide inherited-priority prerequisites; candidate expansion now occurs before final limiting.
8. Historical migration fixtures initially retained new v41 tables while declaring older schema metadata, causing expected fail-closed `table already exists` errors. Fixtures now remove v41 additive state instead of weakening the production migration.

## Validation lineage

- Old canonical run `33905667608` on ancestor `6e48abf...` failed and produced the diagnostics used for root-cause analysis.
- On subsequent code heads, canonical Ruff and mypy both reached green before fixture-only follow-up commits.
- Current state is intentionally `IMPLEMENTED_PENDING_VERIFY` until the canonical `ATHENA Quality Gate` completes successfully on the exact current PR head after this handoff commit.

## Integrator guidance

1. Verify PR #67 current head is still based on the stated Develop lineage or repeat a collision check if Develop advanced.
2. Require the canonical `ATHENA Quality Gate` to be green on the exact PR head.
3. Do not weaken v41 migration fail-closed behavior to accommodate synthetic historical fixtures.
4. Preserve P0 non-inheritance and persisted-base-priority semantics.
5. Preserve atomic create+graph and atomic cancellation-cascade behavior.
6. Merge into `develop/pathena-next` only through the normal integrator path; never merge this slice directly to `main`.
