# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@f76911dfef6530041d62fb6c2e0ddec242d64231`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `e644e0d22b6733dd6bc5fec2c1dff042ef6dca0d`, with current Develop as first parent and prior Backend head `fad7ff588bc5035f07eac4d14ff53cc3d964cdc9` as second parent.
- The merge tree preserves current Develop plus Backend-owned `backend.md` and `backend-external-gateway-runtime-boundaries.patch`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Selected backend slice

Area: `ExternalAccessGateway` runtime-boundary hardening.

Spec/product anchor: `docs/agent_backend_run_201_300.md`, the existing fail-closed external-access contract in `src/athena/external/gateway.py`, and `tests/unit/test_external_access_gateway.py`.

Current product evidence was re-read from the exact worker blob `src/athena/external/gateway.py@ccadac3991c01e726108068768b5c7df8fadd9e9`:

- `authorize_explicit(... ttl_seconds)` still accepts `True` because Python `bool` is an `int`; the value can reach durable authorization insertion.
- `authorize_direct_fallback(... ttl_seconds)` still accepts boolean TTL far enough to read the source grant and resolve the actor before downstream clamping/attachment.
- `capture_url(... max_bytes, timeout_seconds)` still accepts boolean resource bounds.
- `timeout_seconds=float("nan")` bypasses both ordered comparisons because comparisons with NaN are false.
- These malformed values therefore cross intended fail-closed runtime boundaries before the relevant durable/network operations.

## Exact corrective contract

1. Explicit authorization TTL must be a genuine `int` and remain within `1..86400`.
2. Direct-fallback TTL must reject non-genuine integers before source/actor/service side effects; valid effective-TTL clamping remains unchanged.
3. `max_bytes` must be a genuine `int` before authorization/audit/transport/Source side effects; existing safe range remains unchanged.
4. `timeout_seconds` may be `int|float`, but bool and non-finite values must fail before authorization/audit/transport/Source side effects; `(0, 300]` remains unchanged.
5. No retry, persistence schema, recovery, redirect, Tor/Direct, provenance, UI or Search semantics change.

Exact product+test diff remains versioned at `docs/agent_handoffs/backend-external-gateway-runtime-boundaries.patch`.

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
- no uncontrolled retries or new cryptography.

## Verification / mutation state

Repository synchronization succeeded through the GitHub Git-data path; the worker is now based on exact current Develop without force or history rewrite.

The runtime environment still cannot resolve `github.com` for a local checkout, so `git apply` and pytest execution remain unavailable in this run. The connector can now return the complete gateway and test blobs, eliminating the earlier truncated-read uncertainty, but it still has no bounded hunk-edit/apply-patch operation. Applying the patch through whole-file replacement without an executable checkout would create a materially higher risk of transcription/formatting error and would still leave the required tests unexecuted. No unsafe product mutation was made.

No focused PASS is claimed. The versioned acceptance patch covers boolean explicit TTL, boolean direct-fallback TTL, boolean `max_bytes`, and boolean/NaN/infinite timeout, and asserts rejection before relevant persistence, audit, transport and Source side effects.

## Coordination

- Error worker: no current open root cause overlaps this gateway boundary slice; do not allocate a duplicate error unless a concrete current-lineage failure is reproduced.
- Core worker: normal-Hybrid Search composition remains Core-owned.
- UI worker: Qt/11-screen work remains UI-owned.
- Integrator: integrate only an applied-and-verified product/test SHA; the synchronization/handoff commits are not product completion.

## Integrator handoff

`e644e0d22b6733dd6bc5fec2c1dff042ef6dca0d` is synchronization only. The gateway patch remains NOT READY AS PRODUCT. Apply the existing patch through a bounded patch-capable execution environment, run `tests/unit/test_external_access_gateway.py` plus relevant Network/Security regressions, and integrate only the resulting verified product/test SHA.

## Next backend slice

First apply and verify the ExternalAccessGateway runtime-boundary patch. After closure, take the highest unclaimed Backend/System P0/P1/P2 gap from persistence/recovery, Provider/Transport, Windows publication/path safety, Packaging/install/runtime, or Research/Jobs execution.
