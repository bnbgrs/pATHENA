# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@7be496d2fcbb94ab81f5e520f2e45ee2820d3fd9`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization with current Develop: merge `215a9e07661f09656ae80903a3b4b5a9f2dc6b5a`, retaining the prior Backend lineage as first parent and current Develop as second parent while using the exact Develop tree.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Selected backend slice

Area: ExternalAccessGateway runtime-boundary hardening.

Spec/product anchor: `docs/agent_backend_run_201_300.md` gateway-hardening target plus the existing fail-closed external-access contract in `src/athena/external/gateway.py` and `tests/unit/test_external_access_gateway.py`.

Current product evidence on the synchronized worker:

- `authorize_explicit(... ttl_seconds: int)` only range-checks the value; Python `bool` is an `int`, so `ttl_seconds=True` passes and can create durable authorization state.
- `authorize_direct_fallback(... ttl_seconds: int)` performs source/actor work before the malformed runtime type is rejected downstream.
- `capture_url(... max_bytes: int, timeout_seconds: float)` only range-checks values before `_authorized_or_audit`; `max_bytes=True` and `timeout_seconds=True` pass.
- `timeout_seconds=float("nan")` also passes both existing comparisons because NaN is unordered, so a non-finite timeout can reach transport setup.

## Exact corrective contract

1. `ttl_seconds` for explicit authorization must be a genuine `int` (`type(value) is int`) and retain the existing `1..86400` range.
2. Direct-fallback TTL must reject non-genuine integers before actor/service side effects; existing effective-TTL clamping semantics remain unchanged for valid integers.
3. `max_bytes` must be a genuine `int` before authorization/audit/transport/Source side effects; existing `1..128 MiB` range remains unchanged.
4. `timeout_seconds` may remain `int|float`, but bool and non-finite values must fail before authorization/audit/transport/Source side effects; existing `(0, 300]` range remains unchanged.
5. No retry, persistence schema, recovery, redirect, Tor/Direct or provenance behavior changes.

The exact minimal product+test diff is versioned at `docs/agent_handoffs/backend-external-gateway-runtime-boundaries.patch` in commit `2094951f358a8b60a1336a61d48daed7b15ef1b0`. This is a patch artifact, not a completed product commit.

## Call-chain

`authorize_explicit(runtime input) -> purpose/route -> exact TTL type/range -> host policy -> local actor -> authorization INSERT/readback`.

`authorize_direct_fallback(runtime TTL) -> exact type -> source grant -> actor/route/host checks -> effective TTL -> derived explicit Direct authorization`.

`capture_url(resource policy) -> exact max_bytes/finite timeout boundary -> _authorized_or_audit -> privacy route -> per-redirect authorization -> transport.fetch -> response policy -> final-URL authorization -> fsync staging -> transactional Source/audit/provenance finalize`.

## Retained invariants

- no silent Tor -> Direct fallback;
- Direct fallback requires separate explicit authorization;
- no loopback/private proxy leak;
- redirect host scope remains re-authorized before each fetch;
- HTTPS/default-port and destination policy remain fail-closed;
- response compression/size policy remains fail-closed;
- audit durability, Source provenance, fsync and transaction boundaries remain unchanged;
- no Search, PALLAS, UI, retry or schema semantics change.

## Verification state

Repository reads and branch writes through the GitHub connector succeeded. A local checkout was attempted specifically to apply and run the bounded patch, but failed before checkout because the runtime DNS resolver could not resolve `github.com`; therefore no focused PASS is claimed.

The existing gateway suite was re-read on the synchronized branch. It already verifies explicit scope, Tor Preferred no-direct-fallback, separate Direct authorization, non-default-port rejection, response-policy handling, audit behavior and real Source capture.

The patch artifact adds focused acceptance for:

- boolean explicit TTL rejected with authorization-row count unchanged;
- boolean direct-fallback TTL rejected without a new grant;
- boolean byte budget rejected before audit, transport and Source effects;
- boolean, NaN and infinite timeout rejected before audit, transport and Source effects.

## Failure / recovery impact

The intended mutation is fail-before-side-effect and side-effect reducing. It does not alter persisted records, schema, transaction structure, Source staging/finalization, authorization revocation, redirect processing, cancellation/retry behavior or recovery formats.

## Platform impact

Platform-neutral Python runtime-boundary hardening. No Windows/Linux path or packaging behavior changed in this run.

## Coordination

- Error worker: current ERR work is independent from this gateway boundary slice; do not duplicate the gateway root cause unless a canonical failure is observed.
- Core worker: normal-Hybrid Search composition remains Core-owned and untouched.
- UI worker: 11-screen/Qt work remains UI-owned and untouched.
- Integrator: `develop/pathena-next` remains integration target only; Backend does not self-integrate.

## Integrator handoff

NOT READY AS PRODUCT. `215a9e07661f09656ae80903a3b4b5a9f2dc6b5a` is synchronization only and `2094951f358a8b60a1336a61d48daed7b15ef1b0` adds an exact patch artifact only. Apply the versioned patch in a bounded patch-capable checkout, execute `tests/unit/test_external_access_gateway.py` plus relevant network/security regressions, then integrate only the resulting verified product/test commit(s).

## Next backend slice

First complete and verify the ExternalAccessGateway runtime-boundary patch. After that, select the next highest unclaimed Backend/System P0/P1/P2 gap from current Alpha/Beta progress and current Error/Integrator handoffs, prioritizing persistence/recovery, Provider/Transport, Windows publication/path safety, packaging/install/runtime and Research/Jobs system paths.
