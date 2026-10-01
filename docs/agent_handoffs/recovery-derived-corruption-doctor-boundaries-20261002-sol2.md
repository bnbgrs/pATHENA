# Recovery / Doctor Boundary Handoff — 2026-10-02

## Ausgangslage

- Repository: `bnbgrs/pATHENA`
- Integration target: `develop/pathena-next`
- Branch creation base: `67174198e1494fd4c8678aad60756c39ef5c160b`
- Current PR base observed after #329 merged: `467ef434236c320e4afe9d21a39c20a4a2b75728`
- Branch: `fix/recovery-derived-corruption-doctor-boundaries-20261002-sol2`
- Code head before this handoff: `6075213b156badbc77cd020be748c54d3bd56adf`
- Active Chat, LM Studio, Knowledge, Jobs, Research, Sources, Backup, Settings, Storage, Obsidian, PALLAS, Update, Security and Windows-helper PRs were inspected before selecting this work. This slice intentionally avoids their file sets.
- Local checkout/test execution is unavailable in this environment because `github.com` DNS resolution fails. No local PASS or manual Desktop/UI validation is claimed.

## Root Cause A — malformed Derived embedding storage escalated to full Recovery

`DerivedRecoveryService` treated persisted embedding fields as if Python annotations/SQLite column affinity guaranteed runtime types. Canonical and archive inspection used coercive `int(...)` and `bytes(...)` calls on persisted values.

SQLite can retain a different storage class than the declared affinity. In particular, a TEXT value in a BLOB-affinity embedding column can survive persistence and then make `bytes(value)` raise `TypeError`.

For canonical embeddings that exception escaped `DerivedRecoveryService.inspect()`; `RecoveryDiagnosticsService` then converted the entire derived-inspection failure into `recovery-required` and set `normal_core_start_allowed=False`.

For archive embeddings, the same class of failure could make the whole derived archive store appear invalid even when the corruption was limited to reconstructible embedding state.

This conflicts with Beta Recovery chapter 22: derived embeddings are reconstructible and should degrade to rebuild-required after canonical integrity is established, not unnecessarily block normal Core startup.

## Änderungen A

- Added strict persisted integer and BLOB readers that never coerce another SQLite storage class.
- Canonical embedding-state metadata now fails closed into a rebuild-required `DerivedEmbeddingReport`.
- Canonical embedding vectors, entity/revision IDs and content hashes are type-validated before use.
- Archive embedding-state metadata and generation values now fail closed into rebuild-required state.
- Archive vector/chunk/hash fields are type-validated before use.
- Malformed embedding state no longer throws through the whole derived diagnosis.
- Existing HNSW rebuild behavior remains gated by `embeddings_current`; malformed state therefore cannot become a rebuild-from-corrupt-vectors candidate.

## Root Cause B — Doctor path checks disagreed with Windows storage startup

`athena-doctor` used `Path.is_symlink()` for runtime and optional storage roots.

The actual canonical storage startup already uses the shared `is_link_boundary()` predicate and checks ancestors, covering Windows junction/reparse points as well as symbolic links.

The result was a false readiness path: Doctor could report a redirected Windows runtime path as writable/PASS even though the real startup would reject the same path.

## Änderungen B

- Doctor now uses the shared `is_link_boundary()` contract.
- Runtime-root checks walk the selected root and all ancestors before creating a directory or write-probing it.
- Runtime-root boundaries are rechecked after directory creation before the temporary write probe.
- Optional archive/backup/projection roots also detect symbolic-link/reparse boundaries before write probes.
- Existing behavior for normal directories and unavailable optional roots is unchanged.

## Dateien

- `src/athena/core/derived_recovery.py`
- `src/athena/doctor.py`
- `tests/unit/test_derived_recovery.py`
- `tests/unit/test_doctor_runtime_boundary_validation.py`
- `tests/unit/test_doctor_storage_roots.py`
- this handoff

## Regression coverage

### Derived Recovery

New test persists a same-length TEXT value into both canonical and archive embedding `vector_blob` columns after real embedding publication, verifies SQLite reports the storage class as `text`, and then verifies:

- Derived inspection does not raise.
- Both embedding projections are `persisted_valid=False`.
- Both are marked `embedding_rebuild_required=True`.
- Recovery diagnostics report `degraded-derived`.
- Canonical integrity remains confirmed.
- Normal Core start remains allowed.
- Canonical and archive embedding rebuild actions are explicitly reported.

### Doctor

New tests simulate reparse-point boundaries using the shared predicate and verify:

- a runtime-root ancestor boundary returns FAIL before directory creation/write probing;
- an optional storage-root boundary returns WARN before write probing;
- diagnostics identify the redirect boundary rather than claiming writability.

## Validierung

Completed in this run:

- exact branch diff checked against base;
- only five intended product/test files changed before this handoff;
- branch was 11 commits ahead / 0 behind the exact base before this handoff;
- all five changed Python files were statically checked for >100-character lines; none found;
- source was re-read after each write;
- schema verification confirmed canonical `search_embeddings.vector_blob` is BLOB-affinity with a length check rather than a STRICT storage-class constraint, and archive `vector_blob` is likewise non-STRICT, so the TEXT-in-BLOB regression models a real SQLite corruption boundary;
- Develop advanced during the run via Chat cancellation #329; its changed file set is disjoint from this slice and PR #379 remained mergeable without rebasing or force-pushing.

Not available in this execution environment:

- local pytest;
- local Ruff/mypy;
- local Windows execution;
- manual Desktop/UI launch.

GitHub exact-head CI is therefore the executable validation source. Keep the PR draft until current-head Quality and relevant focused checks are terminal and triaged.

## Verhalten danach

- Reconstructible embedding corruption remains fail-closed but is represented as a truthful Derived rebuild requirement instead of an unrelated full-Core recovery requirement.
- Doctor readiness is aligned with the same Windows link/junction/reparse boundary used by actual Storage startup.

## Bekannte Restprobleme

- A successful repository/unit gate is not a substitute for native Windows junction acceptance. A Windows runner should exercise a real junction/reparse root.
- The new regression deliberately targets embedding BLOB runtime type corruption. Other reconstructible Derived fields should continue to be audited for coercive SQLite reads.
- No UI files were changed; there is no manual UI validation claim.

## Abhängigkeiten / Konfliktrisiko

Current active PRs inspected during this run do not own these Recovery/Doctor files. The slice is intentionally disjoint from active Backup #345, Desktop helper #353, LM Studio #334, Research #357/#358, Knowledge #343, Jobs #344/#351, Sources #348/#359, Settings #333, Security #354, Storage #325 and Chat cancellation/branching work.

Conflict risk is low unless another bot begins modifying `derived_recovery.py` or `doctor.py` after this handoff.

## Nächste sinnvolle Schritte

1. Read exact-head Quality/focused CI for draft PR #379; fix only failures caused by this slice.
3. Run native Windows junction/reparse acceptance when an appropriate Windows runner is available.
4. If exact-head green, integrate without pulling unrelated active bot branches into this slice.
5. Continue auditing Recovery for reconstructible-state corruption paths that still escalate to `recovery-required` through generic exceptions.

## Commit / PR

- Base: `67174198e1494fd4c8678aad60756c39ef5c160b`
- Branch: `fix/recovery-derived-corruption-doctor-boundaries-20261002-sol2`
- Product/test head before handoff: `6075213b156badbc77cd020be748c54d3bd56adf`
- PR: #379
- Product/test head after final test-spacing cleanup: `613df7c3c80f033171022307d4445e4db5be26c3`
