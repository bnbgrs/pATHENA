# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@aed609ef8a7ff4af48e15e3dba953daf35d56b5c`.
- Worker branch: `postmerge/backend`.
- Latest history-preserving NON-FORCE synchronization: `6b85147dfd66399fabc04e4950058291feb85fec`, with prior Backend head `40c0aff638ee485591d8373d81e0de32ec0acfe7` and current Develop as parents.
- Develop differed from the previous Backend lineage only in `docs/agent_handoffs/integrator.md`; no Gateway/product/test conflict existed.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Completed backend slice — ExternalAccessGateway runtime boundaries

Spec/product anchor: `docs/agent_backend_run_201_300.md` findings 297-298, existing fail-closed contracts in `src/athena/external/gateway.py`, and `docs/agent_handoffs/backend-external-gateway-runtime-boundaries.patch`.

Product commit `f34e2e6ffd589d7cfceb85dfbe7fcf7aea9f1be9` enforces fail-before-side-effect runtime validation:

1. explicit authorization TTL: genuine `int`, existing `1..86400` range, bool rejected;
2. direct-fallback TTL: genuine `int` before source-grant/actor reads; existing effective-TTL clamp retained;
3. capture `max_bytes`: genuine `int`, existing safe range, bool rejected before authorization/audit/transport/Source effects;
4. capture timeout: numeric but not bool, finite, existing `(0, 300]` range; NaN/Inf rejected.

Focused acceptance tests were added in `5cc4ea8c6b10c43c7203269bb4ccb1dbe484a109` as `tests/unit/test_external_access_gateway_runtime_boundaries.py` and assert malformed inputs do not create authorization/audit/Source side effects or transport calls.

### Call-chain / invariants

`authorize_explicit -> purpose/route -> TTL boundary -> host policy -> actor -> authorization INSERT/readback`

`authorize_direct_fallback -> TTL boundary -> source grant -> actor/route/host -> effective TTL -> explicit Direct grant`

`capture_url -> resource boundaries -> _authorized_or_audit -> privacy route -> redirect reauthorization -> transport -> response policy -> fsync staging -> transactional Source/audit/provenance finalize`

Retained: no silent Tor->Direct fallback; explicit Direct approval; no loopback/private proxy leak; redirect reauthorization; HTTPS/default-port fail-closed policy; response size/compression fail-closed policy; durable audit/provenance/fsync/transaction semantics; no new retries or cryptography.

## Verification — READY

Canonical ATHENA Quality Gate `33790984890` is exact-SHA-bound to product head `f34e2e6ffd589d7cfceb85dfbe7fcf7aea9f1be9` and completed `success`.

Verified green jobs/steps include:

- Windows path safety: PASS;
- Linux storage regressions: PASS;
- Local install smoke / disposable Core-API restart: PASS;
- specification validator: PASS;
- Ruff: PASS;
- mypy: PASS;
- full pytest: PASS;
- canonical result enforcement: PASS.

Independent Integrator review had already identified the intended executable delta as exact-type/bool-safe TTL/max-bytes validation plus finite non-bool timeout validation; other product-commit changes are formatting/comment-only churn. No guard weakening or changed routing/persistence semantics is evidenced.

## Integrator handoff

READY product lineage:

`synchronization 8997b1edbcaf565d4eda5b6879c0596c452091d9 -> focused tests 5cc4ea8c6b10c43c7203269bb4ccb1dbe484a109 -> product f34e2e6ffd589d7cfceb85dfbe7fcf7aea9f1be9`

Current Backend synchronization `6b85147dfd66399fabc04e4950058291feb85fec` additionally incorporates current Develop documentation without altering Gateway product/test blobs.

Integrator may now integrate the bounded Gateway product/test lineage into `develop/pathena-next`; never `main`.

## Next backend slice — selected

Next highest residual Gateway findings are `docs/agent_backend_run_201_300.md` tasks 295-296:

- `authorize_explicit(... purpose)` currently calls `.strip()` without first requiring runtime text;
- `allowed_hosts: Sequence[str]` can receive malformed shapes such as a naked string and then iterate characters; elements also need explicit runtime text validation before `_normalize_host()`.

Planned contract: reject malformed purpose/host-container/host-element values before actor creation or durable authorization side effects while retaining existing normalized-host, local/private rejection, route, TTL and persistence behavior. Focused tests must prove fail-before-authorization-row and preserve valid tuple/list host inputs. This is the next Backend-owned slice unless a newer higher-severity current-lineage defect appears.

## Coordination

- Error worker owns current UI-related Ruff/error-ledger work; no overlap.
- Core owns normal-Hybrid facade/application composition and CHAT/KNOWLEDGE/RESEARCH/PALLAS semantics.
- UI owns Qt/11-screen work.
- Backend next touches only ExternalAccessGateway runtime input boundaries unless superseded by higher-priority evidence.
