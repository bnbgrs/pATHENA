# Alpha/Beta application update v3 — authenticated package contract

Date: 2026-09-27
Base Develop: `cd891f602a1de48f90e9c0cb0f83cbff15ba1e62`
Branch: `fix/alpha-beta-application-update-v3`

## This slice

- introduces strict canonical JSON metadata for stable/beta application updates;
- authenticates the exact manifest bytes with a detached Ed25519 signature;
- binds package name, byte size, SHA-256 digest, application version, and supported
  database-schema interval into the signed contract;
- rejects duplicate/unknown fields, invalid versions/channels, non-canonical JSON,
  malformed signatures, links/junctions, path-identity races, size drift, and hash drift;
- exposes compatibility checking only; it does not migrate or reinterpret stored data.

## Tests

`tests/unit/test_update_manifest.py`

## Next

After exact-head green, add preflight composition on top of the existing read-only
database inspection and backup primitives. Do not implement an install switch until
a verified restore point and deterministic rollback contract are both present.
