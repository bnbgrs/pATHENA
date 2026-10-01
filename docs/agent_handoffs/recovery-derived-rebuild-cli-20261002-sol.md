# Recovery Derived-State rebuild CLI handoff — 2026-10-02

## Canonical coordinates

- Integration target: `develop/pathena-next`
- Exact base inspected before work: `467ef434236c320e4afe9d21a39c20a4a2b75728`
- Base already includes merged PR #329 (Core/API chat cancellation).
- Working branch: `fix/recovery-derived-rebuild-cli-20261002-sol`
- Implementation commit: `a5688802e6b33d85c79dbf046a0d34c08c97a115`
- Focused CLI test commit: `83cba4cc539c0e9f7dc611cbc42ffdd962801a76`\n- Diagnostic truthfulness fix: `3a218b5d1fbb698049b07be187d10d06b6515d64`\n- Diagnostic truthfulness tests: `98cf02fbbd0363f15bd364239aa6042bd12b2f51`

## Ausgangslage

Beta 22 requires Recovery to offer an explicit “Index neu aufbauen” path while keeping the normal Core, model runtime, plugins and Internet out of the recovery dependency set.

Current code already had four guarded repair primitives in `DerivedRecoveryService`:

- canonical FTS rebuild;
- archive FTS rebuild;
- canonical HNSW rebuild from already persisted vectors;
- archive HNSW rebuild from already persisted vectors.

However, `athena-recover` exposed only `diagnose` and `restore-path`. A normal user/operator could diagnose a rebuild-required Derived State but could not invoke the existing safe repair primitives through the Recovery entrypoint without writing Python code.

## Root Cause

The recovery implementation was split at the final integration boundary: safe repair services existed and were tested, but the minimal CLI never wired them into an operator-facing command surface.

This was a functional gap rather than a missing algorithm. Reimplementing index repair would have duplicated already hardened code and risked divergence.

## Änderungen

`src/athena/recovery_cli.py`

- adds `athena-recover rebuild-derived <target>`;
- supported explicit targets:
  - `canonical-fts`
  - `archive-fts`
  - `canonical-hnsw`
  - `archive-hnsw`
- delegates only to the existing `DerivedRecoveryService` guarded repair methods;
- keeps each invocation one-target-at-a-time so partial repair is never hidden behind an “all succeeded” claim;
- reports the real returned count:
  - FTS: `documents_indexed`
  - HNSW: `model_indexes_rebuilt`
- preserves Recovery minimality: no `AthenaApplication` startup and no provider/model call for these rebuild paths;
- maps `DerivedRecoveryRequiredError` to exit code 4, matching the existing Recovery diagnostic “broader recovery required” contract;
- maps expected rebuild/configuration/OS failures to exit code 2;
- deliberately does not catch unexpected `RuntimeError`/programming defects, avoiding false classification as a known recovery condition;
- rejects unknown rebuild targets before runtime/settings loading.

`tests/unit/test_recovery_derived_cli.py`

- proves all four targets dispatch to exactly one intended service method;
- proves truthful count labels/output;
- proves broader recovery requirement returns 4;
- proves ordinary rebuild failure returns 2 without falsely claiming “recovery required”;
- proves unexpected implementation defects propagate;
- proves unsupported targets are rejected before runtime loading;
- proves parser exposes the four bounded targets.

## Zweiter behobener Fehler: falsche Gewissheit in Recovery-Diagnosen

### Ausgangslage / Root Cause

`RecoveryDiagnosticsService.inspect()` fing am kanonischen Preflight pauschal `Exception` ab und meldete **jede** Exception als `canonical.database_invalid_or_incompatible`.

Damit wurden auch unerwartete Implementierungs-/Diagnostikfehler semantisch als beschädigte oder inkompatible Benutzerdaten klassifiziert. Das verletzt Beta 22 „No False Certainty“ und kann einen Operator fälschlich in Richtung Restore lenken.

### Änderung

`src/athena/core/recovery_diagnostics.py`

- `DatabaseRecoveryRequiredError` behält die präzise bestehende Klassifikation `invalid-or-incompatible`;
- unerwartete Fehler werden separat als `canonical.database_inspection_failed` / `canonical_database=inspection-failed` ausgegeben;
- normaler Core-Start bleibt dabei sicher blockiert;
- Exception-Text wird nicht in den payload-freien Diagnosebericht gespiegelt.

`tests/unit/test_recovery_diagnostics_truth.py`

- bekannte Recovery-Fehler bleiben präzise klassifiziert;
- unerwartete Fehler werden nicht mehr als DB-Korruption ausgegeben;
- unerwartete interne Exception-Texte werden nicht in den Diagnosepayload geleakt.

## Verhalten danach

Operators can now move from:

`athena-recover diagnose`

to one explicit, pre-existing safe repair action without launching the normal Core:

`athena-recover rebuild-derived canonical-fts`

`athena-recover rebuild-derived archive-fts`

`athena-recover rebuild-derived canonical-hnsw`

`athena-recover rebuild-derived archive-hnsw`

The underlying service still owns all integrity and state preconditions. The CLI does not bypass or weaken those guards.

## Dateien

- `src/athena/recovery_cli.py`
- `tests/unit/test_recovery_derived_cli.py`
- `docs/agent_handoffs/recovery-derived-rebuild-cli-20261002-sol.md`

## Validierung

Local checkout/test execution is unavailable in this agent container because `github.com` DNS resolution fails. No local PASS is claimed.

Static review completed against the exact branch diff and the existing `DerivedRecoveryService` contracts.

Repository CI on the PR head is the executable validation source. Required evidence:

1. Ruff on changed source/tests;
2. mypy over production source;
3. focused `tests/unit/test_recovery_derived_cli.py`;
4. existing Derived Recovery tests;
5. full ATHENA Quality before integration.

## Bekannte Restprobleme

- This slice exposes only already-implemented Derived-State repairs. It does not add automatic canonical DB repair, blob rehydration, storage rebinding, or a Recovery GUI.
- Missing/stale archive SourceChunks remain a broader recovery condition where the existing service says so; the CLI does not fabricate or delete data to make the rebuild pass.
- Embedding regeneration still requires the normal model-backed workflow. Recovery HNSW rebuild uses only already persisted valid vectors.

## Abhängigkeiten / Konfliktrisiko

No active open PR inspected at start owned `src/athena/recovery_cli.py` or this new focused test file.

This slice deliberately avoids currently active Chat cancellation/UI, LM Studio runtime, Settings, Knowledge, Jobs, Sources, Backup, Storage replication, Research comparison and Windows packaged-helper branches.

Potential future overlap: any worker extending Recovery CLI or Recovery UI should build on this command contract rather than adding a second repair entrypoint.

## Nächste sinnvolle Schritte

1. Qualify exact PR head in repository CI and fix only evidenced failures.
2. If green, integrate onto fresh `develop/pathena-next`.
3. Next independent Recovery slice: expose a user-reviewable diagnostics export or a safe read-only Recovery UI action that consumes the existing structured report; do not combine that work into this PR unless CI reveals a direct blocker.
