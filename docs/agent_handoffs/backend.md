# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@c91e76804e74595f92c8eb624ce7c5d83b66bad2`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `7cc4f9fe7dd176638f5c1ac747fd0238c73b80c0`, with parents prior Backend head `7688f49ea351749bf227a1683fd14aba719d9bb6` and exact Develop `c91e76804e74595f92c8eb624ce7c5d83b66bad2`.
- `main` remains strict read-only and untouched.
- Required handoffs reviewed before mutation: `errors.md`, `spec-core.md`, `ui.md`, `integrator.md`, plus Backend worker state.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage Health runtime boundaries — VERIFIED

Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` is backed by canonical ATHENA Quality `33868034634 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP cumulative response-size boundary — VERIFIED

Product `247ff4710a889fdeb8be880b11be1d2cf870eb18` and tests `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` share one response-wide byte budget across `read()`, `read(-1)` and `readline()`. Exact descendant Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` passed canonical Quality `33890486614 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP readline remaining-budget hardening — ERR-0009 CORRECTED / VERIFYING

Product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386` makes `readline()` request only `remaining + 1` bytes, retaining one detection byte for fail-closed overflow handling.

Canonical Quality `33906351499` on synchronized Backend head `7688f49ea351749bf227a1683fd14aba719d9bb6` executed four real jobs. Windows path safety, Linux storage regressions and local-install smoke passed; validator, Ruff and mypy passed; full pytest failed exactly two stale LM Studio response-limit expectations. Diagnostics reported `4615 passed, 3 skipped` plus the two failures:

- `test_stream_iteration_uses_bounded_readline_without_whole_body_read`: actual `[17, 9, 2]`, stale expected `[17, 17, 17]`;
- `test_stream_iteration_rejects_many_small_lines_over_cumulative_limit`: actual `[9, 5, 1]`, stale expected `[9, 9, 9]`.

Integrator independently classified this as `ERR-0009`: the product security guard is correct and must not be reverted.

Harness-only correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e` updates those two expectations to the real remaining-budget sequence. No production file changed in this fix. Exact canonical green evidence for this correction is still required before READY.

## Invariants retained

- local model HTTP transport remains loopback-only and proxy-free;
- redirect rejection and timeout validation remain unchanged;
- response-size enforcement remains fail-closed and is strengthened without new retries, routing or cryptography;
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
- NOT READY: local HTTP readline remaining-budget product `2981624e0f7eef8c2e94b6f0eb86a859132a2386` plus ERR-0009 harness correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e` until an exact descendant canonical Quality run is green.

## Next backend slice

Consume exact canonical evidence containing `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`. If green, mark the readline remaining-budget lineage VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, correct only the exact remaining Backend-owned failure before unrelated mutation.
