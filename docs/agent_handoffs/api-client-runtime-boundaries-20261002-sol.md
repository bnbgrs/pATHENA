# Core API client runtime-boundary handoff — 2026-10-02

## Ausgangslage

The local desktop Core client trusted type annotations for several numeric runtime
inputs. Boolean, non-integer pagination and non-finite timeout values could pass
initial validation and fail later in discovery/urllib. The generic numeric
response decoder also accepted NaN/Infinity. In addition, the runtime publisher
rejects link/reparse ancestors while the client previously checked only the
runtime root itself and individual bootstrap files.

## Root Cause

Python bool is an int subtype, ordinary comparison checks do not reject NaN, and
the client normalized response floats without an explicit finiteness check or a
bounded failure path for integer-to-float overflow. The bootstrap reader also
used narrower `Path.is_symlink()` checks than the publisher's shared
`is_link_boundary()` trust predicate.

## Änderungen

- require positive finite numeric transport and generation timeouts;
- reject bool and non-integer chat list limit/offset before discovery or HTTP;
- reject non-finite or float-overflowing numeric response fields with `invalid_response`;
- reject symlink/junction/reparse boundaries anywhere in the runtime-root path;
- use the shared filesystem trust predicate for discovery/token files;
- add focused regression coverage for numeric and bootstrap-path boundaries.

## Dateien

- `src/athena/api/client.py`
- shared trust predicate: `athena.storage.durable_fs.is_link_boundary` (import only)
- `tests/unit/test_core_api_client.py`
- this handoff

## Verhalten danach

Malformed client configuration/request values fail deterministically before any
Core lookup or network request. Corrupt/non-standard JSON numeric values, including enormous integers that
cannot be represented as floats, cannot escape the client response boundary as
raw conversion errors or valid floats. Bootstrap discovery now rejects linked
ancestors consistently with the runtime publisher before reading metadata.

## Validierung

No local PASS is claimed: this runner cannot resolve github.com for a checkout.
Exact-head GitHub Actions are the executable validation source. The PR remains
draft until canonical Quality completes.

## Abhängigkeiten / Konfliktrisiko

Base: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`.
The active Chat cancellation UI work does not touch `src/athena/api/client.py`;
Core cancellation itself is already integrated in the base. No current open PR
found in the synchronization pass owns this client file.

## Nächste sinnvolle Schritte

1. Qualify the exact PR head with canonical ATHENA Quality.
2. Fix only evidenced failures; do not weaken client validation.
3. Integrator should re-check `src/athena/api/client.py` ownership immediately
   before integration because it is a shared transport boundary.
