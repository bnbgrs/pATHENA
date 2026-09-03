# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@dd4b623cc7bbc5b5a24c4427382f0b98ff50ad02`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `8997b1edbcaf565d4eda5b6879c0596c452091d9`, with prior Backend head `9083ca691b804962e136006745b07622bb95d84e` and current Develop as parents.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Selected backend slice

Area: `ExternalAccessGateway` runtime-boundary hardening.

Spec/product anchor: `docs/agent_backend_run_201_300.md`, existing fail-closed external-access contracts in `src/athena/external/gateway.py`, and the versioned patch `docs/agent_handoffs/backend-external-gateway-runtime-boundaries.patch`.

## Implemented behavior

Product commit `f34e2e6ffd589d7cfceb85dfbe7fcf7aea9f1be9` now enforces:

1. `authorize_explicit(... ttl_seconds)` accepts only genuine `int` values in the existing `1..86400` range; booleans fail before durable authorization creation.
2. `authorize_direct_fallback(... ttl_seconds)` rejects non-genuine integers before reading the source authorization or resolving the actor; valid effective-TTL clamping remains unchanged.
3. `capture_url(... max_bytes)` accepts only genuine `int` values within the existing safe range before authorization/audit/transport/Source side effects.
4. `capture_url(... timeout_seconds)` rejects booleans, non-numeric values, NaN and infinities; finite numeric values must remain in `(0, 300]`.
5. Tor/Direct routing, redirect reauthorization, retries, audit/provenance, staging/fsync, transaction boundaries, persistence schema and recovery semantics are unchanged.

Focused acceptance tests were added in `5cc4ea8c6b10c43c7203269bb4ccb1dbe484a109` as `tests/unit/test_external_access_gateway_runtime_boundaries.py`. They assert malformed values fail before new authorization rows, audit rows, transport calls or Source creation.

## Call-chain

`authorize_explicit -> purpose/route -> exact TTL boundary -> host policy -> actor -> authorization INSERT/readback`

`authorize_direct_fallback -> exact TTL boundary -> source grant -> actor/route/host -> effective TTL -> explicit Direct grant`

`capture_url -> exact resource boundaries -> _authorized_or_audit -> privacy route -> redirect re-authorization -> transport -> response policy -> fsync staging -> transactional Source/audit/provenance finalize`

## Retained invariants

- no silent Tor -> Direct fallback;
- separate explicit Direct authorization remains mandatory;
- no loopback/private proxy leak;
- redirect host re-authorization remains fail-closed;
- HTTPS/default-port and response size/compression policy remain unchanged;
- audit durability, Source provenance, fsync and transaction semantics remain unchanged;
- no uncontrolled retries or new cryptography.

## Verification

A draft verification PR was opened as `#54` from `postmerge/backend` to `develop/pathena-next`; it is not authorized for merge and exists only to obtain SHA-bound CI evidence.

Canonical Quality run `33790984890` is bound to exact product head `f34e2e6ffd589d7cfceb85dfbe7fcf7aea9f1be9`. At the handoff update point all four jobs had started and no conclusion was yet available. No PASS is claimed until the run completes successfully.

Local checkout-based pytest remains unavailable because the execution environment cannot resolve `github.com`; GitHub Actions is therefore the current executable verification path.

## Coordination

- Error worker: current open `ERR-0004` is UI-owned and does not overlap this gateway slice.
- Core worker: normal-Hybrid Search composition remains Core-owned.
- UI worker: Qt/11-screen and Ruff harness correction remain UI-owned.
- Integrator: do not integrate until exact SHA-bound Quality evidence is green; if run `33790984890` fails, reject this candidate and use the exact failing diagnostic for the next backend correction.

## Integrator handoff

Candidate product lineage: synchronization `8997b1edbcaf565d4eda5b6879c0596c452091d9` -> focused tests `5cc4ea8c6b10c43c7203269bb4ccb1dbe484a109` -> product `f34e2e6ffd589d7cfceb85dfbe7fcf7aea9f1be9`.

Status: `IMPLEMENTED_PENDING_VERIFY`. Integrate only after canonical Quality run `33790984890` completes green on exact head `f34e2e6ffd589d7cfceb85dfbe7fcf7aea9f1be9` and independent diff review confirms no guard weakening.

## Next backend slice

First close or correct this exact Gateway candidate from CI evidence. After verification, take the highest unclaimed Backend/System P0/P1/P2 gap from persistence/recovery, Provider/Transport, Windows publication/path safety, Packaging/install/runtime, or Research/Jobs execution.
