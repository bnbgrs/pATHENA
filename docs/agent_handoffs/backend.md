# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@6a9b933dcec80d4d104ac7d3be68351c46554864`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `86c7ba35d527c1437a840e0d9ea15a4a034392e6`, with parents prior Backend head `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` and exact Develop `6a9b933dcec80d4d104ac7d3be68351c46554864`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.
- Required handoffs were reviewed before mutation: errors, spec-core, ui, integrator and this Backend handoff.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage Health runtime boundaries — VERIFIED

Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` is backed by canonical ATHENA Quality `33868034634 = success` and is present on Develop.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP cumulative response-size boundary — VERIFIED / INTEGRATED

Product `247ff4710a889fdeb8be880b11be1d2cf870eb18` and tests `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` share one response-wide byte budget across `read()`, `read(-1)` and `readline()`. Exact descendant Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` passed canonical Quality `33890486614 = success`; Integrator has since carried byte-identical cumulative-budget product/test blobs onto Develop.

Status: `BACKEND_VERIFIED / INTEGRATED_ON_DEVELOP`.

## Local model HTTP readline remaining-budget hardening — VERIFIED / INTEGRATED

Product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` makes `readline()` request only `remaining + 1` bytes, retaining one detection byte for fail-closed overflow handling. Harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e` aligns the LM-Studio size expectations with this intentional behavior.

Exact descendant Backend head `225db6c031551a2b79edf0d74b331a33e359ad26` passed canonical ATHENA Quality `33911612711 = success`; Integrator has since carried the verified blobs to Develop.

Status: `BACKEND_VERIFIED / INTEGRATED_ON_DEVELOP`; `ERR-0009` is closed.

## Local model HTTP direct-read total-deadline enforcement — VERIFIED

Product `2270477ccf7631471379774430745f1a81f24d36` enforces the existing monotonic total-response deadline inside direct `read()` and `readline()` calls, before the underlying operation and again before returning accepted bytes. Focused tests `93e83640e69df9016fc4a10ac790e803fecf5d57` cover expired direct read/readline and expiry during a direct read.

Test-only correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81` supplies timestamps for the full first-line iterator check chain without weakening any product assertion or guard.

Exact descendant Backend head `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` passed canonical ATHENA Quality `33921338439 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP error-body total-deadline enforcement — FIXED_PENDING_VERIFY

HTTP error bodies were already wrapped in `_BoundedLocalResponse` for fail-closed response-size enforcement, but the wrapper omitted the validated total timeout. An active local-provider error stream could therefore continue making progress indefinitely while evading the total-response deadline that applies to successful responses.

Product commit `4f94d07f87849aec832437c2ac0dde66bd7433b2` passes the already validated request timeout into the HTTP-error `_BoundedLocalResponse`, preserving the same pre/post `read()` and `readline()` deadline guards. Focused test commit `08973df26572e66a3ecb26ace403362701e7376e` proves an expired HTTP-error body fails before the underlying body read.

No routing, retry, redirect, proxy, byte-limit, TLS, persistence, audit, provenance or cryptographic behavior changes.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until exact descendant canonical Quality is green.

## Invariants retained

- local model HTTP transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation remain unchanged;
- response-size enforcement remains fail-closed;
- total response deadline remains fail-closed on successful direct/iterator paths and now also applies to HTTP error-body parsing;
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
- INTEGRATED: local HTTP readline remaining-budget lineage through exact green `225db6c031551a2b79edf0d74b331a33e359ad26`, canonical Quality `33911612711 = success`.
- READY: direct-read total-deadline product `2270477ccf7631471379774430745f1a81f24d36` plus focused tests `93e83640e69df9016fc4a10ac790e803fecf5d57` and harness correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`, exact descendant `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`, canonical Quality `33921338439 = success`.
- NOT READY: HTTP-error total-deadline product `4f94d07f87849aec832437c2ac0dde66bd7433b2` plus focused tests `08973df26572e66a3ecb26ace403362701e7376e` until exact descendant canonical Quality is green.

## Next backend slice

Consume exact canonical Quality containing `08973df26572e66a3ecb26ace403362701e7376e`. If green, mark HTTP-error total-deadline enforcement VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact current diagnostics and minimally correct only the Backend-owned failure.