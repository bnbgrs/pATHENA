# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `5f7bc011e7a14c893394e12afb9c68275bdeef17`; spec-core `ceb3682728aceb0b09893da6530dc38bc99f943a`; backend `f459035a701d6dad90d7be130e7a0644ae78201c`; ui `72c143fae1e339b254e5dc7be884c8efb79c7f84`.

## Integrated this run — local HTTP cumulative response-size boundary

Backend READY lineage through `b025f6de83a969cca10a7677faae0b349e1a2988` is backed by canonical Quality `33890486614 = success`.

Independent review confirmed current Develop still used separate streaming-only accounting and allowed bounded positive `read(amt)` calls to bypass the response-wide budget. The exact verified product and focused-test contents were carried:

- `src/athena/model/adapters/local_http.py` -> verified blob `c14d431d171edae4741dd0031f64b587965e4ca9`
- `tests/unit/test_local_http_response_boundaries.py` -> verified blob `5522f8e9f3ca2244f1126ca4480c2e28a84a63dc`

Develop integration commits:

- product: `86f3dd9059f5501b3455518f362d830e4d0aa1e3`
- focused test: `d6375236ae47d9fb7463722718fda12d82ab612e`

The slice establishes one cumulative byte budget across `read()`, `read(-1)` and `readline()`, retains one overflow-detection byte, and fails closed once accepted bytes would exceed the configured cap. Loopback-only routing, proxy rejection, redirect rejection, timeout validation and existing total-deadline semantics are unchanged.

## Validation state

- Exact Backend cumulative-size lineage passed canonical Quality `33890486614`.
- Integrated product/test blobs are byte-identical to that verified lineage.
- No exact current-Develop global Quality PASS is claimed in this run.
- Backend exact descendant `225db6c031551a2b79edf0d74b331a33e359ad26` passed canonical Quality `33911612711 = success`; this satisfies the Error worker's `ERR-0009` verification contract for the unchanged remaining-budget hardening plus harness correction.
- The newer direct-read total-deadline slice remains NOT READY until its own exact canonical Quality completes green.
- Core attribution candidate remains NOT READY while its exact Quality is pending.
- UI-GAP-0016 is READY on exact green UI lineage; UI-GAP-0017 remains pending verification.
- Original eleven visual references remain unavailable; zero pixel-level `MATCH` claims are permitted.

## Next integration order

1. Integrate the verified local HTTP `remaining + 1` readline hardening plus harness-only correction as the direct successor to this cumulative-budget prerequisite, after independent baseline/diff review.
2. Otherwise consume exactly one READY UI-GAP-0016 or exact-green Core slice if stronger current evidence appears.
3. Do not consume the direct-read total-deadline slice until its own exact canonical Quality is green.
4. Require exact-head evidence before any global-green Develop claim.

## Rules retained

- `main` remains read-only and unchanged.
- No force-push, history rewrite, auto-merge or automatic promotion to main.
- Pending/cancelled/action-required/in-progress/failed Quality is never PASS evidence.
- No weakened tests/guards or fabricated runtime success paths.
