# Recovery Derived-State rebuild CLI handoff — 2026-10-02

## Canonical coordinates

- Integration target: `develop/pathena-next`
- Exact base inspected before work: `467ef434236c320e4afe9d21a39c20a4a2b75728`
- Base already includes merged PR #329 (Core/API chat cancellation).
- Working branch: `fix/recovery-derived-rebuild-cli-20261002-sol`
- Draft PR: #366 — Recovery: expose guarded derived-state rebuild commands
- First rebuild implementation: `a5688802e6b33d85c79dbf046a0d34c08c97a115`
- Initial rebuild tests: `83cba4cc539c0e9f7dc611cbc42ffdd962801a76`
- Canonical diagnostic truth fix: `3a218b5d1fbb698049b07be187d10d06b6515d64`
- Import formatting correction: `6f30c67cae3e1faaef1292305e6dc1e57ddbe43a`
- Derived diagnostic truth fix: `d8e490c57ba8cb1fb733a9b06ab42cbbe09f981e`
- Rebuild invariant-boundary fix: `f9cbf13c9958fc181620091b8a0d04b6b25fc6eb`
- Rebuild invariant tests: `63c464286c173f4c390c093c572531632740d08b`
- Derived diagnostic truth tests: `c2308d6dd21cb789fff366fea43959765f374cb8`
- Lazy Backup import: `6c4fa9407d62903edb4687343a4f0f66a4995cbf`
- Recovery CLI import-boundary test: `bdaab08605b5603256d83193cda94ff65fe0a2e1`

## Ausgangslage

Beta 22 requires Recovery to provide an explicit “Index neu aufbauen” path while keeping the emergency entrypoint independent from the normal Core, models, plugins, Internet, News and background services.

The repository already contained four guarded repair primitives in `DerivedRecoveryService`:

- canonical FTS rebuild;
- archive FTS rebuild;
- canonical HNSW rebuild from persisted vectors;
- archive HNSW rebuild from persisted vectors.

But `athena-recover` exposed only `diagnose` and `restore-path`. A user could receive a truthful rebuild-required diagnosis but had no supported Recovery command to execute the already-implemented safe repair.

A second review found two truthfulness defects in Recovery error classification and one unnecessary dependency expansion in the CLI import path.

## Root causes

1. **Missing final Recovery integration boundary.** Safe Derived repair services existed, but the minimal operator CLI never wired them.
2. **Canonical false certainty.** `RecoveryDiagnosticsService.inspect()` caught every canonical-preflight `Exception` and reported it as damaged/incompatible user data.
3. **Derived false certainty.** Every unexpected Derived inspection exception was presented as a Derived-State problem even when the failure could be an internal diagnostics defect.
4. **Rebuild exception masking.** `run_rebuild_derived()` caught generic `ValueError`, which could hide an invariant/programming failure as an expected recovery error.
5. **Unnecessary Recovery dependencies.** Importing `athena.recovery_cli` eagerly imported `BackupService` and its broad dependency graph even for `diagnose` and Derived rebuilds.

## Changes

### `src/athena/recovery_cli.py`

Adds:

`athena-recover rebuild-derived <target>`

Supported explicit targets:

- `canonical-fts`
- `archive-fts`
- `canonical-hnsw`
- `archive-hnsw`

Behavior:

- delegates to the existing guarded `DerivedRecoveryService` methods;
- runs one target at a time;
- reports real returned counts:
  - FTS: `documents_indexed`
  - HNSW: `model_indexes_rebuilt`;
- does not start `AthenaApplication`;
- does not invoke a model/provider for these rebuilds;
- maps `DerivedRecoveryRequiredError` to exit 4;
- maps expected `DerivedRecoveryError`, configuration and OS failures to exit 2;
- does **not** catch generic `ValueError` or `RuntimeError` invariant/programming defects;
- rejects unsupported target strings before runtime settings are loaded;
- imports `BackupService` only inside `run_restore_path()`, so diagnose/rebuild imports do not pull in the Backup service graph.

### `src/athena/core/recovery_diagnostics.py`

Canonical preflight:

- `DatabaseRecoveryRequiredError` keeps the established `canonical.database_invalid_or_incompatible` classification;
- unexpected exceptions become `canonical.database_inspection_failed`;
- canonical integrity is not claimed;
- normal Core start remains blocked;
- action is `investigate-recovery-diagnostics`;
- exception text is not exposed.

Derived inspection:

- `DerivedRecoveryRequiredError` keeps `derived.inspection_failed` / `investigate-derived-state`;
- unexpected exceptions become `recovery.diagnostics_internal_error` on layer `recovery`;
- canonical health remains truthfully recorded as already confirmed;
- normal Core start remains blocked;
- exception text is not exposed.

## Tests added/extended

### `tests/unit/test_recovery_derived_cli.py`

- exact dispatch for all four rebuild targets;
- truthful count labels;
- exit 4 for broader Recovery requirement;
- exit 2 for expected rebuild failure;
- unexpected `RuntimeError` **and** `ValueError` propagate;
- unsupported targets fail before settings/runtime loading;
- parser exposes only the bounded target set.

### `tests/unit/test_recovery_diagnostics_truth.py`

- known canonical Recovery errors preserve the existing specific classification;
- unexpected canonical inspection failure is not labeled database corruption;
- canonical internal exception text is not leaked;
- known Derived Recovery requirement remains a Derived-State recovery classification;
- unexpected Derived inspection failure is classified as a Recovery diagnostics defect;
- Derived internal exception text is not leaked.

### `tests/unit/test_recovery_cli_import_boundaries.py`

Fresh-interpreter regression asserts that importing and building the Recovery CLI parser does not eagerly load:

- `athena.backup.service`
- `athena.core.application`
- LM Studio model adapters
- News service
- Security service

## Verhalten danach

Supported operator flow:

1. `athena-recover diagnose`
2. inspect the structured Recovery result;
3. when the reported condition matches an existing safe repair, run exactly one:
   - `athena-recover rebuild-derived canonical-fts`
   - `athena-recover rebuild-derived archive-fts`
   - `athena-recover rebuild-derived canonical-hnsw`
   - `athena-recover rebuild-derived archive-hnsw`
4. diagnose again before normal startup.

All integrity/state prerequisites remain owned by `DerivedRecoveryService`; the CLI does not bypass them.

## Files changed

- `src/athena/recovery_cli.py`
- `src/athena/core/recovery_diagnostics.py`
- `tests/unit/test_recovery_derived_cli.py`
- `tests/unit/test_recovery_diagnostics_truth.py`
- `tests/unit/test_recovery_cli_import_boundaries.py`
- `docs/agent_handoffs/recovery-derived-rebuild-cli-20261002-sol.md`

## Validation

Local checkout/test execution is unavailable in this agent container because `github.com` DNS resolution fails. **No local PASS is claimed.**

Completed static/contract review:

- branch remains based on exact current Develop with no behind commits at last compare;
- all changed Python files re-read from GitHub after edits;
- no accidental literal `\\n` sequences remain in changed Python files;
- no changed Python line exceeds the repository 100-character Ruff line limit;
- existing `DerivedRecoveryService` tests already prove FTS rebuilds preserve authoritative state and HNSW rebuilds use persisted vectors without provider calls.

Executable validation source is repository CI. Latest exact-head Quality run must cover:

- specification validator;
- Ruff;
- mypy;
- complete canonical pytest suite;
- Linux storage regressions;
- local install smoke;
- Windows path/restart/package guards.

Do not merge #366 until the final PR head is green.

## Known remaining gaps

- No automatic canonical DB repair is added.
- Missing/stale archive SourceChunks remain a broader recovery condition when the existing service says so; no data is fabricated/deleted to make a rebuild appear successful.
- Embedding regeneration remains a normal model-backed workflow; Recovery HNSW rebuild uses only already-persisted valid vectors.
- Recovery GUI still exposes diagnosis only; wiring mutation actions into the desktop should be a separate reviewed slice because the current packaged-worker routing has active parallel work.
- Diagnostics export, blob rehydration and storage rebinding remain separate Beta 22 work.

## Dependencies / conflict risk

At branch start, no active open PR owned `src/athena/recovery_cli.py` or `src/athena/core/recovery_diagnostics.py`.

This slice intentionally avoids active Chat/UI, LM Studio, Settings, Knowledge, Jobs, Sources, Backup, Storage replication, Research comparison and Windows packaged-helper branches.

Potential future overlap:

- Recovery UI workers should consume this command/diagnostic contract rather than create a second repair path.
- Packaged-worker work should be reconciled before exposing these mutation commands in the frozen desktop.

## Next actions

1. Qualify the final exact PR #366 head in repository CI; fix only evidenced failures.
2. If green, integrate history-preserving onto fresh `develop/pathena-next` and rerun required integration gates.
3. Next independent Recovery slice should be diagnostics export or a reviewed Recovery UI action after packaged-worker routing stabilizes.
