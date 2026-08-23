# pATHENA Security Queue

Persistent security queue for `agent/pathena`.

Status values: `FOUND`, `READY`, `IN_PROGRESS`, `BLOCKED`, `FIXED`, `VERIFIED`, `STALE`.

| ID | Priority | Category | Threat / attack surface | Evidence / reproduction | Assets / impact | Ownership | Status | Fix / mitigation | Last verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | P1 | Local API / secrets / Windows ACL | The bearer token for the loopback Core API is persisted to `core-api.token`; `_write_private_text()` requests mode `0o600`, but Windows does not provide POSIX permission-bit isolation equivalent to a private DACL. A second local account/process with filesystem access to the runtime root could reuse the bearer token and obtain the authenticated local API surface. | `src/athena/api/runtime.py`: `LocalApiRuntime.publish()` writes a 48-byte-url-safe bearer token; `_write_private_text()` creates/chmods the file with `_PRIVATE_MODE = 0o600`. `src/athena/api/asgi.py` authenticates API requests solely with that bearer token. Static verification on HEAD `f8eeac0e8456ff3e168b99c846fdd54a17b9bb31`; no claim that a real Windows ACL exploit was executed. | Local chat/knowledge/jobs/system API and shutdown capability when enabled. Impact depends on inherited Windows ACL of the runtime directory. | SECURITY/RELEASE | READY | Define and regression-test a Windows runtime-root invariant: token/discovery state must live under a per-user directory whose DACL excludes other interactive users; if current runtime-root construction cannot guarantee this, add Windows ACL hardening using an established OS/API library rather than emulating POSIX modes. Preserve symlink/reparse-point protections. | 2026-08-23, static code-path verification at HEAD `f8eeac0e8456ff3e168b99c846fdd54a17b9bb31` |
| SEC-002 | P2 | External transport policy | `ExternalFetchGateway` supports both `http://` and `https://`; therefore an explicitly authorized direct request may send request metadata and receive content over plaintext HTTP. This is not an authorization bypass and may be intentional because current capability text describes HTTP(S), but it is a hardening/policy gap for sensitive research workflows. | `src/athena/external/gateway.py` allows schemes `{http, https}` and uses TLS only for `https`. Approval binding, SSRF checks, DNS rebinding resistance and response limits still apply. | Network confidentiality/integrity for explicitly approved clearnet HTTP destinations. | SECURITY/FEATURE | FOUND | Verify product/spec intent before mutation. Preferred hardening if compatible: HTTPS-only default with an explicit, high-friction opt-in for plaintext HTTP and provenance marking of insecure transport. Do not silently rewrite HTTP to HTTPS. | 2026-08-23, static gateway review at HEAD `f8eeac0e8456ff3e168b99c846fdd54a17b9bb31` |

## Verified baseline controls

These controls were inspected so future runs do not repeatedly rediscover them without a relevant code change:

- `ExternalFetchGateway` direct mode rejects loopback/private/link-local/reserved targets and freezes validated DNS results into the socket connection, reducing SSRF and DNS-rebinding risk.
- Tor mode delegates hostname resolution to SOCKS, uses per-request stream-isolation credentials, restricts the proxy endpoint to loopback by default, and fails closed instead of silently falling back to direct networking.
- Direct and Tor HTTPS paths use Python's default TLS context with certificate and hostname validation; no `verify=False` or permissive SSL context was found in the reviewed gateway path.
- Redirects are bounded and re-authorized per hop; response bytes are capped; URL userinfo is rejected; sensitive-looking query values are redacted from recorded provenance.
- Core API listener is hard-coded to IPv4 loopback (`127.0.0.1`), refuses alternate bind hosts, caps request bodies, rejects browser `Origin` requests, and requires a random bearer token using constant-time comparison.
- API runtime publication rejects symlink ancestors, uses exclusive staging files, durable replacement and best-effort cleanup.

## Handoffs

- `SEC-001`: coordinate with Windows/Release ownership when such a queue exists; Security owns the invariant/test and may implement a narrowly isolated ACL helper only after confirming the runtime-root construction and available Windows APIs.
- `SEC-002`: Feature/Specification decision required before changing the externally visible HTTP(S) contract. Security should not remove HTTP support unilaterally.
