# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@0b7f428f8679db9391c00b4b9638d85550332c43`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `9dd82f0c25c6442db79c54b5bf7f756dc35c427c`, parents prior Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` and exact Develop `0b7f428f8679db9391c00b4b9638d85550332c43`.
- `main` remains strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect runtime guards and canonical-harness coverage are present and verified. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Storage Health runtime boundaries — VERIFIED

Storage Health lineage through `19c73aee29cae2d2ea479a6e3d2aa1256afa06a1` is backed by canonical ATHENA Quality `33868034634 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Local model HTTP cumulative response-size boundary — VERIFIED

Product commit `247ff4710a889fdeb8be880b11be1d2cf870eb18` and focused-test commit `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33` make `read()`, `read(-1)` and `readline()` share one response-wide byte budget so repeated explicit reads cannot bypass `MAX_LOCAL_RESPONSE_BYTES`.

Exact descendant Backend head `b025f6de83a969cca10a7677faae0b349e1a2988` contains those product/test blobs unchanged and canonical ATHENA Quality run `33890486614` completed `success` on that exact head.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY` for the cumulative local-response-size lineage through `b025f6de83a969cca10a7677faae0b349e1a2988`.

## Local model HTTP readline remaining-budget hardening — VERIFYING

Adjacent review found that cumulative `readline()` accounting failed closed correctly but still requested up to `max_bytes + 1` bytes from the underlying stream on every call. Once part of the response budget had already been consumed, this could unnecessarily buffer far more than the remaining response allowance before rejection.

Product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386` changes `readline()` to request only `remaining + 1` bytes and rejects any result larger than the remaining budget. The extra byte is retained solely to detect overflow fail-closed.

Focused-test commit `4822b9ed6d84e05ae3d293e362dc9be62b6e844b` verifies that a partially consumed response requests exactly remaining-budget-plus-one and that an exact-limit response probes only one detection byte before rejecting further payload.

Canonical ATHENA Quality run `33895580329` exists for exact test head `4822b9ed6d84e05ae3d293e362dc9be62b6e844b` and was `pending` at handoff update time. No PASS/READY claim is made until it executes and completes green.

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
- READY: local HTTP cumulative response-size lineage through exact head `b025f6de83a969cca10a7677faae0b349e1a2988`, canonical Quality `33890486614 = success`, product/test commits `247ff4710a889fdeb8be880b11be1d2cf870eb18` + `f8001aa04ba969a21ffa06bc9b991c4b3a8c0d33`.
- NOT READY: local HTTP readline remaining-budget hardening `2981624e0f7eef8c2e94b6f0eb86a859132a2386` + `4822b9ed6d84e05ae3d293e362dc9be62b6e844b` until canonical `33895580329` is green.

## Next backend slice

Consume canonical Quality `33895580329`. If green, mark readline remaining-budget hardening VERIFIED/READY and immediately take the highest current unclaimed Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, correct only the exact Backend-owned failure before unrelated mutation.
