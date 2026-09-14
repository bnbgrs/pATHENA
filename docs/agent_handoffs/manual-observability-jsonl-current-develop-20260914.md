# Manual Observability JSONL diagnostics — current Develop — 2026-09-14

Base: `develop/pathena-next@42614da4d235c2613b7a683d357a5af17a271817`
Branch: `manual/observability-jsonl-current-develop-20260914`
Supersedes integration use of old draft #187; the old branch remains provenance only.

## Purpose

Reconstruct the already-reviewed Observability JSONL primitive on the post-#200 Develop line without entering Backend/WAL, Source/OCR, Spec/Core/Knowledge, UI/PALLAS, Security, backup, or packaging ownership.

This slice adds an opt-in persistent JSONL sink only. It deliberately does **not** wire the sink into `AthenaApplication` or any runtime layout, so application startup behavior and existing console logging remain unchanged.

## Product behavior

- `configure_jsonl_logging()` uses the standard-library rotating file handler;
- one privacy-preserving JSON object per line through the already-qualified shared `JsonFormatter`;
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
- changed path or rotation policy replaces the previous owned file handler deterministically;
- file configuration lowers the root threshold when necessary so a more-verbose file level can flow in the supported startup order.

## Files

Exactly four new files relative to current Develop:

- `src/athena/observability/jsonl.py`
- `tests/unit/test_observability_jsonl.py`
- `tests/unit/test_observability_jsonl_retention.py`
- this handoff

No pre-existing product file is changed.

## Regression contract

Coverage includes:

- idempotent handler ownership;
- shared secret and semantic-payload redaction in persisted JSONL;
- valid JSON for every retained line;
- bounded rotation;
- deterministic removal of backups outside a reduced retention window;
- literal sibling matching for metacharacter-containing filenames;
- preservation of unrelated siblings;
- fail-closed non-file stale backup slots;
- deterministic handler replacement when file path or rotation policy changes;
- fail-closed invalid rotation bounds;
- fail-closed missing parent and non-`Path` input.

## Deliberate runtime boundary

This does **not** claim runtime persistence is enabled.

Current `AthenaApplication.start()` performs canonical database read-only integrity preflight before `StorageBootstrapService.start()` is allowed to create or probe runtime directories. `RuntimeLayoutService`, reached through storage bootstrap, owns creation/validation of `RuntimePaths.log_root`.

Do not call `configure_jsonl_logging()` beside the existing early `configure_logging()` call. A later runtime-wiring slice must preserve this ordering:

1. configure console diagnostics;
2. complete the read-only database integrity preflight;
3. establish the safe runtime layout through the existing storage lifecycle;
4. only then attach JSONL at an application-owned path such as `paths.log_root / "athena.jsonl"`.

Startup failures before step 4 remain console-only.

## Shared root-level policy still required before production wiring

The current console `configure_logging()` resets the root logger level whenever Console is reconfigured. The JSONL primitive can lower that threshold for a more-verbose file handler, which is correct for the current one-way startup order. A later Console reconfiguration could raise the root threshold again and suppress records that JSONL still needs.

Before persistent JSONL is enabled in production, Console and JSONL configuration must therefore gain one shared deterministic root-level policy: after either ATHENA-owned handler changes, the root threshold must equal the minimum level required by all active ATHENA-owned handlers. Add regressions for both configuration orders and for raising/lowering either handler level. Do not solve this by writing before database preflight or by forcing both outputs to the same level.

Cross-layer request/job/model-run correlation remains a separate Observability slice.

## Integration rule

Fresh exact-head canonical ATHENA Quality is mandatory. This candidate was reconstructed from current Develop rather than rebasing the stale #187 branch so its qualification can be attributed to the exact post-#200 tree. Keep draft until both this exact head and post-#200 Develop are terminal green. If Develop advances again first, reconstruct/requalify this bounded four-file slice rather than treating stale green evidence as merge authority.
