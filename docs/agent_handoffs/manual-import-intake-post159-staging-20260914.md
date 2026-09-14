# Import Intake — post-#159 no-skip staging

Status: STAGED_NOT_QUALIFIED

Base: `develop/pathena-next@4634af7ab0db315574e692c57635585d3a3b3bf6`

## Product

Carries the final historical Import Intake product blob `e0797e58cf123bcf1a4fe15d1c73db2fb0ec089d` after checking its current dependencies against post-#159 Develop:

- `SourceCaptureService.capture_file(Path)` still exists;
- `SourceCaptureService.capture_protected_file(..., protection_scope_id=UUID)` still exists;
- `RuntimePaths.spool_root` and optional `archive_root` still exist;
- `SourceChangedDuringCaptureError` remains the canonical mutation-during-copy signal;
- current BlobStore still performs the durable spool/hash/source-change boundary delegated to by intake.

No Source/Blob durability, dedup, hashing, encryption, or protection semantics are reimplemented by Import Intake.

## Test correction

The historical test blob was not reused unchanged because three link-policy tests depended on platform symlink creation and could call `pytest.skip()` when permissions/platform support were missing.

The staged test keeps the same contracts but simulates link/junction classification and target resolution deterministically with monkeypatches. This preserves coverage for:

- default do-not-follow policy;
- outside-root rejection under follow-inside-root;
- directory-cycle detection;

without Skip/XFail.

Other retained contracts include strict JSON payload validation, deterministic discovery, metadata filtering, size/count/spool preflight, fail-closed temporary/do-not-store flags, archive warning behavior, one source-mutation retry, sanitized partial/failure results, and exact protection-scope forwarding.

## Integration boundary

Do not open or merge a PR from this staging branch until the active PALLAS token-cache integration queue is resolved and current Develop is canonical-green. Before PR creation, run a fresh exact-base comparison, inspect any Source API drift, and qualify focused tests plus canonical Quality.
