# Manual Observability JSONL diagnostics — post-Knowledge Develop — 2026-09-14

Base: `develop/pathena-next@f8a25be7fd7df9f2a8ca281a1567f79ddaabcfb6`
Branch: `manual/observability-jsonl-post-knowledge-20260914`
Supersedes integration use of draft #218; older #205/#187 remain provenance only.

## Purpose

Reconstruct the bounded Observability JSONL primitive on the current post-Knowledge Develop line without entering Backend/WAL, Source/OCR, Spec/Core/Knowledge, UI/PALLAS, Security, backup, or packaging ownership.

This slice adds an opt-in persistent JSONL sink only. It deliberately does **not** wire the sink into `AthenaApplication` or any runtime layout, so application startup behavior and existing console logging remain unchanged.

## Qualification correction from #218

#218 exact head `e3558c95011657af9158d8162b18b81b7170dc84` passed canonical pytest, Windows path safety, Linux storage, local install smoke, specification validation, and Ruff, but canonical mypy failed on one issue:

`src/athena/observability/jsonl.py:73: "_SecureRotatingFileHandler" has no attribute "_builtin_open" [attr-defined]`

At runtime `logging.FileHandler.__init__` installs `_builtin_open` as its cached builtin-open hook. The stdlib typing surface does not expose that private runtime attribute. This reconstruction keeps the runtime/security behavior intact and explicitly declares the inherited hook as `Callable[..., TextIOWrapper]` on `_SecureRotatingFileHandler`. It does not replace the hook with a different open path and does not weaken descriptor/path identity validation.

Fresh exact-head CI is mandatory; the old #218 failure is not treated as green evidence.

## Product behavior

- `configure_jsonl_logging()` uses a standard-library rotating file handler with a hardened open path;
- one privacy-preserving JSON object per line through the already-qualified shared `JsonFormatter`;
- JSONL is attached to the `athena` logger namespace rather than Root;
- the `athena` namespace uses explicit level `1`, so individual handler thresholds own routing for normal/custom positive levels;
- Console may continue to own/reset the Root level without suppressing more-verbose `athena.*` records before JSONL sees them;
- Console and JSONL can therefore use different levels in either configuration order;
- any legacy Root-owned ATHENA JSONL handler is removed before the namespace-owned handler is installed;
- byte-bounded rotation and count-bounded retention;
- default 8 MiB active-file rollover threshold and 5 retained rotated files;
- numeric rotated backups outside a later-reduced retention window are removed before the new handler opens;
- unrelated sibling files are never treated as rotated backups, including filenames containing glob metacharacters;
- unexpected non-file objects in a stale numeric backup slot fail closed;
- exact positive-integer validation for `max_bytes` and `backup_count`, with booleans rejected;
- strict log-level validation matching the existing console configuration contract;
- missing parent directories fail before file creation;
- direct symbolic-link log targets and symbolic-link immediate parents fail closed;
- delayed first open and rollover reopen use descriptor/path identity checks so path substitution fails before log bytes are emitted through the substituted target;
- exactly one ATHENA-owned JSONL handler; repeated equivalent configuration is idempotent;
- changed path or rotation policy replaces the previous owned file handler deterministically.

## Files

Exactly four files relative to this Develop base:

- `src/athena/observability/jsonl.py`
- `tests/unit/test_observability_jsonl.py`
- `tests/unit/test_observability_jsonl_retention.py`
- this handoff

No pre-existing product file is changed.

## Regression contract

Coverage includes idempotent namespace ownership, shared secret/content redaction, valid retained JSONL, bounded rotation, reduced-retention cleanup, literal metacharacter filename handling, preservation of unrelated siblings, fail-closed non-file backup slots, independent Console/JSONL thresholds in both configuration orders, strict invalid-bound rejection, missing-parent/non-Path rejection, delayed-open symlink substitution, and rollover-time symlink substitution.

## Deliberate runtime boundary

This does **not** claim runtime persistence is enabled.

`AthenaApplication.start()` must keep canonical database read-only integrity preflight ahead of any filesystem writes introduced for logging. `RuntimeLayoutService`, through storage bootstrap, owns creation/validation of `RuntimePaths.log_root`. A later runtime-wiring slice must preserve this ordering:

1. configure console diagnostics;
2. complete read-only database integrity preflight;
3. establish the safe runtime layout through the existing storage lifecycle;
4. only then attach JSONL at an application-owned path such as `paths.log_root / "athena.jsonl"`.

Startup failures before step 4 remain console-only. Cross-layer request/job/model-run correlation remains separate.

## Integration rule

Require terminal SUCCESS for the exact current Develop push gate and for fresh canonical ATHENA Quality on this exact candidate head. Immediately before integration, recheck Develop identity, candidate head identity, exact four-file diff, and mergeability. If Develop advances first, reconstruct/requalify this bounded slice instead of using stale green evidence.
