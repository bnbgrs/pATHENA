# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@2520224ebe3143368b3e5f13c091479d5e7b8d35`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `e07e08ce05dc31af081da4c165465d47601760b7`, with parents prior Backend head `d9685d5ab3ce49c09ccfe6c4df375e238886b904` and exact Develop `2520224ebe3143368b3e5f13c091479d5e7b8d35`.
- `main` remains strict read-only and untouched.
- Current worker heads reviewed: errors `28e75ca7391ce0f41165f6d481f1318a98f27fdb`, spec-core `921c6868c8813c92da200cdd68a0ba12df583e9c`, ui `3d3ac638ce35c2bd149cea2358ef726f243244f0`.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage Health runtime boundaries — VERIFIED

Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` is backed by canonical ATHENA Quality `33868034634 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP cumulative response-size boundary — VERIFIED

Product `247ff4710a889fdeb8be880b11be1d2cf870eb18` and tests `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` share one response-wide byte budget across `read()`, `read(-1)` and `readline()`. Exact descendant Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` passed canonical Quality `33890486614 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP readline remaining-budget hardening — FAILURE CORRECTED / VERIFYING

Product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386` makes `readline()` request only `remaining + 1` bytes, retaining one detection byte for fail-closed overflow handling.

The first focused test commit `4822b9ed6d84e05ae3d293e362dc9be62b6e844b` contained a defective overflow fixture: after consuming `b"abc"`, the remaining stream started with a newline, so bounded `readline(3)` legitimately returned one byte and did not overflow. Canonical Quality `33895643213` on descendant head `d9685d5ab3ce49c09ccfe6c4df375e238886b904` ran four real jobs; Windows path safety, Linux storage and local-install smoke passed, while Python quality failed only at full pytest.

Fix commit `d988c9faa171f4fe86aac4b5fa4d169e8ee34a41` changes only that test fixture to `b"abcdef\n"`, so after consuming `b"abc"` the bounded `readline(remaining + 1)` receives three bytes while only two remain and exercises the intended `LocalResponseTooLargeError` path. Product behavior is unchanged.

Canonical Quality `33900614960` exists for exact fix head `d988c9faa171f4fe86aac4b5fa4d169e8ee34a41` and was pending at handoff update time. No PASS/READY claim is made until it executes and completes green.

## Invariants retained

- local model HTTP transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation remain unchanged;
- response-size enforcement remains fail-closed and is strengthened without new retries, routing or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- no loopback/private proxy leak relaxation;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no Skip/XFail, assertion weakening or guard relaxation.

## Integrator handoff

- READY: ExternalAccessGateway runtime-boundary lineage through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, canonical Quality `33884210684 = success`.
- READY: Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`, canonical Quality `33868034634 = success`.
- READY: local HTTP cumulative response-size lineage through `b025f6de83a969cca10a7677faae0b349e1a2988`, canonical Quality `33890486614 = success`.
- NOT READY: local HTTP readline remaining-budget hardening `2981624e0f7eef8c2e94b6f0eb86a859132a2386` with corrected focused harness `d988c9faa171f4fe86aac4b5fa4d169e8ee34a41` until canonical `33900614960` is green.

## Next backend slice

Consume canonical Quality `33900614960`. If green, mark readline remaining-budget hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, correct only the exact Backend-owned failure before unrelated mutation.
