# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@fefe26b9fdc972b5e6950cd535397eae1067d5ea`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `538e1ae2e26bc33a63dc4c7377ac76940ba45b62`, parents `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` and exact Develop `fefe26b9fdc972b5e6950cd535397eae1067d5ea`.
- `main` remains strict read-only and untouched.

## Storage Health runtime boundaries — VERIFIED

Canonical ATHENA Quality Gate `33868034634` completed `success` on exact worker head `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY` for the bounded Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`.

## ExternalAccessGateway runtime boundaries — VERIFIED

Current product code contains the required fail-before-side-effect runtime guards:

- `authorize_explicit(... ttl_seconds=...)`: exact `int`, bool rejected, established `1..86400` range retained;
- `authorize_direct_fallback(... ttl_seconds=...)`: exact `int`, bool rejected, established `1..900` range retained before authorization lookup;
- `capture_url(... max_bytes=...)`: exact `int`, bool rejected, established safe range retained before authorization lookup/fetch;
- `capture_url(... timeout_seconds=...)`: numeric but not bool, finite via `math.isfinite`, established `(0, 300]` range retained before authorization lookup/fetch.

Gateway boundary test commit `3bd9e6ae4fd67344d5e8b094747daa5ff7ea405f` is canonically verified by ATHENA Quality Gate `33878485868 = success` on exact synchronized head `3ff9e39ab8e01bf0aedc8ac524dd8bef8cf00e39`.

The explicitly required canonical harness `tests/unit/test_external_access_gateway.py` contains equivalent regression coverage in commit `f4a1fcb13ce80071a42e383cee1226516cba5a74`, without removing the dedicated authorization-boundary tests. Although run `33884147977` was cancelled and is not PASS evidence, the immediately following canonical Quality run `33884210684` completed `success` on exact head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, which contains `f4a1fcb13ce80071a42e383cee1226516cba5a74` unchanged.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY` for the ExternalAccessGateway runtime-boundary lineage through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`.

## Local model HTTP cumulative response-size boundary — VERIFYING

A concrete adjacent provider/transport gap was found in `_BoundedLocalResponse.read(amt)`: explicit chunk reads delegated `amt` directly and therefore did not share the cumulative response byte budget already enforced for streaming `readline()` calls. Repeated chunk reads could exceed `MAX_LOCAL_RESPONSE_BYTES` without triggering `LocalResponseTooLargeError`.

Product commit `247ff4710a889fdeb8be880b11be1d2cf870eb18` replaces the separate streaming counter with one response-wide byte counter. `read()`, `read(-1)` and `readline()` now share the same budget, requests are bounded to at most the remaining budget plus one detection byte, and overflow still fails closed with `LocalResponseTooLargeError`.

Test commit `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` adds unit coverage for cumulative chunk overflow, exact-limit EOF, mixed `readline()` + `read()` accounting, and negative/read-all behavior.

No PASS is claimed until an exact-head or descendant canonical Quality run executes these unchanged product/test blobs successfully.

## Invariants retained

- local model HTTP transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation remain unchanged;
- response-size enforcement is strengthened without new retries, routing or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- no loopback/private proxy leak relaxation;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no Skip/XFail, assertion weakening or guard relaxation.

## Integrator handoff

- READY: Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`, canonical Quality `33868034634 = success`.
- READY: ExternalAccessGateway runtime-boundary lineage through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, canonical Quality `33884210684 = success`, including required harness commit `f4a1fcb13ce80071a42e383cee1226516cba5a74`.
- NOT READY: local HTTP cumulative response-size product/test commits `247ff4710a889fdeb8be880b11be1d2cf870eb18` + `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` pending executable canonical evidence.

## Next backend slice

Consume the exact Quality result containing local HTTP commits `247ff4710a889fdeb8be880b11be1d2cf870eb18` and `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33`. If green, mark the cumulative response-size boundary VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, correct only the exact Backend-owned failure before unrelated work.
