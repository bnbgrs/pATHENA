# Plugin runtime boundary handoff — 2026-10-02

## Ausgangslage

Beta 17 requires plugin manifests/capabilities to fail closed. The existing parser paths were strict, but three public runtime dataclasses were trusted by downstream Core code merely because their Python type matched:

1. `PluginManifest.from_mapping()` validates manifest syntax and authority, but callers could construct `PluginManifest(...)` directly and bypass those invariants.
2. `PluginCapabilityRequest` was described as validated, while direct construction bypassed request-id/scope anti-spoofing and capability-type validation. `PluginCapabilityBroker` only checked `isinstance(request, PluginCapabilityRequest)`.

Publisher trust-root hardening is intentionally excluded because parallel PR #393 now owns that exact boundary.

No executable plugin host/loader is added in this slice.

## Root Cause

Validation lived only at deserialization/factory boundaries while the validated domain objects themselves were publicly constructible frozen dataclasses. Downstream code therefore treated object identity/type as proof of validation although the constructor did not enforce the same contract.

## Änderungen

### Manifest

`src/athena/plugins/manifest.py`

Added `PluginManifest.__post_init__()` so every manifest instance enforces:

- canonical bounded scalar strings;
- plugin ID/version/API-version/entrypoint grammar;
- unsafe control/format-character rejection;
- exact `frozenset[PluginPermission]` and `frozenset[PluginCapability]` runtime types;
- capability → required coarse-permission relationship;
- bounded, canonical, unique and sorted publisher metadata.

`from_mapping()` remains the normal parser and still performs normalization before construction.

### Capability request

`src/athena/plugins/protocol.py`

Added `PluginCapabilityRequest.__post_init__()` enforcing request-ID, capability type and scope bounds/anti-spoofing rules for directly constructed instances.

Request IDs and scopes must now also be canonical (no leading/trailing whitespace), so the JSON decoder cannot produce multiple textual identities for the same logical opaque value.

This makes the broker's "validated request" type contract true independently of object origin.

## Tests

Added/expanded:

- `tests/unit/test_plugin_manifest_runtime_boundaries.py`
  - valid direct construction;
  - invalid/canonical scalar values;
  - runtime collection type spoofing;
  - capability/permission mismatch;
  - duplicate/unsorted/unsafe publisher metadata;
  - `from_mapping()` normalization compatibility.
  - invalid key-id runtime type;
  - bytearray/non-bytes public key rejection;
  - invalid trust-root mapping entry;
  - non-mapping trust-root container.
- `tests/unit/test_plugin_process_boundary.py`
  - direct request construction cannot bypass request-ID/capability/scope validation;
  - decoder rejects noncanonical padded request IDs/scopes;
  - valid direct request remains broker-authorizable.

## Dateien

- `src/athena/plugins/manifest.py`
- `src/athena/plugins/protocol.py`
- `tests/unit/test_plugin_manifest_runtime_boundaries.py`
- `tests/unit/test_plugin_publisher_identity.py`
- `tests/unit/test_plugin_process_boundary.py`
- this handoff

## Parallelität / Konfliktrisiko

Before mutation and again before PR preparation:

- `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`;
- no open PR matched Plugin work;
- stale historical plugin branches are ancestors of current Develop and contain no ahead commits;
- active current work is concentrated in Chat, Search, Core lifecycle, Recovery/System, Backup, Sources, Research, Knowledge, LM Studio, Settings, Windows packaging, Security, Logging and related areas.

This slice is isolated to `src/athena/plugins/*` plus plugin unit tests.

## Validierung

Completed:

- current-Develop relationship checked: branch is ahead only, not behind;
- diff scope checked after parallel deconfliction: two plugin production modules, two plugin test files and this handoff;
- existing parser/identity/broker contracts were inspected before mutation;
- no local success is claimed: the runner cannot resolve `github.com`, and the local container is not the repository's Python 3.12/uv environment.

Required exact-head validation:

- Ruff;
- mypy on `src/athena`;
- focused plugin unit tests;
- canonical ATHENA Quality Gate.

## Bekannte Restprobleme

Beta 17 still describes a larger plugin lifecycle/host/install surface that is intentionally not fabricated here. Current `athena.plugins` explicitly contains contracts and no executable plugin loader. A later feature slice should implement missing lifecycle only against the normative trust model and with explicit user installation; it must not turn this boundary-hardening PR into a broad architecture rewrite.

## Nächste sinnvolle Schritte

1. Run exact-head CI and fix any plugin/mypy/Ruff regression on this branch.
2. After integration, re-evaluate Beta 17 installation/lifecycle gaps from current Develop.
3. Prefer the smallest real vertical slice (for example explicit package inspection/install state) before introducing an executable host.
4. Keep all third-party code disabled by default until explicit trust/permission state exists.


## Parallel deconfliction update

After PR #392 opened, parallel PR #393 appeared on the same base and independently owned
`src/athena/plugins/identity.py` plus its publisher-identity tests. #393 also found an
additional non-string package-digest boundary that this branch had not covered.

To avoid competing edits, this branch restored both publisher-identity files exactly to
current Develop and leaves #393 as the sole owner of that boundary. PR #392 now owns only
Manifest and CapabilityRequest self-validation.
