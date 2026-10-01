# Plugin Publisher Boundary Handoff — 2026-10-02

## Ausgangslage

- Repository: `bnbgrs/pATHENA`
- Target: `develop/pathena-next`
- Branch creation base: `467ef434236c320e4afe9d21a39c20a4a2b75728`
- Branch: `fix/plugin-publisher-boundary-validation-20261002-sol2`
- No open Plugin PR existed when this slice was selected.
- Scope is intentionally limited to publisher identity validation and its focused tests.

## Root Cause

The public publisher-identity boundary trusted type annotations more than runtime input:

1. `TrustedPluginPublisher.__post_init__()` only checked `len(public_key) == 32`. A 32-character Python `str` therefore passed construction even though Ed25519 verification requires raw bytes.
2. `key_id` was passed into the regex without an explicit string check, so malformed callers could receive a regex `TypeError` instead of the plugin-domain failure.
3. `canonical_plugin_identity_payload()` called `.strip()` on `package_sha256` before validating its runtime type.
4. `verify_plugin_publisher_identity()` called `trust_roots.get(...)` without checking that the supplied object was actually a Mapping.
5. A Mapping entry could be an arbitrary object; attribute access or crypto construction could then leak implementation exceptions out of the trust boundary.

These are configuration/runtime-boundary defects. They do not create a valid forged signature, but they weaken fail-closed behavior and can turn malformed trust configuration into uncontrolled exceptions during plugin verification.

## Änderungen

- Require publisher `key_id` to be a valid string before regex validation.
- Require `public_key` to be `bytes` and exactly 32 bytes.
- Reject non-string package digests with `PluginPublisherIdentityError` before normalization.
- Validate `trust_roots` as a runtime `Mapping` before lookup.
- Validate retrieved entries as `TrustedPluginPublisher` before reading fields or constructing Ed25519 keys.
- Preserve existing signature, package hash, manifest binding and trust-root key-ID semantics.

## Dateien

- `src/athena/plugins/identity.py`
- `tests/unit/test_plugin_publisher_identity.py`
- this handoff

## Regression Coverage

Focused tests now cover:

- non-string key IDs;
- 32-character string values passed where Ed25519 public-key bytes are required;
- non-string `package_sha256`;
- non-Mapping `trust_roots`;
- arbitrary objects stored as trust-root entries.

The tests use `typing.cast` only to cross static type boundaries deliberately; production runtime validation remains the subject under test.

## Validierung

Completed in this run:

- compared branch to exact creation base: only two intended product/test files changed before this handoff;
- branch was 3 commits ahead / 0 behind that base;
- both changed Python files checked for lines over 100 characters: none;
- source re-read after writes;
- no parallel Plugin PR found.

Not available in this execution environment:

- local pytest/Ruff/mypy because direct GitHub checkout is DNS-blocked;
- no UI work is involved.

Exact-head GitHub CI is the executable validation source.

## Verhalten danach

Malformed plugin trust configuration is rejected at the publisher identity boundary with controlled, intentional errors. Valid trusted Ed25519 verification behavior is unchanged.

## Bekannte Restprobleme

- This does not claim OS sandboxing for plugin code; Beta chapter 17 explicitly treats v1 third-party plugin code as trusted local extension code.
- Publisher display metadata remains unauthenticated by design.
- Plugin manifest display metadata normalization could be audited separately, but is not changed here.

## Konfliktrisiko

Low. No active Plugin PR was found and the slice does not touch Plugin Host, capabilities, Jobs, Core API, Storage, UI, Research, Chat or Model code.

## Nächste Schritte

1. Triage exact-head CI for draft PR #393 and fix only failures attributable to this slice.
2. If green, integrate independently from the Recovery/Doctor PR.

## Commit / PR

- Base: `467ef434236c320e4afe9d21a39c20a4a2b75728`
- Product/test head before handoff: `f2ed758334f4c299cfa271001784ebbdc316fc8f`
- PR: #393
