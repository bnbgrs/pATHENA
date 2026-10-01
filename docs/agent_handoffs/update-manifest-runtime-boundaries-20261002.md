# Update manifest runtime-boundary hardening — 2026-10-02

## Baseline / parallel-work check

- Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.
- This branch intentionally does not touch active parallel slices:
  - #325 canonical Storage commit bundle;
  - #327 Qt quality-process isolation;
  - #328 Chat cancellation architecture handoff;
  - #329 Chat cancellation Core control plane.
- #326 Research accessibility was already merged before this branch was created.
- Files are limited to the update-manifest contract, its focused unit tests, and this handoff.

## Ausgangslage

`UpdateManifest.from_bytes()` validated signed canonical JSON strictly, but a caller could construct
`UpdateManifest(...)` directly with values that violate those same invariants. Examples included a
string instead of `UpdateChannel`, boolean integer fields, unsupported manifest versions, invalid
package names/hashes, or a schema interval with maximum below minimum.

`supports_schema()` also relied on Python comparison semantics, so `True` behaved as integer
`1` and other wrong runtime types could escape as incidental `TypeError`.

`verify_signed_manifest()` relied mostly on downstream cryptography/base64 exceptions. Wrong
runtime types could therefore surface as unrelated exceptions, and an arbitrarily large base64
signature string was decoded before the Ed25519 64-byte invariant was enforced.

## Root cause

The update boundary had two validation paths with unequal strength:

1. serialized input -> strict parser -> validated manifest;
2. in-process direct construction -> dataclass field annotations only.

Python type annotations do not enforce runtime invariants, so the trusted manifest object could exist
in states that the authenticated wire format explicitly rejects.

## Änderungen

### Product

`src/athena/update/manifest.py`

- added `UpdateManifest.__post_init__()` so direct construction enforces:
  - real `UpdateChannel` identity;
  - exact supported manifest version, rejecting bools;
  - semantic-version syntax;
  - bounded safe package-name syntax;
  - positive non-bool package size;
  - canonical lowercase SHA-256 text;
  - positive non-bool schema versions;
  - maximum schema version not below minimum.
- made `supports_schema()` fail closed for bool/non-int runtime values instead of using incidental
  Python numeric coercion.
- bounded manifest parsing to 64 KiB and made `UpdateManifest.from_bytes()` reject non-byte runtime input before JSON parsing;
- replaced the approximate version regex with a SemVer 2.0-compatible contract for core/pre-release/build structure, including rejection of leading-zero numeric pre-release identifiers;
- hardened `verify_signed_manifest()` runtime boundaries:
  - manifest payload must be bytes and within the same 64 KiB bound;
  - detached signature must be text;
  - oversized signature text is rejected before base64 decoding;
  - public key must be exactly 32 bytes;
  - decoded Ed25519 signature must be exactly 64 bytes;
  - all boundary failures become `UpdateVerificationError`.

### Tests

`tests/unit/test_update_manifest.py`

- direct-construction regressions for channel/version/package/hash/schema invariants;
- schema-compatibility regressions for bool/float/text/None;
- signed-manifest runtime-boundary regressions for wrong payload/signature/key types and sizes;
- parser size/type regressions;
- SemVer regressions for invalid leading zeros and valid pre-release + build metadata.

## Verhalten danach

There is one fail-closed manifest invariant regardless of whether metadata came from signed JSON or
was constructed inside the process. Invalid compatibility probes and malformed signature/key inputs
cannot produce a trusted manifest or leak unrelated runtime exceptions.

No update staging, installation, migration, network-check, rollback, or channel-switch behavior is
added or changed.

## Validierung

- Static branch/base comparison: only the intended update source/test files changed before this
  handoff.
- Manual diff review caught and corrected an intermediate connector-escaping defect in the SemVer
  regex before qualification; the current head contains single regex escapes (for example `\.`
  and `\+`) as intended.
- Direct local pytest is not available in the current execution environment because the container
  cannot resolve `github.com` for a checkout.
- Required next validation: focused `tests/unit/test_update_manifest.py`, Ruff, mypy and canonical
  Quality on this exact branch head. No PASS is claimed until CI reports it.

## Konfliktrisiko / Abhängigkeiten

- Low conflict risk: current active #325/#327/#328/#329 file sets do not include the files in this
  slice.
- If `develop/pathena-next` moves before integration, compare the new base first; reconstruct rather
  than overwrite if another update-manifest change appears.
- Preserve Beta 23 behavior: this patch strengthens authenticated package metadata only and does not
  bypass preflight/restore-point/rollback requirements.

## Nächste sinnvolle Schritte

1. Qualify exact branch head with focused/update and canonical quality gates.
2. If green and base remains non-conflicting, integrate as one bounded update-security slice.
3. Continue Beta 23 staged-update/preflight work separately; do not fold it into this boundary patch.
