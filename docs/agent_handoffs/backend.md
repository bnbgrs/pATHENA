# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@25089e434412e7c1b8ede229438324338a0d5da0`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `d507de617f27976b174c1beadb22d8432fef63d6`.
- History-preserving NON-FORCE synchronization: `80ec5efc9a92881d429a7eab4cce9af7a2ad8a17`, with parents prior Backend head `d507de617f27976b174c1beadb22d8432fef63d6` and exact Develop `25089e434412e7c1b8ede229438324338a0d5da0`.
- Worker heads reviewed before mutation: errors `853bec9df7bdaa676ebc2424cbdc7b7bfb628f3a`; spec-core `eccbb0b7b0240f642fa9c678ff4fa58f4288e685`; ui `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- Required handoffs reviewed: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, and this Backend handoff.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage Health runtime boundaries — VERIFIED

Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` is backed by canonical ATHENA Quality `33868034634 = success` and is present on Develop.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP cumulative response-size boundary — VERIFIED / INTEGRATED

Product `247ff4710a889fdeb8be880b11be1d2cf870eb18` and tests `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` share one response-wide byte budget across `read()`, `read(-1)` and `readline()`. Exact descendant Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` passed canonical Quality `33890486614 = success`.

Status: `BACKEND_VERIFIED / INTEGRATED_ON_DEVELOP`.

## Local model HTTP readline remaining-budget hardening — VERIFIED / INTEGRATED

Product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` makes `readline()` request only `remaining + 1` bytes, retaining one detection byte for fail-closed overflow handling. Harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e` aligns LM-Studio expectations with the intentional behavior. Exact descendant Backend head `225db6c031551a2b79edf0d74b331a33e359ad26` passed canonical Quality `33911612711 = success`.

Status: `BACKEND_VERIFIED / INTEGRATED_ON_DEVELOP`; `ERR-0009` closed.

## Local model HTTP direct-read total-deadline enforcement — VERIFIED

Product `2270477ccf7631471379774430745f1a81f24d36`, focused tests `93e83640e69df9016fc4a10ac790e803fecf5d57`, and harness correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81` enforce the existing monotonic total-response deadline inside direct `read()` and `readline()` calls. Exact descendant Backend head `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` passed canonical Quality `33921338439 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP error-body total-deadline enforcement — VERIFIED

Product `4f94d07f87849aec832437c2ac0dde66bd7433b2` passes the validated request timeout into the HTTP-error `_BoundedLocalResponse`; focused tests `08973df26572e66a3ecb26ace403362701e7376e` prove an expired HTTP-error body fails before the underlying body read.

Exact descendant Backend head `d507de617f27976b174c1beadb22d8432fef63d6` passed canonical ATHENA Quality `33925587762 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP terminal size-overflow state — FIXED_PENDING_VERIFY

A response-size breach consumed bytes from the underlying local-provider stream but previously left `_bytes_read` at its pre-breach value because accounting happened only after the limit check. A caller that caught `LocalResponseTooLargeError` could therefore attempt another read against a wrapper that no longer represented the bytes already consumed from the transport.

Product `f1fba82ed81bb1fe744fa698bdacc8d25c1a1f8e` now accounts every consumed byte before evaluating the cumulative cap and rejects any subsequent `read()`/`readline()` before additional underlying I/O once the budget is exceeded. Test commit `31fa8d4cd25cd9a67a1e43bce22a600a98b98128` covers both direct-read and readline overflow poisoning and verifies the second access performs no new underlying read.

This does not change the configured limit, successful exact-limit behavior, timeout semantics, proxy/redirect policy, routing, retries, persistence, provenance, audit or cryptography.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact product-containing canonical Quality run is green.

## Invariants retained

- local model HTTP transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation unchanged;
- response-size enforcement remains cumulative and fail-closed, with terminal state after overflow;
- total response deadline remains fail-closed on successful direct/iterator paths and HTTP error bodies;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- no loopback/private proxy leak relaxation;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy, compressed-response rejection and response-size fail-closed behavior unchanged;
- audit, provenance, fsync and transactional Source finalization unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Integrator handoff

- READY: ExternalAccessGateway runtime-boundary lineage through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, canonical Quality `33884210684 = success`.
- READY: Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1`, canonical Quality `33868034634 = success`.
- INTEGRATED: local HTTP cumulative response-size lineage through `b025f6de83a969cca10a7677faae0b349e1a2988`, canonical Quality `33890486614 = success`.
- INTEGRATED: local HTTP readline remaining-budget lineage through `225db6c031551a2b79edf0d74b331a33e359ad26`, canonical Quality `33911612711 = success`.
- READY: direct-read total-deadline lineage through `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`, canonical Quality `33921338439 = success`.
- READY: HTTP-error total-deadline product `4f94d07f87849aec832437c2ac0dde66bd7433b2` + focused tests `08973df26572e66a3ecb26ace403362701e7376e`, exact descendant `d507de617f27976b174c1beadb22d8432fef63d6`, canonical Quality `33925587762 = success`.
- NOT READY: terminal size-overflow product `f1fba82ed81bb1fe744fa698bdacc8d25c1a1f8e` + tests `31fa8d4cd25cd9a67a1e43bce22a600a98b98128` until exact canonical green evidence.

## Next backend slice

Consume exact canonical Quality containing `31fa8d4cd25cd9a67a1e43bce22a600a98b98128`. If green, mark terminal size-overflow hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact diagnostics and minimally correct only the Backend-owned failure.
