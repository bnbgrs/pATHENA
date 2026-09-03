# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@3347f766651a9b6e2a03235eca4add7905ad4527`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: merge `c28f37e17ac4678cfc1a6cdccadcfed1ba4e0eef`, using the exact current Develop tree with prior Backend head `e3c7a7ea56206a1c7a965b74d4e649ada5e76ee7` retained as second parent.
- `main` remains strictly read-only and untouched.

## Selected backend slice

Area: ExternalAccessGateway runtime-boundary hardening.

Spec/product anchor: `docs/agent_backend_run_201_300.md` gateway-hardening target plus the existing fail-closed external-access contract in `src/athena/external/gateway.py` and its unit acceptance suite.

Current product evidence on the synchronized worker:

- `authorize_explicit(..., ttl_seconds: int)` validates only the numeric range. In Python, `bool` is an `int`, therefore `ttl_seconds=True` passes the range check and can create a durable authorization.
- `capture_url(..., max_bytes: int, timeout_seconds: float)` likewise range-checks values before `_authorized_or_audit`, but `max_bytes=True` and `timeout_seconds=True` pass those comparisons.
- The invalid values therefore cross security/resource runtime boundaries even though the annotated contract is integer bytes / numeric timeout and the existing gateway otherwise fails closed.

The bounded corrective contract is:

1. `ttl_seconds` must be a genuine integer (`type(value) is int`) before any local-user creation or authorization INSERT.
2. `max_bytes` must be a genuine integer before authorization lookup/audit, transport I/O or Source staging.
3. `timeout_seconds` may remain an ordinary finite numeric `int|float` for compatibility, but `bool` must be rejected explicitly before authorization lookup/audit or transport I/O.
4. Existing value ranges remain unchanged: TTL `1..86400`, byte budget `1..128 MiB`, timeout `(0, 300]`.
5. `authorize_direct_fallback` must not create a direct authorization from malformed boolean TTL input; validation must happen before the derived grant is persisted.

## Call-chain

`authorize_explicit(runtime input) -> purpose/route validation -> TTL exact-type/range boundary -> host validation -> local actor -> authorization INSERT/readback`.

`authorize_direct_fallback(source authorization, host, TTL) -> source/actor/route/host checks -> TTL boundary -> derived explicit Direct authorization`.

`capture_url(resource policy) -> max_bytes/timeout exact runtime boundary -> _authorized_or_audit -> privacy-route selection -> per-redirect authorization -> transport.fetch -> response policy -> final-URL authorization -> fsync staging -> transactional Source/audit/provenance finalize`.

## Retained invariants

- no silent Tor -> Direct fallback;
- Direct fallback requires a separate explicit authorization;
- no proxy leak for loopback/private destinations;
- redirect host scope is re-authorized before each fetch;
- HTTPS/default-port and destination policy remain fail-closed;
- response compression/size policy remains fail-closed;
- audit durability, Source provenance, fsync and transaction boundaries remain unchanged;
- no retry, persistence schema, recovery, UI, Search or PALLAS semantics change.

## Verification state

No product mutation was made in this run. The connector exposes whole-file replacement and Git-data object writes but no bounded patch primitive for an existing ~1k-line central gateway module. Replacing the complete module merely to change several predicates would create disproportionate overwrite risk and violate the small/safe mutation rule.

Focused acceptance tests to add with the product patch:

- `authorize_explicit(... ttl_seconds=True)` rejects before authorization-row count changes;
- `authorize_direct_fallback(... ttl_seconds=True)` rejects without a new Direct grant;
- `capture_url(... max_bytes=True)` rejects before audit rows, transport calls and Source rows change;
- `capture_url(... timeout_seconds=True)` rejects before audit rows, transport calls and Source rows change;
- valid boundary integers/floats continue to pass the existing range contract.

Existing `tests/unit/test_external_access_gateway.py` already covers explicit host scope, Tor Preferred no-direct-fallback, explicit fallback authorization, non-default-port rejection, response-policy failure and Source capture behavior. No PASS is claimed for the new boundary behavior because it is not yet implemented or executed.

## Coordination

- `postmerge/errors`: current ERR-0003 is UI/test-harness contract drift; no overlap with this gateway slice.
- `postmerge/spec-core`: normal-Hybrid Search facade/application wiring remains Core-owned; untouched.
- `postmerge/ui`: 11-screen/Qt work remains UI-owned; untouched.
- `develop/pathena-next`: integration target only; Backend never self-integrates.

## Integrator handoff

`c28f37e17ac4678cfc1a6cdccadcfed1ba4e0eef` is synchronization only and is not a product slice to cherry-pick. The Backend worker is now safely based on exact current Develop and ready for a bounded gateway patch once a patch-capable mutation route is available.

## Next backend slice

Implement the ExternalAccessGateway exact-runtime-type boundaries above with fail-before-side-effect tests, run the focused gateway suite plus relevant network/security regressions, and hand only verified product/test commits to the Integrator. If the mutation surface remains limited to unsafe whole-file replacement, continue read-only gateway/system analysis rather than risking central-module corruption.
