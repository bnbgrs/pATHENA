# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`.
- Worker branch: `postmerge/backend@58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3` before this handoff update.
- Worker was synchronized to Develop by NON-FORCE fast-forward; no foreign history was rewritten.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Previous backend slice

Durable deletion-ledger runtime boundaries are integrated on Develop and independently closed by the Error worker. Do not reopen that root cause without new evidence.

## Selected backend slice

Area: external network gateway runtime policy boundaries.

Technical/spec anchors:

- `docs/agent_backend_run_201_300.md` identifies `src/athena/external/gateway.py` as a remaining high-value backend hardening target.
- `src/athena/external/gateway.py` is explicitly fail-closed for external authorization, privacy routing, redirects, transport, response policy, auditing and Source capture.
- Existing `tests/unit/test_external_access_gateway.py` pins explicit host scope, Tor-Preferred no-direct-fallback behavior, explicit direct-fallback grants, non-default-port rejection and response-policy failures.

## Confirmed gap

The gateway performs numeric range validation but does not perform exact runtime type validation at all relevant external policy boundaries. In Python, `bool` is a subclass of `int`, so the following malformed runtime values currently pass range checks:

- `authorize_explicit(..., ttl_seconds=True)` is accepted as a one-second authorization;
- `capture_url(..., max_bytes=True)` is accepted as a one-byte response budget;
- `capture_url(..., timeout_seconds=True)` is accepted as a one-second timeout;
- `authorize_direct_fallback(..., ttl_seconds=True)` can likewise flow into its arithmetic/range path.

This is the same class of bool-as-int runtime-boundary defect already hardened in the deletion ledger, but it is a separate ExternalAccessGateway root cause and must not be conflated with the closed deletion error.

Proposed acceptance behavior: fail before authorization persistence, transport selection/network I/O, audit side effects or Source staging when any of these runtime policy parameters has the wrong concrete type or is outside the existing safe range. Preserve the currently documented numerical ranges.

## Call-chain reviewed

`authorize_explicit(runtime policy) -> purpose/route/TTL/host validation -> ensure_local_user -> authorization INSERT -> readback`.

`capture_url(runtime resource policy) -> max_bytes/timeout validation -> _authorized_or_audit -> privacy-route selection -> per-redirect re-authorization -> _fetch_authorized_url -> transport.fetch -> response-policy validation -> final URL authorization -> fsync staging -> transactional Source capture + external audit/provenance finalize`.

`tor_preferred -> tor transport only -> bounded retry -> ExternalDirectApprovalRequired`; there is no silent Tor-to-Direct transport switch.

Direct transport resolves the destination, rejects non-global addresses from the returned resolution set, then connects using that validated set. Redirects are re-authorized before every fetch. `_http_over_socket` reads at most `max_bytes + 1` and raises policy error on overflow.

## Invariants to preserve

- no silent Tor -> Direct fallback;
- explicit Direct fallback remains a separate authorization with host scope and bounded lifetime;
- loopback/local/private destinations remain rejected;
- redirects remain host-scope checked before fetching;
- only HTTPS/default HTTPS port remains permitted at the gateway authorization boundary;
- response-size limit and compressed-response rejection remain fail-closed;
- failed/denied access audit durability remains unchanged;
- successful Source capture keeps fsync staging and transactional audit/provenance finalization;
- no Security, UI, Search composition or deletion-ledger semantics may change.

## Mutation state

No product mutation was made in this run. The available GitHub contents mutation replaces the complete ~1k-line central gateway module; reconstructing that file merely to change several boundary predicates would create unnecessary overwrite risk. A partial/speculative product rewrite was therefore rejected.

No red acceptance test was committed without its product fix. The next safe patch-capable run should add focused bool/wrong-type boundary tests and the minimal exact-type checks together as one bounded slice.

## Tests / evidence

Read-only code review confirms the malformed bool values above through Python runtime semantics and the current predicates. Existing gateway tests were inspected but not executed in this run. No PASS claim is made for new behavior.

There are currently no workflow runs associated with exact Develop SHA `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3` through the available commit-workflow query, so no current-Develop global Quality claim is made.

## Coordination

- `postmerge/errors`: no open Backend root cause currently collides with this slice. Allocate a new ERR ID only if a real failing runtime/CI signature is independently observed; this proactive hardening gap is not being mislabeled as a historical error.
- `postmerge/spec-core`: owns normal-Hybrid Search facade/application composition; do not touch it here.
- `postmerge/ui`: owns 11-screen/PALLAS visual and interaction work; do not touch it here.
- `develop/pathena-next`: integration target only; Backend never self-integrates.

## Integrator handoff

NOT READY as a product slice. This commit is repository handoff/evidence only. Do not integrate it as implementation of gateway hardening.

## Next backend slice

Implement exact-type, fail-before-side-effect validation for ExternalAccessGateway TTL, response-byte budget and timeout parameters; add focused regression coverage for bool/wrong-type values and existing boundary values; run `tests/unit/test_external_access_gateway.py` plus the new focused boundary tests and relevant network/security regressions. If green, update this handoff with the product/test commit SHAs and mark Integrator-ready. After that, continue to the next unclaimed Backend/System P0/P1/P2 gap rather than stopping.
