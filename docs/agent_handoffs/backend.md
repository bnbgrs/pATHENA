# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `cbcb155f961f861c0dc48419d7bfee7d47e25d89`, with parents prior Backend head `225db6c031551a2b79edf0d74b331a33e359ad26` and exact Develop `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.
- Required handoffs and worker heads were reviewed before mutation.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage Health runtime boundaries — VERIFIED

Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` is backed by canonical ATHENA Quality `33868034634 = success` and is now present on current Develop.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP cumulative response-size boundary — VERIFIED

Product `247ff4710a889fdeb8be880b11be1d2cf870eb18` and tests `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` share one response-wide byte budget across `read()`, `read(-1)` and `readline()`. Exact descendant Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` passed canonical Quality `33890486614 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP readline remaining-budget hardening — VERIFIED

Product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` makes `readline()` request only `remaining + 1` bytes, retaining one detection byte for fail-closed overflow handling. Harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e` aligns the two LM-Studio expectations with this intentional behavior.

Exact descendant Backend head `225db6c031551a2b79edf0d74b331a33e359ad26` passed canonical ATHENA Quality `33911612711 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`; `ERR-0009` is satisfied by exact green descendant evidence.

## Local model HTTP direct-read total-deadline enforcement — VERIFYING

Current product commit `2270477ccf7631471379774430745f1a81f24d36` enforces the existing monotonic total-response deadline inside direct `read()` and `readline()` calls, before the underlying read and again before returning accepted bytes. This closes the direct-call path that previously relied on `__iter__()` for total-deadline checks.

Focused test commit `93e83640e69df9016fc4a10ac790e803fecf5d57` proves:

- expired deadline rejects direct `read()` before any underlying read;
- expired deadline rejects direct `readline()` before any underlying read;
- a deadline expiring during an underlying read fails closed before bytes are returned to the caller.

Canonical Quality `33916277339` exists on exact focused-test head `93e83640e69df9016fc4a10ac790e803fecf5d57` and is pending. No PASS/READY claim is made for this slice yet.

## Invariants retained

- local model HTTP transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation remain unchanged;
- response-size enforcement remains fail-closed;
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
- READY: local HTTP cumulative response-size lineage through `b025f6de83a969cca10a7677faae0b349e1a2988`, canonical Quality `33890486614 = success`.
- READY: local HTTP readline remaining-budget product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` plus harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`, exact descendant Quality `33911612711 = success`.
- NOT READY: direct-read total-deadline product `2270477ccf7631471379774430745f1a81f24d36` plus focused tests `93e83640e69df9016fc4a10ac790e803fecf5d57` until an exact descendant canonical Quality run is green.

## Next backend slice

Consume exact canonical evidence containing `93e83640e69df9016fc4a10ac790e803fecf5d57`. If green, mark direct-read total-deadline enforcement VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, correct only the exact Backend-owned failure before unrelated mutation.
