# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@8de698904c98cb50de327e805ae8e9b600df11ea`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `61370efd1a1c7accff52184772ace0c7299ab4d8`, parents prior Backend `e7e8d46e4d1011ec5586367f086c1571fe2a1267` + exact Develop `8de698904c98cb50de327e805ae8e9b600df11ea`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Verified predecessor

- `e7e8d46e4d1011ec5586367f086c1571fe2a1267` passed canonical ATHENA Quality Gate `34039538125 = success`.
- That exact-green lineage includes the migration PRAGMA exact-runtime-type boundary and negative WAL checkpoint frame-counter rejection.
- Error worker reports OPEN=none and no objection to that Backend candidate.

## Current slice

Area: Storage / Recovery / migration WAL checkpoint status shape.

Product `cdd261a0ee9ff9cb7799247cc83e1adc778cfd5f` requires `PRAGMA wal_checkpoint(TRUNCATE)` to return exactly the canonical three status fields before any journal-mode transition is attempted. Previously an oversized malformed row could pass the `len >= 3` shape gate and have trailing status data silently ignored.

Focused regression `53fb49cdf974ddf984def9d5978187191c621007` covers empty, one-field, two-field and four-field checkpoint rows and asserts rejection occurs before `PRAGMA journal_mode = DELETE`. Existing negative-frame-counter tests remain retained.

## Invariants

- candidate-only schema migration; live DB untouched;
- absolute regular non-link candidate and safe ancestry required;
- exact non-bool integer PRAGMA values retained;
- WAL frame counters remain non-negative;
- complete checkpoint remains required;
- malformed checkpoint shape fails before journal-mode transition;
- DELETE journal mode and sidecar-free activation handoff retained;
- no Security/TOR/Provider/UI semantics, schema representation, WAL format, retry or cryptography changes.

## Verification

- Predecessor canonical Quality `34039538125 = success`.
- Current exact test head `53fb49cdf974ddf984def9d5978187191c621007` has canonical Quality `34042405895` pending at handoff write time.
- No PASS or Integrator-ready claim is made for the new checkpoint-shape slice until an exact containing run completes successfully.

## Coordination

- Error head reviewed: OPEN=none; ERR-0016/ERR-0017 remain fixed.
- Spec/Core head `a47d4902c44d1a2126536cef65cb5f858aaa7fe9` is disjoint Personal-Memory/Core work.
- UI head `81b8d6c2c250a412bb2947b2b356d9111c10b995` is disjoint System posture UI work.
- Integrator/Develop head is `8de698904c98cb50de327e805ae8e9b600df11ea`; it has integrated the earlier PRAGMA exact-type slice but not this new exact-shape successor.

## Integrator handoff

READY: verified predecessor `e7e8d46e4d1011ec5586367f086c1571fe2a1267` / Quality `34039538125`.

NOT READY: exact WAL checkpoint status-shape product `cdd261a0ee9ff9cb7799247cc83e1adc778cfd5f` + focused tests `53fb49cdf974ddf984def9d5978187191c621007` pending canonical completion.

## Next backend slice

Consume the first exact canonical Quality containing `53fb49cdf974ddf984def9d5978187191c621007` or this documentation descendant. If green, promote only the exact status-shape slice and continue to the highest current unclaimed disjoint Backend/System gap. If red, repair only the smallest Backend-owned primary failure without weakening Storage/Recovery, ExternalAccessGateway, persistence, provenance or platform invariants. If cancelled, do not repeat unchanged; use a distinct executable verification route or disjoint real Backend/System slice.
