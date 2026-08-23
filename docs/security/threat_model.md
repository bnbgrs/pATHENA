# pATHENA Threat Model

This is the working security model for `agent/pathena`. It records concrete trust boundaries and verified invariants so security work follows real code paths instead of hypothetical features.

Last reviewed baseline: `a9a9c44464b29b0dd9962a1d5d77b7104cecdc07` (2026-08-23).

## Security goals

1. Local-first data must not leave the machine unless a concrete network action is authorized by the applicable policy.
2. Tor-selected traffic must not silently downgrade to direct clearnet transport or local DNS resolution.
3. External content and URLs are untrusted input and must not gain access to loopback/private networks, local files, command execution, or unrestricted storage.
4. The local Core API must remain loopback-only and require an unguessable per-runtime credential.
5. Secrets, private knowledge, prompts, source content and credentials must not be exposed through logs, provenance metadata, temporary files or weak filesystem permissions.
6. Cryptography must use established libraries/primitives with authenticated encryption and explicit key-management semantics; no custom cryptography.
7. Updates, dependencies and downloaded artifacts must preserve origin/integrity guarantees appropriate to their privilege.

## Trust boundaries

### Desktop UI -> local Core API

**Assets:** chats, knowledge, jobs, settings, provider configuration, shutdown/control operations.

**Boundary:** an HTTP listener bound to `127.0.0.1` plus a random bearer token published in the runtime directory.

**Verified controls:**
- `CoreApiServer` refuses non-`127.0.0.1` bind hosts.
- Request bodies are bounded and ambiguous/multiple Content-Length and chunked bodies are rejected by the local transport.
- `CoreApiAsgiApp` rejects requests carrying an `Origin` header by default and requires bearer authentication.
- `LocalApiRuntime.authenticate()` uses `hmac.compare_digest`.
- Runtime token publication uses exclusive staging, symlink-ancestor checks and durable replacement.

**Open risk:** `SEC-001` — POSIX `0600` is not equivalent to a private Windows DACL; the confidentiality invariant of the bearer-token file must be proven on Windows.

### Core -> Internet / clearnet

**Assets:** query terms, source URLs, prompts or derived research metadata, downloaded source bytes.

**Boundary:** `ExternalFetchGateway` and any other provider/network adapters discovered in later scans.

**Verified controls in gateway path:**
- explicit scheme/host/port approval binding;
- URL userinfo rejection;
- loopback/private/link-local/reserved destination rejection;
- direct DNS resolution validated before connecting, with validated addrinfos frozen into the connection to reduce DNS rebinding;
- bounded redirects with re-authorization per hop;
- response-size cap;
- provenance redaction for query keys that look like tokens/keys/secrets/passwords.

**Open risk:** `SEC-002` — explicitly approved plaintext `http://` is supported; product intent must be verified before enforcing HTTPS-by-default.

### Core -> Tor / SOCKS proxy

**Assets:** destination hostname, request metadata/content, Tor-stream linkability.

**Verified controls:**
- SOCKS proxy is constrained to loopback by default;
- hostname resolution is delegated to the proxy rather than performed locally;
- per-request SOCKS credentials provide stream isolation;
- Tor-preferred behavior fails closed rather than silently falling back to direct networking when Tor is unavailable.

**Required invariant:** no alternate network adapter may bypass the selected Tor policy. Each newly discovered HTTP/WebSocket/provider path must be traced back to the network policy before being considered covered.

### External source / imported file -> parsers and persistence

**Assets:** local filesystem, database integrity, execution environment, durable knowledge.

**Threats to continue scanning:** SSRF through nested URLs, archive/path traversal, unsafe deserialization, parser bombs, excessive response/import size, filename/path injection, unsafe temporary files, subprocess invocation, template/code execution.

**Current status:** partially reviewed only; no blanket safety claim.

### Configuration / credentials -> filesystem and OS secret store

**Assets:** provider API keys, local API tokens, encryption keys, Tor/proxy credentials.

**Threats to continue scanning:** plaintext config, accidental logging, weak Windows ACLs, backup inclusion, crash-dump exposure, stale temp files, unsafe migration/rotation.

**Current status:** local API token path reviewed; provider/keyring and encryption-at-rest paths remain to be traced.

### Repository / dependencies -> build and runtime

**Assets:** executable code and packaged application.

**Threats to continue scanning:** dependency vulnerabilities, unpinned or mutable download sources, artifact integrity, release signing, unsafe installer/update behavior, CI secret exposure.

**Current status:** dependency manifest exists (`pyproject.toml` includes `cryptography`, `httpx[socks]`, `keyring`, PySide6 and related runtime dependencies); supply-chain and release verification remains open.

## Adversaries considered

- Malicious or compromised external website/source.
- Untrusted document/file imported by the user.
- Network attacker on a clearnet path.
- Local unprivileged process or another local user able to inspect incorrectly protected runtime files.
- Malicious dependency/update artifact.
- Accidental application behavior that bypasses offline/Tor/network policy.

Out of scope for normal application hardening: an administrator/root attacker with unrestricted access to the user's process memory and files. pATHENA should still avoid making such compromise easier, but cannot promise secrecy against a fully privileged local attacker.

## Verification discipline

- A control is `VERIFIED` only for the concrete code path and commit inspected/tested.
- Any relevant code, dependency or configuration change marks that surface for re-check.
- Active exploit tests are restricted to local fixtures/isolated pATHENA runtimes.
- Security findings and handoffs live in `docs/agent_coordination/security_queue.md` under stable `SEC-###` identifiers.
