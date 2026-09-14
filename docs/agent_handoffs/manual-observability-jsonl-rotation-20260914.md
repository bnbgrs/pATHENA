# Manual Observability JSONL rotation — 2026-09-14

Base: `develop/pathena-next@ba5e541f780c3b650060f8ac65085032873088a3`
Branch: `manual/observability-jsonl-rotation-20260914`

## Purpose

Continue the already-integrated Observability privacy slice without entering Backend/WAL, Source/OCR, Spec/Core/Knowledge, UI/PALLAS, Security, or packaging ownership.

This slice adds an opt-in persistent JSONL sink only. It deliberately does **not** wire the sink into `AthenaApplication` or any runtime layout yet, so application startup behavior and existing console logging remain unchanged until the primitive is independently qualified.

## Product behavior

- new `configure_jsonl_logging()` primitive using the standard-library rotating file handler;
- one privacy-preserving JSON object per line through the already-qualified shared `JsonFormatter`;
- byte-bounded rotation and count-bounded retention;
- default 8 MiB active-file rollover threshold and 5 retained rotated files;
- numeric rotated backups outside a later-reduced retention window are removed before the new handler opens;
- unrelated sibling files are never treated as rotated backups;
- unexpected non-file objects in a stale numeric backup slot fail closed instead of silently weakening retention;
- exact positive-integer validation for `max_bytes` and `backup_count`, with booleans rejected;
- strict log-level validation matching the existing console configuration contract;
- missing parent directories fail before file creation rather than silently creating filesystem structure;
- direct symbolic-link log targets and symbolic-link immediate parents fail closed;
- exactly one ATHENA-owned JSONL handler; repeated equivalent configuration is idempotent;
- changed path or rotation policy replaces the previous owned file handler deterministically;
- file configuration only lowers the root threshold when necessary, so a requested file level can flow without raising an already-more-verbose root threshold.

## Files

- `src/athena/observability/jsonl.py`
- `tests/unit/test_observability_jsonl.py`
- `tests/unit/test_observability_jsonl_retention.py`
- this handoff

No existing Observability privacy code is replaced. No storage schema, database, Source, PALLAS/UI, model/provider, job scheduler, network, backup, or packaging file is touched.

## Focused regression contract

The new tests cover:

- idempotent handler ownership;
- shared secret and semantic-payload redaction in persisted JSONL;
- valid JSON for every retained line;
- bounded rotation with active file plus exactly two configured backups in the focused case;
- deterministic removal of numeric backups outside a reduced retention window;
- preservation of unrelated sibling files;
- fail-closed non-file objects occupying a stale numeric backup slot;
- replacement when path/rotation policy changes;
- fail-closed invalid rotation bounds;
- fail-closed missing parent and non-`Path` input.

## Boundary deliberately left open

This does not claim runtime persistence is enabled. A later composition slice must choose an application-owned log directory using the existing runtime/path-safety contracts, then enable this primitive only after that directory boundary is proven. Cross-layer request/job/model-run correlation also remains separate.

### Required startup ordering for the later composition slice

Current `AthenaApplication.start()` intentionally performs the canonical database read-only integrity preflight before `StorageBootstrapService.start()` is allowed to create or probe runtime directories. `RuntimeLayoutService`, reached through storage bootstrap, is the existing owner that creates and validates `RuntimePaths.log_root`, rejects symlink boundaries, and proves that directory writable.

Therefore do **not** call `configure_jsonl_logging()` beside the existing early `configure_logging()` call. Opening the JSONL file there would introduce a filesystem write before the canonical database read-only preflight. A later runtime-wiring slice must preserve that ordering: first complete the read-only database preflight, then establish the safe runtime layout through the existing storage lifecycle, and only then attach the JSONL sink at an application-owned path such as `paths.log_root / "athena.jsonl"`. Any startup failure before that point must remain console-only.

## Integration rule

Fresh exact-head canonical ATHENA Quality is mandatory before promotion. Do not auto-merge this branch. Recheck current Develop, post-merge Quality, and worker collisions immediately before any integration. If Develop advances through PALLAS, Source/OCR, Backup, or other work, reconstruct/requalify this four-file slice on the then-current green Develop rather than relying on stale qualification evidence.
