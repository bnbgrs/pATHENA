# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@14adeb8949f680dc16a3067e586b3950132e0375`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `9cbace0756d5ab93ce322b7e0a76a5ce1eda03b2`, parents `3ff9e39ab8e01bf0aedc8ac524dd8bef8cf00e39` and exact Develop `14adeb8949f680dc16a3067e586b3950132e0375`.
- `main` remains strict read-only and untouched.

## Storage Health runtime boundaries — VERIFIED

Canonical ATHENA Quality Gate `33868034634` completed `success` on exact worker head `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY` for the bounded Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`.

## ExternalAccessGateway runtime boundaries — VERIFIED / FINAL HARNESS PLACEMENT VERIFYING

Current product code contains the required fail-before-side-effect runtime guards:

- `authorize_explicit(... ttl_seconds=...)`: exact `int`, bool rejected, established `1..86400` range retained;
- `authorize_direct_fallback(... ttl_seconds=...)`: exact `int`, bool rejected, established `1..900` range retained before authorization lookup;
- `capture_url(... max_bytes=...)`: exact `int`, bool rejected, established safe range retained before authorization lookup/fetch;
- `capture_url(... timeout_seconds=...)`: numeric but not bool, finite via `math.isfinite`, established `(0, 300]` range retained before authorization lookup/fetch.

Gateway boundary test commit `3bd9e6ae4fd67344d5e8b094747daa5ff7ea405f` is canonically verified by ATHENA Quality Gate `33878485868 = success` on exact synchronized head `3ff9e39ab8e01bf0aedc8ac524dd8bef8cf00e39`. This supplies real canonical evidence for bool TTL, bool max_bytes and bool/NaN/+Inf/-Inf timeout fail-before-side-effect behavior.

The explicitly required canonical harness `tests/unit/test_external_access_gateway.py` now also contains equivalent regression coverage in commit `f4a1fcb13ce80071a42e383cee1226516cba5a74`, without removing the dedicated authorization-boundary tests. Canonical Quality `33884147977` is associated with this exact test head and is pending; no PASS is claimed for this final harness-placement commit until jobs complete.

## Invariants retained

- no silent Tor -> Direct fallback; Direct remains explicit-only;
- no loopback/private proxy leak relaxation;
- redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no retries or cryptography added;
- no Skip/XFail, assertion weakening or guard relaxation.

## Integrator handoff

- READY: Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`, canonical Quality `33868034634 = success`.
- READY FOR BOUNDED REVIEW: ExternalAccessGateway runtime-boundary product/test lineage through `3ff9e39ab8e01bf0aedc8ac524dd8bef8cf00e39`, canonical Quality `33878485868 = success`.
- PENDING FINAL HARNESS EVIDENCE: `f4a1fcb13ce80071a42e383cee1226516cba5a74` adds the same required cases to `tests/unit/test_external_access_gateway.py`; Quality `33884147977` pending.

## Next backend slice

Consume exact Quality `33884147977`. If green, mark the canonical-harness placement verified and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, correct only the exact Backend-owned failure before unrelated work.
