# Alpha/Beta CanonicalCommitBundle handoff — 2026-10-01

## Scope

This is the deliberately narrow serializer/verifier slice for structured
long-term replication. It does **not** publish to `long_term_root`, select rows
from SQLite, advance replication watermarks, or implement snapshot/replay.

- Base when branch was created: `6f51095bed7d612cab7308fe19da58f647401c56`
- Branch: `fix/alpha-beta-canonical-commit-bundle-20261001`
- Draft PR: #324
- Parent release candidate #321 is independent and must integrate first if its
  exact-head gates finish green.

## Normative references used

Beta 03 requires:

- `CanonicalCommitBundle` with commit identity/sequence, schema/format version,
  predecessor/baseline hash, required structured revisions/metadata and an
  integrity manifest;
- hash-reproducible structured JSON follows RFC 8785 JCS;
- protected content appears only as ciphertext or opaque protected-payload
  references;
- unexpected long-term target history must never be silently overwritten.

Beta 16 additionally requires that public metadata for protected state remain
neutral. Sensitive titles, paths, URIs, exact media details, queries and other
revealing metadata belong in encrypted payloads.

## Work completed on this branch

### Initial worker commit

Added `src/athena/storage/canonical_commit_bundle.py` with:

- deterministic envelope/body model;
- stable record ordering;
- duplicate record identity rejection;
- SHA-256 body integrity;
- bundle hash over exact bytes;
- previous-head validation;
- protected `json` payload rejection;
- exact-byte verification.

### Review fixes added in support run

1. Canonical object ordering now uses UTF-16 code-unit ordering rather than
   Python Unicode code-point ordering, closing the non-BMP JCS mismatch.
2. The accepted number domain is deliberately restricted to integers in the
   exact IEEE-754 safe range. Floats/NaN/Infinity are rejected, so every
   accepted numeric value has an unambiguous JCS representation.
3. Invalid Unicode scalar values are rejected.
4. The verifier now checks exact body/integrity shapes and reconstructs the
   bundle through the serializer. A canonical, re-hashed but semantically
   invalid bundle can no longer pass merely because its checksum is valid.
5. The module explicitly documents the Protected Metadata boundary: the
   serializer only receives already-selected records and cannot infer whether
   arbitrary metadata text is sensitive.
6. Top-level `commit_id` now accepts `uuid.UUID`, matching
   `commit_records.commit_id BLOB(16)` and ATHENA's canonical UUID primitives.
   The bundle serializes the UUID to its canonical lowercase hyphenated text form
   only at the wire-format boundary, avoiding multiple caller-supplied textual
   representations of the same persistent commit identity.

### Focused tests added

`tests/unit/test_canonical_commit_bundle.py` covers:

- identical bytes/hash independent of input record order;
- UTF-16/JCS property ordering for non-BMP keys;
- safe integer boundary and float/NaN/Infinity rejection;
- duplicate record identity rejection;
- protected plaintext JSON rejection;
- accepted opaque protected representation kinds;
- noncanonical whitespace rejection;
- body tamper rejection;
- re-hashed semantic-invalid-body rejection;
- re-hashed protected-plaintext rejection;
- extra envelope fields;
- invalid Unicode scalar;
- invalid predecessor hash.
- top-level commit identity rejects arbitrary strings and requires `uuid.UUID`.

## Security decision still required

The low-level serializer must **not** be treated as proof that arbitrary
`metadata` is safe for a protected record. It can enforce representation
shape, not semantic sensitivity.

Before an end-to-end replication path is marked IMPLEMENTED, the upstream
record builder/selector must prove one of the following:

1. protected records expose only an explicit typed/allowlisted neutral metadata
   set; or
2. a canary leak test scans the produced bundle and proves sensitive metadata
   was moved to ciphertext/opaque protected-payload references.

Do not solve this by a brittle global blacklist of words.

## Validation required on current PR head

- focused canonical bundle tests;
- Ruff;
- mypy;
- pATHENA Storage Focused Candidate;
- full ATHENA Quality.

If a new failure occurs, diagnose only the new signature. Do not restart the
already-closed #321 Ruff/UI-refinement investigation.

## Next storage slice after #324

Create a **fresh branch from the then-current Develop** for verified
`long_term_root` publication:

1. read and verify expected target head before mutation;
2. existing identical bundle is idempotent success;
3. unexpected history enters persisted conflict/recovery and never overwrites;
4. write through durable temp + fsync + atomic rename/directory durability;
5. read back and verify exact bundle bytes/hash;
6. only then call the structured-replication confirmation/watermark transition;
7. prove crash/restart behavior around pre-write, post-write/pre-confirm and
   post-confirm boundaries.

Snapshot/replay remains a later slice.
