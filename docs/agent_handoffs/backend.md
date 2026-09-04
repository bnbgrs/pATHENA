# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@b69a91a5781fd8d65b3643243c8feec60e4824f7`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `1800b3bf179ebce1c344d6c15ea2204ff055dcb8`, with parents prior Backend head `f459035a701d6dad90d7be130e7a0644ae78201c` and exact Develop `b69a91a5781fd8d65b3643243c8feec60e4824f7`.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.
- Required handoffs and worker heads were reviewed before mutation: errors `2ee9c374fd931a099de27b5ea8bd9dae0c876b76`, spec-core `66ddde67931b0fbc6b79cc35f534fb221bdd13bc`, ui `72c143fae1e339b254e5dc7be884c8efb79c7f84`.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage Health runtime boundaries — VERIFIED

Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` is backed by canonical ATHENA Quality `33868034634 = success` and is present on Develop.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP cumulative response-size boundary — VERIFIED / INTEGRATED

Product `247ff4710a889fdeb8be880b11be1d2cf870eb18` and tests `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` share one response-wide byte budget across `read()`, `read(-1)` and `readline()`. Exact descendant Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` passed canonical Quality `33890486614 = success`; Integrator has since carried byte-identical cumulative-budget product/test blobs onto Develop.

Status: `BACKEND_VERIFIED / INTEGRATED_ON_DEVELOP`.

## Local model HTTP readline remaining-budget hardening — VERIFIED

Product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` makes `readline()` request only `remaining + 1` bytes, retaining one detection byte for fail-closed overflow handling. Harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e` aligns the LM-Studio size expectations with this intentional behavior.

Exact descendant Backend head `225db6c031551a2b79edf0d74b331a33e359ad26` passed canonical ATHENA Quality `33911612711 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`; `ERR-0009` is closed.

## Local model HTTP direct-read total-deadline enforcement — FIXED_PENDING_VERIFY

Product `2270477ccf7631471379774430745f1a81f24d36` enforces the existing monotonic total-response deadline inside direct `read()` and `readline()` calls, before the underlying operation and again before returning accepted bytes. Focused tests `93e83640e69df9016fc4a10ac790e803fecf5d57` cover expired direct read/readline and expiry during a direct read.

Exact descendant canonical Quality `33916312429` on Backend head `f459035a701d6dad90d7be130e7a0644ae78201c` executed four real jobs. Windows path safety, Linux storage regressions and local-install smoke passed; validator, Ruff and mypy passed; only full pytest failed.

The failure is Backend-owned harness drift in `test_stream_iteration_enforces_monotonic_total_deadline`: direct `readline()` now performs its own pre/post deadline checks, so the previous four-value monotonic iterator reaches the deadline during the first yielded line rather than before the second streaming read. Product behavior is intentionally fail-closed and is not reverted.

Test-only correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81` supplies timestamps for the full first-line check chain (`__iter__` pre, `readline` pre/post, `__iter__` post) and reaches the deadline before the second underlying read. No assertion, production guard, timeout, byte-limit, routing or security contract is weakened.

Status: `FIXED_PENDING_VERIFY`; no PASS/READY claim until an exact descendant canonical Quality run is green.

## Invariants retained

- local model HTTP transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation remain unchanged;
- response-size enforcement remains fail-closed;
- total response deadline remains fail-closed on direct and iterator paths;
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
- READY: local HTTP readline remaining-budget product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` plus harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`, exact descendant Quality `33911612711 = success`.
- NOT READY: direct-read total-deadline product `2270477ccf7631471379774430745f1a81f24d36` plus focused tests `93e83640e69df9016fc4a10ac790e803fecf5d57` and harness correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81` until exact descendant canonical Quality is green.

## Next backend slice

Consume the exact descendant canonical Quality containing `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`. If green, mark direct-read total-deadline enforcement VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact current diagnostics and minimally correct only the remaining Backend-owned failure.
