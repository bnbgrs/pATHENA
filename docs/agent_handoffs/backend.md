# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@647ea036329280378a7e573aca0df905f48ac3b1`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `899d37e93be6590d4fcec423e88d31abea31b4e6`, retaining Backend work while taking current Develop, including the integrated temporal contradiction policy.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Prior Gateway slices

- TTL/max-bytes/timeout runtime hardening is already integrated on Develop and remains closed.
- `authorize_explicit()` purpose/allowed-host boundaries remain present on this worker as product commit `7fb68f20e48a463282c4f29e08c531cadc71b60b`, focused verified and pending independent Integrator acceptance.

## Current selected slice

Area: ExternalAccessGateway privacy-route and explicit direct-fallback host runtime boundaries.

Current-code evidence after synchronization showed two concrete fail-closed gaps:

1. `authorize_explicit()` performed `privacy_route not in {…}` without first requiring text. An unhashable runtime value such as `[]` or `{}` could therefore escape as a generic `TypeError` instead of the Gateway authorization error contract.
2. `authorize_direct_fallback()` performed source authorization lookup and actor resolution before normalizing `host`. A non-text runtime host could therefore reach authorization/actor reads before its invalid type was rejected.

Product commit: `6a2d920630df5f5ca921369fe249310110b79270`.

The bounded product mutation adds:

- exact runtime text validation for `privacy_route` before set membership / transport-route resolution;
- exact runtime text validation for explicit direct-fallback `host` before `get_authorization()` and actor resolution;
- focused tests proving malformed privacy-route inputs fail before actor/persistence and malformed fallback-host inputs fail before authorization lookup.

No Tor/Direct policy, redirect handling, authorization scope, destination safety, audit, Source capture, fsync, transaction, provenance, retry, recovery or platform-path semantics changed.

## Call-chain / failure boundary

`authorize_explicit(runtime input) -> purpose/host-container validation -> privacy_route text guard -> route allow-list / transport availability -> TTL guard -> host normalization/safety -> actor -> authorization persistence`.

`authorize_direct_fallback(runtime input) -> host text guard -> TTL exact-type guard -> source authorization lookup -> actor -> active Tor-Preferred checks -> host scope/safety -> bounded effective TTL -> explicit Direct authorization`.

Malformed route or fallback-host runtime values now fail with `ExternalAuthorizationError` before the first actor/persistence or source-authorization lookup boundary relevant to that invalid input.

## Verification

Because the local checkout path still could not resolve `github.com`, verification used a temporary worker-only GitHub Actions runner. Initial workflow-definition attempts failed before job creation and produced no product mutation. The corrected runner executed the actual bounded slice.

Focused run `33808355340` completed SUCCESS. Its predecessor `33808249465` had already established the same product/tests as green but was stopped only by `git diff --check` detecting one writer-created blank line at EOF; the writer was corrected without changing test semantics.

Exact successful verification for the final committed slice:

- dependency lock check PASS;
- focused Gateway suites PASS: `36 passed` across `test_external_access_gateway_authorization_boundaries.py`, `test_external_access_gateway_runtime_boundaries.py`, and `test_external_access_gateway.py`;
- Ruff on Gateway plus boundary tests PASS;
- mypy on `src/athena/external/gateway.py` PASS;
- `git diff --check` PASS before product commit;
- bounded product/test commit and NON-FORCE push PASS.

Canonical Quality run `33808413391` associated with the bot-created product commit concluded `action_required` with no jobs, so it is not PASS evidence and does not indicate a product/test failure. Focused execution remains the concrete verification evidence for this slice.

## Commits

- Develop synchronization: `899d37e93be6590d4fcec423e88d31abea31b4e6`.
- Temporary runner/debug commits: `e9f9e080bb153e087fd2e69e282e6c1c9fcb90a6`, `0e1773853e6621f410683eeaafd1e77dcfb75c33`, `48f97141836fbaa3837cdcfeed509f8dc50e5a15`, `bda51d110ecefdab294728a1d9c9cb061358c324`, `443716c4572859352220c3c54aa8fc838fa3fed0` — tooling only, do not integrate.
- Product + focused tests: `6a2d920630df5f5ca921369fe249310110b79270`.
- Temporary runner removal: `0a5a0a3d6afa2da6e3be6cffb35f3b2779ef51ea`.

## Integrator handoff

`6a2d920630df5f5ca921369fe249310110b79270` is `BOUNDED_FOCUSED_VERIFIED` and ready for independent diff review. Integrate only the bounded product/test delta from `src/athena/external/gateway.py` and `tests/unit/test_external_access_gateway_authorization_boundaries.py`; do not integrate temporary runner history. Preserve the earlier purpose/allowed-host boundary slice and all integrated Gateway invariants.

## Coordination

- Error worker: no new Backend-owned regression signature was produced by focused tests.
- Core: current Develop temporal-contradiction changes are included through the synchronization merge; no overlap with Gateway files.
- UI: no UI/Qt files touched.
- Main remains unchanged.

## Next backend slice

Verify the remaining explicit-direct-fallback TTL range boundary on current code. `ttl_seconds` currently rejects non-int types before source/actor lookup, but zero/negative or excessively large integer values can still traverse source authorization and actor checks before the later effective-TTL calculation. If reproduced, add a minimal fail-before-lookup range guard while preserving the 900-second cap and remaining-source-lifetime semantics; otherwise move to the next evidence-backed Research/Jobs/Storage/Recovery/Provider/Packaging P0/P1/P2 gap.
