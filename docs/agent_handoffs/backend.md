# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@e98c88e0d3b41b81de7efa70873729f873038080`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `c6d9569cd1bcb80a7b0a46dcb5003e0f680ecff3` with parents previous Backend head and current Develop.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Closed Gateway boundary lineage

The worker retains the previously focused-verified Gateway hardening for:

- explicit TTL / capture max-bytes / timeout runtime boundaries;
- explicit authorization purpose and allowed-host container/element validation;
- privacy-route runtime text validation;
- explicit Direct-fallback host runtime text validation.

No Tor→Direct silent fallback, redirect, destination, audit, Source capture, fsync, transactional provenance, retry, recovery, storage or platform-path invariant was weakened.

## Current completed slice — Direct fallback TTL range

Current code previously rejected non-integer `ttl_seconds` before authorization lookup, but integer values `<= 0` or `> 900` still reached `get_authorization()` and actor/source-state checks before the later `effective_ttl` calculation. This violated the established fail-before-side-effect runtime-boundary pattern.

Product/test commit: `6b6498e36959e044c874b9c17b31b4f547febd0b`.

The bounded mutation changes only `authorize_direct_fallback()` TTL validation from exact-type-only to exact integer range `1..900` before `get_authorization()`. Valid values retain the existing `min(requested_ttl, remaining_source_lifetime, 900)` semantics; therefore the source authorization lifetime can still shorten an otherwise valid request.

Focused tests add:

- `0`, `-1`, `901`, and `10000` rejection before authorization lookup;
- valid boundary values `1` and `900` preserving creation of a separate `direct_explicit` authorization.

## Call-chain / failure boundary

`authorize_direct_fallback(runtime input) -> host text guard -> TTL exact-type/range 1..900 guard -> source authorization lookup -> actor -> active Tor-Preferred checks -> host scope/safety -> remaining-source-lifetime bound -> explicit Direct authorization`.

Malformed or out-of-range TTL now fails with `ExternalAuthorizationError` before source/actor lookup. Valid TTL still cannot exceed either 900 seconds or the remaining lifetime of the original Tor-Preferred grant.

## Verification

Temporary worker-only verifier run `33813211483` completed SUCCESS. Exact successful steps:

- install project PASS;
- deterministic bounded patch application PASS;
- focused Gateway suites PASS: `test_external_access_gateway_authorization_boundaries.py`, `test_external_access_gateway_runtime_boundaries.py`, `test_external_access_gateway.py`;
- Ruff on changed Gateway/test files PASS;
- mypy on `src/athena/external/gateway.py` PASS;
- `git diff --check` PASS;
- product/test commit + NON-FORCE push PASS.

The first verifier run `33813121816` already had focused tests, Ruff and mypy PASS but stopped at `git diff --check` because the temporary writer emitted an extra EOF blank line; it therefore created no product commit. The writer was normalized and the full verification rerun successfully without changing product/test semantics.

## Commits

- Develop synchronization: `c6d9569cd1bcb80a7b0a46dcb5003e0f680ecff3`.
- Temporary verifier add/fix: `bb9e15830f89d8f22a77bb45c910a285ac536d6f`, `35acaa2202e023ad1c4e2371217d4b0b42afa2c4` — tooling only, do not integrate.
- Product + focused tests: `6b6498e36959e044c874b9c17b31b4f547febd0b`.
- Temporary verifier removal: `eeaeb32e07ddd18b1446d57b37ac76df710114c3`.

## Integrator handoff

`6b6498e36959e044c874b9c17b31b4f547febd0b` is `BOUNDED_FOCUSED_VERIFIED`. Independently review and integrate only its product/test delta, preserving the preceding Backend Gateway boundary state. Do not integrate temporary verifier workflow history. Canonical Quality evidence must be treated separately from the focused verifier; no global PASS is claimed here unless an exact relevant canonical run completes successfully.

## Coordination

- Error worker: no new Backend-owned regression signature from focused verification.
- Core: no Core files changed.
- UI: no UI/Qt files changed.
- Main remains unchanged.

## Next backend slice

Trace the next evidence-backed Backend/System runtime boundary on current Develop. First candidate to verify is `capture_url()` URL runtime typing/fail-before-authorization-audit behavior: resource limits are validated before lookup, but malformed non-text URL input may still reach authorization/audit lookup before URL parsing rejects it. Only mutate if reproduced and supported by the existing external-access contract; otherwise move to the highest current Research/Jobs/Storage/Recovery/Provider/Packaging gap.
