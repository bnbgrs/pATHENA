# pATHENA Threat Model

This is the working security model for `agent/pathena`. It records concrete trust boundaries and verified invariants so security work follows real code paths instead of hypothetical features.

Last reviewed baseline: `c147a2a31ddff822a63e91c56ef7851006d34892` (2026-08-23).

## Security goals

1. Local-first data must not leave the machine unless a concrete network action is authorized by the applicable policy.
2. Tor-selected traffic must not silently downgrade to direct clearnet transport or local DNS resolution.
3. External content and URLs are untrusted input and must not gain access to loopback/private networks, local files, command execution, or unrestricted storage.
4. The local Core API must remain loopback-only and require an unguessable per-runtime credential.
5. Secrets, private knowledge, prompts, source content and credentials must not be exposed through logs, provenance metadata, temporary files or weak filesystem permissions.
6. Cryptography must use established libraries/primitives with authenticated encryption and explicit key-management semantics; no custom cryptography.
7. Updates, dependencies and downloaded artifacts must preserve origin/integrity guarantees appropriate to their privilege.
8. Persisted cryptographic work factors must be resource-bounded before invoking expensive primitives so corrupted metadata cannot create avoidable local denial of service.

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

**Verified controls so far:**
- Native DOCX parsing uses `zipfile` only as a container reader and does not extract ZIP members to filesystem paths.
- Native DOCX reads only required OOXML parts and enforces uncompressed-size limits plus a compression-ratio ceiling before reading the main document/styles parts.

**Threats to continue scanning:** SSRF through nested URLs, parser bombs/DOM amplification, excessive response/import size, filename/path injection, unsafe temporary files, subprocess invocation, template/code execution, and equivalent boundaries in PDF/HTML/other parsers.

**Current status:** partially reviewed only; no blanket safety claim.

### Protected Content metadata -> KDF / encryption

**Assets:** availability of unlock/recovery, Root Key confidentiality, protected payload integrity.

**Verified controls:**
- AES-256-GCM and Argon2id come from pyca/cryptography; there are no custom cryptographic primitives in the reviewed path.
- Password-slot Argon2id metadata is strict/versioned JSON and invalid metadata is converted by the repository to a security integrity error.
- v1 Argon2id parameters are bounded before KDF construction: maximum 10 iterations, 16 lanes and 256 MiB memory, while the production default remains 3 / 4 / 64 MiB.
- Boundary tests exercise ceilings and pathological JSON without allocating the pathological work factors.

**Verification state:** `SEC-004` is FIXED in commits `be5a7f06d2f71f011aae7f30a02671ff9a5ebd18` and `fd700b85dcf8e4cbe7bc6289e7af31203c2fd0b9`; promote to VERIFIED only after targeted/CI execution succeeds.

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
