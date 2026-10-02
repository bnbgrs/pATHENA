# Plugin runtime domain-boundary handoff — 2026-10-02

## Base
- Branch: `fix/plugin-runtime-boundaries-current-20261002-sol`
- Base at creation: `develop/pathena-next@d80e92954005c7497697186cb945f96dd56017d4`
- This base already includes #393 publisher-trust hardening.

## Root cause
Parser functions validated plugin manifests and capability requests, but the public frozen dataclasses could still be constructed directly. Downstream Core code treats those objects as validated, so direct construction could bypass parser-only invariants.

## Product changes
- `PluginManifest.__post_init__()` now enforces canonical scalar grammar, enum collection runtime types, capability-to-permission authority, and canonical bounded publisher tuples even for direct construction.
- `PluginCapabilityRequest.__post_init__()` now enforces canonical request IDs, real `PluginCapability` values, bounded canonical scope text, and unsafe-text rejection for direct construction.
- Existing #393 publisher parsing/identity hardening is preserved; no identity/trust-root file is changed.

## Tests
- New `tests/unit/test_plugin_manifest_runtime_boundaries.py` covers direct scalar, collection, capability-authority and publisher metadata bypasses while preserving parser normalization.
- `tests/unit/test_plugin_process_boundary.py` adds canonical request/scope parsing tests, direct-construction bypass tests, and broker acceptance for a self-validated request.

## Scope
Fresh compare against Develop at handoff:
- 4 commits ahead / 0 behind
- only:
  - `src/athena/plugins/manifest.py`
  - `src/athena/plugins/protocol.py`
  - `tests/unit/test_plugin_manifest_runtime_boundaries.py`
  - `tests/unit/test_plugin_process_boundary.py`
  - this handoff

## Prior evidence
Old PR #392 exact head `94bb16069f25cf51be770156d729852c18e329a3` had ATHENA Quality PASS. This fresh current-Develop port still requires its own exact-head Quality before integration.

## Non-goals
No plugin loader, process host, sandbox expansion, capability expansion, or publisher trust-root duplication.

## Next
Run exact-head Quality. If terminal PASS and mergeable, integrate normally into `develop/pathena-next` and close old #392 as superseded.
