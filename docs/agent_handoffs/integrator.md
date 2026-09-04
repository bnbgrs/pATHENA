# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `b69a91a5781fd8d65b3643243c8feec60e4824f7`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `2ee9c374fd931a099de27b5ea8bd9dae0c876b76`; spec-core `66ddde67931b0fbc6b79cc35f534fb221bdd13bc`; backend `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`; ui `3d74d43279d9a80bf891bb6bc31001b1e43490e2`.

## Integrated this run — local HTTP readline remaining-budget hardening

Backend READY lineage is product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` plus harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`, exact verified descendant `225db6c031551a2b79edf0d74b331a33e359ad26`, canonical Quality `33911612711 = success`.

Independent diff review confirmed current Develop already contained the cumulative response-wide byte-budget prerequisite but still requested `max_bytes + 1` on every `readline()` call. The bounded successor changes only that remaining-budget boundary and its stale harness expectations.

Exact verified contents carried to Develop:

- `src/athena/model/adapters/local_http.py` -> blob `5fe00ce8a4b0b78f17279497b2a3d1caeeaac704`
- `tests/unit/test_lm_studio_response_limits.py` -> blob `28737d4b79f0d4b3e03d24f0f1a6d161ee736f99`

Develop integration commits:

- product: `efb5b1cb3ddc82f2908437ece67af2dbe9524032`
- harness: `2924280beed8999be4e82c41e16e4285e3c03eec`

`readline()` now requests only `remaining + 1`, preserving one overflow-detection byte and failing closed if the returned line exceeds remaining capacity. The harness expectation changes from repeated full-cap requests to the verified shrinking remaining-budget sizes. No assertion, byte cap, loopback-only restriction, proxy/redirect rejection, timeout validation, storage/security/recovery guard or provider routing contract was weakened.

## Validation state

- Exact Backend descendant `225db6c031551a2b79edf0d74b331a33e359ad26` passed canonical ATHENA Quality `33911612711` with Windows path safety, Linux storage regressions, local-install smoke, validator, Ruff, mypy, full pytest and canonical enforcement green.
- Integrated product and harness blobs are byte-identical to the exact verified lineage.
- No exact current-Develop canonical Quality run was attached immediately after the two integration commits; no global-green Develop claim is made.
- Error worker has already closed `ERR-0009`; no open deduplicated product error is currently recorded.
- Core attribution-aware contradiction policy is READY on exact green `ceb3682728aceb0b09893da6530dc38bc99f943a` / Quality `33915587266`; its newer combined contradiction gate remains pending verification.
- UI-GAP-0017 is READY on exact green `72c143fae1e339b254e5dc7be884c8efb79c7f84` / Quality `33917796701`; UI-GAP-0018 remains pending verification.
- Backend direct-read total-deadline product is still NOT READY until an exact descendant containing harness correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81` is canonical green.
- Original eleven visual references remain unavailable; zero pixel-level `MATCH` claims are permitted.

## Next integration order

1. Independently review exactly one current READY bounded slice: Core attribution-aware contradiction policy or UI-GAP-0017, preferring the stronger cross-cutting product dependency.
2. If Backend direct-read total-deadline correction obtains exact canonical-green evidence first, it becomes a valid bounded alternative.
3. Do not consume UI-GAP-0018 or the combined contradiction gate until their exact product-containing canonical Quality is green.
4. Require exact-head evidence before any global-green Develop claim.

## Rules retained

- `main` remains read-only and unchanged.
- No force-push, history rewrite, auto-merge or automatic promotion to main.
- Pending/cancelled/action-required/in-progress/failed Quality is never PASS evidence.
- No weakened tests/guards or fabricated runtime success paths.
