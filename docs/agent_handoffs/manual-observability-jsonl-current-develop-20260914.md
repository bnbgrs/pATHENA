# Manual Observability JSONL diagnostics — current Develop — 2026-09-14

Base: `develop/pathena-next@42614da4d235c2613b7a683d357a5af17a271817`
Branch: `manual/observability-jsonl-current-develop-20260914`
Supersedes integration use of old draft #187; the old branch remains provenance only.

## Purpose

Reconstruct and harden the Observability JSONL primitive on the post-#200 Develop line without entering Backend/WAL, Source/OCR, Spec/Core/Knowledge, UI/PALLAS, Security, backup, or packaging ownership.

This slice adds an opt-in persistent JSONL sink only. It deliberately does **not** wire the sink into `AthenaApplication` or any runtime layout, so application startup behavior and existing console logging remain unchanged.

## Product behavior

- `configure_jsonl_logging()` uses the standard-library rotating file handler;
- one privacy-preserving JSON object per line through the already-qualified shared `JsonFormatter`;
- JSONL is attached to the `athena` logger namespace rather than Root;
- the `athena` namespace uses explicit level `1`, the lowest practical non-`NOTSET` threshold, so handler thresholds own output routing for normal/custom positive levels;
- Console may continue to own/reset the Root level without suppressing more-verbose `athena.*` records before JSONL sees them;
- Console and JSONL can therefore use different levels in either configuration order;
- any legacy Root-owned ATHENA JSONL handler is removed before the namespace-owned handler is installed;
- byte-bounded rotation and count-bounded retention;
- default 8 MiB active-file rollover threshold and 5 retained rotated files;
- numeric rotated backups outside a later-reduced retention window are removed before the new handler opens;
- unrelated sibling files are never treated as rotated backups, including when the selected log filename contains glob metacharacters such as `[`;
- unexpected non-file objects in a stale numeric backup slot fail closed instead of silently weakening retention;
- exact positive-integer validation for `max_bytes` and `backup_count`, with booleans rejected;
- strict log-level validation matching the existing console configuration contract;
- missing parent directories fail before file creation rather than silently creating filesystem structure;
- direct symbolic-link log targets and symbolic-link immediate parents fail closed;
- exactly one ATHENA-owned JSONL handler; repeated equivalent configuration is idempotent;
- changed path or rotation policy replaces the previous owned file handler deterministically.

## Files

Exactly four new files relative to current Develop:

- `src/athena/observability/jsonl.py`
- `tests/unit/test_observability_jsonl.py`
- `tests/unit/test_observability_jsonl_retention.py`
- this handoff

No pre-existing product file is changed.

## Regression contract

Coverage includes:

- idempotent namespace-owned handler ownership;
- no Root-owned JSONL handler after configuration;
- shared secret and semantic-payload redaction in persisted JSONL;
- valid JSON for every retained line;
- bounded rotation;
- deterministic removal of backups outside a reduced retention window;
- literal sibling matching for metacharacter-containing filenames;
- preservation of unrelated siblings;
- fail-closed non-file stale backup slots;
- deterministic handler replacement when file path or rotation policy changes;
- JSONL `DEBUG` remains persisted after later Console `INFO` reconfiguration;
- Console `DEBUG` can coexist with JSONL `INFO` without leaking DEBUG into the file;
- fail-closed invalid rotation bounds;
- fail-closed missing parent and non-`Path` input.

## Deliberate runtime boundary

This still does **not** claim runtime persistence is enabled.

Current `AthenaApplication.start()` performs canonical database read-only integrity preflight before `StorageBootstrapService.start()` is allowed to create or probe runtime directories. `RuntimeLayoutService`, reached through storage bootstrap, owns creation/validation of `RuntimePaths.log_root`.

Do not call `configure_jsonl_logging()` beside the existing early `configure_logging()` call. A later runtime-wiring slice must preserve this ordering:

1. configure console diagnostics;
2. complete the read-only database integrity preflight;
3. establish the safe runtime layout through the existing storage lifecycle;
4. only then attach JSONL at an application-owned path such as `paths.log_root / "athena.jsonl"`.

Startup failures before step 4 remain console-only.

The previous Root-level reconfiguration blocker from #187 is closed by namespace-owned JSONL routing. A later runtime-wiring slice no longer needs to modify the existing Console `configure_logging()` contract merely to support independent Console/JSONL levels.

Cross-layer request/job/model-run correlation remains a separate Observability slice.

## Integration rule

Fresh exact-head canonical ATHENA Quality is mandatory. This candidate was reconstructed from current Develop rather than rebasing the stale #187 branch so its qualification can be attributed to the exact post-#200 tree. Keep draft until both this exact head and post-#200 Develop are terminal green. If Develop advances again first, reconstruct/requalify this bounded four-file slice rather than treating stale green evidence as merge authority.
