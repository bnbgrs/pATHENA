# Core API client runtime-boundary handoff — 2026-10-02

## Ausgangslage

The local desktop Core client trusted type annotations for several numeric runtime
inputs. Boolean, non-integer pagination and non-finite timeout values could pass
initial validation and fail later in discovery/urllib. The generic numeric
response decoder also accepted NaN/Infinity.

## Root Cause

Python bool is an int subtype, ordinary comparison checks do not reject NaN, and
the client normalized response floats without an explicit finiteness check.

## Änderungen

- require positive finite numeric transport and generation timeouts;
- reject bool and non-integer chat list limit/offset before discovery or HTTP;
- reject non-finite numeric response fields with `invalid_response`;
- add focused regression coverage for all three boundaries.

## Dateien

- `src/athena/api/client.py`
- `tests/unit/test_core_api_client.py`
- this handoff

## Verhalten danach

Malformed client configuration/request values fail deterministically before any
Core lookup or network request. Corrupt/non-standard JSON numeric values cannot
cross the client response boundary as valid floats.

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
