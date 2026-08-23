# pATHENA Threat Model

This is the working security model for `agent/pathena`. It records concrete trust boundaries and verified invariants so security work follows real code paths instead of hypothetical features.

Last reviewed baseline: current `agent/pathena` after security coordination commits on 2026-08-23.

## Security goals

1. Local-first data must not leave the machine unless a concrete network action is authorized by the applicable policy.
2. Tor-selected traffic must not silently downgrade to direct clearnet transport or local DNS resolution.
3. External content and URLs are untrusted input and must not gain access to loopback/private networks, local files, command execution, or unrestricted storage.
4. The local Core API must remain loopback-only and require an unguessable per-runtime credential.
5. Secrets, private knowledge, prompts, source content and credentials must not be exposed through logs, provenance metadata, temporary files or weak filesystem permissions.
6. Cryptography must use established libraries/primitives with authenticated encryption and explicit key-management semantics; no custom cryptography.
7. Updates, dependencies and downloaded artifacts must preserve origin/integrity guarantees appropriate to their privilege.
8. Persisted cryptographic work factors must be resource-bounded before invoking expensive primitives so corrupted metadata cannot create avoidable local denial of service.
9. Durable spool/archive/backup writes must remain confined beneath their configured storage roots even if hostile symlink/junction/reparse-point ancestors are present.

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
- Windows bootstrap defaults `ATHENA_LOCAL_ROOT` beneath per-user LocalApplicationData and rejects repository-local runtime roots, but its preflight currently verifies writability rather than DACL confidentiality.

**Open risk:** `SEC-001` — POSIX `0600` is not equivalent to a private Windows DACL; the confidentiality invariant of the bearer-token file must be proven on Windows, including explicitly overridden local roots.

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

**Required invariant:** no alternate network adapter may bypass the selected Tor policy. Each newly discovered HTTP/WebSocket/provider path must be traced back to the network policy before being considered covered. `SEC-003` tracks the current LM Studio ambient-proxy exception to the local-only provider boundary.

### External source / imported file -> parsers and persistence

**Assets:** local filesystem, database integrity, execution environment, durable knowledge.

**Verified controls so far:**
- Native DOCX parsing uses `zipfile` only as a container reader and does not extract ZIP members to filesystem paths.
- Native DOCX reads only required OOXML parts and enforces uncompressed-size limits plus a compression-ratio ceiling before reading the main document/styles parts.
- Native HTML parsing caps input bytes, tree depth, node count and attribute length, treats script/style/template/iframe-like elements as excluded data, and performs no browser execution.
- Native PDF parsing is supervised in a disposable Python child launched as an argument vector with `-I` and no shell. Input bytes, pages, output bytes, process memory and wall-clock time are bounded; Windows uses a Job Object memory limit and POSIX applies an address-space limit in the worker.
- PDF child IPC is framed and independently range-checked by the parent before the result is accepted.

**Threats to continue scanning:** SSRF through nested URLs, parser bombs/DOM amplification inside accepted limits, filename/path injection, unsafe temporary files, and equivalent boundaries in remaining parsers/importers.

**Current status:** DOCX/HTML/PDF native parser boundaries have been statically traced; this is not a blanket claim about every import path or parser dependency vulnerability.

### Raw Source bytes -> Durable Spool / Archive Root

**Assets:** source bytes, filesystem confinement, integrity of content-addressed storage.

**Verified controls:**
- imported source paths reject a symlink at the requested leaf and are copied through exclusive random staging files while SHA-256 and byte length are computed;
- capture detects size/mtime changes during the copy;
- content-addressed blobs are hash-verified before durable publication;
- read/purge enumeration paths contain root-containment and symlink checks.

**Open risk:** `SEC-006` — the blob write path `_copy_into_root()` does not currently prove that existing hash-prefix ancestors are non-link directories confined beneath the configured root. A hostile local filesystem mutation can therefore redirect a later write through a symlink/junction/reparse-point ancestor. Required invariant: resolve/validate the destination parent under the configured root immediately before temp creation and again before publication, with Windows reparse-point coverage where executable.

### Backup target -> isolated restore root

**Assets:** restored database, Raw Source replicas, live runtime isolation, destination filesystem.

**Verified controls:**
- restore requires an absolute destination that does not overlap live roots or the backup target and requires the destination to be absent;
- backup manifest hash and completion marker are verified before restore;
- manifest object paths are canonicalized through `_safe_relative()` and content-addressed object paths must match their declared digest;
- `_safe_existing_file()` resolves backup object sources beneath the backup target and rejects leaf symlinks;
- copied database/blob content is hash-checked and the restored SQLite database undergoes integrity, foreign-key and schema checks before atomic publication.

**Threats to continue scanning:** ancestor-link races on destination/target paths, Windows reparse-point behavior, manifest/resource amplification, and retention/GC deletion confinement.

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

**Current status:** local API token path reviewed. Current bootstrap settings expose no provider API-key field; broader provider/keyring and future credential-storage paths must be re-traced when introduced.

### Repository / dependencies -> build and runtime

**Assets:** executable code and packaged application.

**Verified controls:**
- `pyproject.toml` exactly pins build/runtime/dev package versions and the required `uv` resolver version.
- `uv.lock` records artifact hashes and CI validates the lock then invokes `uv run --locked`.
- Workflow `permissions` are reduced to `contents: read` in the reviewed workflows.

**Open risk:** `SEC-005` — executable GitHub Actions are referenced by mutable major-version tags instead of immutable reviewed commit SHAs.

**Current direct runtime dependencies reviewed in `pyproject.toml`:** `cryptography`, `pypdf`, `numpy`, `usearch`, and `tzdata`; desktop adds `PySide6-Essentials`. Earlier references to `httpx[socks]`/`keyring` are no longer part of the current manifest and must not be treated as current attack surface without code/dependency evidence.

**Threats to continue scanning:** known dependency vulnerabilities, release/artifact signing and origin, installer/update behavior, CI secret exposure, and immutable Action pinning.

## Adversaries considered

- Malicious or compromised external website/source.
- Untrusted document/file imported by the user.
- Network attacker on a clearnet path.
- Local unprivileged process or another local user able to inspect or mutate incorrectly protected runtime/storage files.
- Malicious dependency/update artifact.
- Accidental application behavior that bypasses offline/Tor/network policy.

Out of scope for normal application hardening: an administrator/root attacker with unrestricted access to the user's process memory and files. pATHENA should still avoid making such compromise easier, but cannot promise secrecy against a fully privileged local attacker.

## Verification discipline

- A control is `VERIFIED` only for the concrete code path and commit inspected/tested.
- Any relevant code, dependency or configuration change marks that surface for re-check.
- Active exploit tests are restricted to local fixtures/isolated pATHENA runtimes.
- Security findings and handoffs live in `docs/agent_coordination/security_queue.md` under stable `SEC-###` identifiers.