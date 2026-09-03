# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@1dc2da1bd38e6147d01d3b1d6833ea1ea6a0e37b`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `a2274a512a0fdcb124112fd0060b7e6f03e23ee9`, with current Develop as first parent and prior Backend head `d3396dbc5d517a415a00a8e1105118263ad5c8d3` as second parent. The tree preserves current Develop plus the Backend handoff and versioned gateway patch artifact.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Selected backend slice

Area: `ExternalAccessGateway` runtime-boundary hardening.

Spec/product anchor: `docs/agent_backend_run_201_300.md` gateway-hardening target plus the existing fail-closed external-access contract in `src/athena/external/gateway.py` and `tests/unit/test_external_access_gateway.py`.

Current product evidence remains reproducible by inspection on the synchronized worker:

- `authorize_explicit(... ttl_seconds)` accepts `True` because Python `bool` is an `int`; this can reach durable authorization insertion.
- `authorize_direct_fallback(... ttl_seconds)` reads the source authorization and resolves the actor before malformed boolean TTL is rejected downstream.
- `capture_url(... max_bytes, timeout_seconds)` accepts boolean resource bounds; `timeout_seconds=float("nan")` also bypasses the current ordered comparisons.
- These malformed values therefore can cross security/resource boundaries before the intended fail-closed rejection point.

## Exact corrective contract

1. Explicit authorization TTL must be a genuine `int` and remain within `1..86400`.
2. Direct-fallback TTL must reject non-genuine integers before source/actor/service side effects; valid effective-TTL clamping remains unchanged.
3. `max_bytes` must be a genuine `int` before authorization/audit/transport/Source side effects; existing safe range remains unchanged.
4. `timeout_seconds` may be `int|float`, but bool and non-finite values must fail before authorization/audit/transport/Source side effects; `(0, 300]` remains unchanged.
5. No retry, persistence schema, recovery, redirect, Tor/Direct, provenance, UI or Search semantics change.

Exact product+test diff remains versioned at `docs/agent_handoffs/backend-external-gateway-runtime-boundaries.patch` from `2094951f358a8b60a1336a61d48daed7b15ef1b0`.

## Call-chain

`authorize_explicit -> purpose/route -> TTL boundary -> host policy -> actor -> authorization INSERT/readback`

`authorize_direct_fallback -> TTL boundary -> source grant -> actor/route/host -> effective TTL -> explicit Direct grant`

`capture_url -> resource boundaries -> _authorized_or_audit -> privacy route -> redirect re-authorization -> transport -> response policy -> fsync staging -> transactional Source/audit/provenance finalize`

## Retained invariants

- no silent Tor -> Direct fallback;
- separate explicit Direct authorization remains mandatory;
- no loopback/private proxy leak;
- redirect host re-authorization remains fail-closed;
- HTTPS/default-port and response size/compression policy remain unchanged;
- audit durability, Source provenance, fsync and transaction semantics remain unchanged;
- no uncontrolled retries or new crypto.

## Verification / mutation state

The worker synchronization is complete. The local execution environment still cannot resolve `github.com`, so a checkout-based `git apply` + pytest run remains unavailable. The GitHub connector can safely create commits/trees but does not expose a bounded hunk-edit/apply-patch operation for an existing large source file. Replacing the complete central gateway module from truncated reads would be an unnecessary overwrite risk, so no unsafe product mutation was made.

No focused PASS is claimed. The existing gateway suite and the versioned patch specify acceptance for boolean explicit TTL, boolean direct-fallback TTL, boolean `max_bytes`, and boolean/NaN/infinite timeout, all failing before relevant durable/network side effects.

## Coordination

- Error worker: no open root cause overlaps this gateway boundary slice; ERR-0003 is integrated on Develop.
- Core worker: normal-Hybrid Search composition remains Core-owned.
- UI worker: Qt/11-screen work remains UI-owned.
- Integrator: integrate only an applied-and-verified product/test SHA, never this documentation/patch-artifact state as completed functionality.

## Integrator handoff

`a2274a512a0fdcb124112fd0060b7e6f03e23ee9` is synchronization only. The gateway patch artifact remains NOT READY AS PRODUCT. Apply it through a bounded patch-capable environment, run `tests/unit/test_external_access_gateway.py` plus relevant Network/Security regressions, then hand off only the resulting verified product/test SHA.

## Next backend slice

First apply and verify the ExternalAccessGateway runtime-boundary patch. After closure, take the highest unclaimed Backend/System P0/P1/P2 gap from persistence/recovery, Provider/Transport, Windows publication/path safety, Packaging/install/runtime, or Research/Jobs execution.
