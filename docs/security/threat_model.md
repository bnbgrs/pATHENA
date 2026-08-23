# pATHENA Threat Model

Working security model for `agent/pathena`. It records concrete trust boundaries and verified invariants so security work follows real code paths instead of hypothetical features.

Last reviewed baseline: current remote `agent/pathena` on 2026-08-23.

## Security goals

1. Local-first data must not leave the machine unless a concrete network action is authorized by policy.
2. Tor-selected traffic must not silently downgrade to direct clearnet transport or local DNS resolution.
3. External content and URLs are untrusted and must not gain access to loopback/private networks, local files, command execution or unrestricted storage.
4. The local Core API must remain loopback-only and require an unguessable per-runtime credential.
5. Secrets, private knowledge, prompts, source content and credentials must not leak through logs, provenance, temp files or weak filesystem permissions.
6. Cryptography must use established libraries/primitives with authenticated encryption and explicit key-management semantics; no custom cryptography.
7. Updates, dependencies and downloaded artifacts must preserve origin/integrity guarantees appropriate to their privilege.
8. Persisted cryptographic work factors must be bounded before expensive primitives execute.
9. Durable spool/archive/backup writes and destructive operations must remain confined beneath configured roots even when hostile symlink/junction/reparse-point ancestors can be introduced concurrently.
10. Filesystem confinement checks must bind security decisions to directory/object identity across the sensitive operation; pathname pre-checks alone are not sufficient against check/use replacement races.

## Trust boundaries

### Desktop UI -> local Core API

**Assets:** chats, knowledge, jobs, settings, provider configuration, shutdown/control operations.

**Boundary:** HTTP listener bound to `127.0.0.1` plus random bearer token in the runtime directory.

**Verified controls:** non-loopback bind refusal, bounded/strict request framing, `Origin` rejection, bearer authentication with constant-time comparison, exclusive staged runtime publication and static symlink/reparse checks.

**Open risk:** `SEC-001` — POSIX `0600` is not equivalent to a proven private Windows DACL. The token/discovery directory must be demonstrated to exclude other interactive users on Windows, including overridden runtime roots.

### Core -> Internet / clearnet

**Assets:** query terms, URLs, prompts/derived metadata and downloaded bytes.

**Verified controls in `ExternalFetchGateway`:** explicit scheme/host/port approval binding; URL-userinfo rejection; loopback/private/link-local/reserved destination rejection; validated/frozen direct DNS results; bounded redirects with re-authorization; response-size caps; provenance redaction for sensitive-looking query keys.

**Open risk:** `SEC-002` — explicitly approved plaintext `http://` remains supported; product intent must be resolved before HTTPS-only hardening.

### Core -> Tor / SOCKS proxy

**Assets:** destination hostname, request metadata/content and stream linkability.

**Verified controls:** SOCKS proxy constrained to loopback by default, hostname resolution delegated to SOCKS, per-request isolation credentials and fail-closed behavior rather than silent direct fallback.

**Open risk:** `SEC-003` — LM Studio remains a separate local-only network adapter using ambient `urllib` proxy behavior. Local provider traffic must not be influenced by process/OS HTTP(S) proxy configuration.

### External source / imported file -> parsers and persistence

**Assets:** filesystem, database integrity, execution environment and durable knowledge.

**Verified controls so far:** DOCX uses `zipfile` as a reader without extracting members and applies size/ratio limits; HTML parsing caps bytes/tree/nodes/attribute size and executes no browser code; PDF parsing runs in an isolated supervised child with bounded input/pages/output/time/memory and framed IPC.

**Threats to continue scanning:** nested URL SSRF, parser/resource amplification inside accepted limits, filename/path injection, unsafe temporary files and equivalent boundaries in remaining importers.

### Raw Source bytes -> Durable Spool / Archive Root

**Assets:** source bytes, filesystem confinement and content-addressed storage integrity.

**Verified controls:** source-leaf symlink rejection, exclusive random capture staging, SHA-256/length verification, change detection during capture, static symlink/junction/reparse checks in durable filesystem primitives, content-addressed hash validation, and static root-containment checks in read/enumeration paths.

**Residual write/publication risk — `SEC-006`:** static link/reparse hardening does not close a concurrent path-replacement race. `_copy_into_root()` validates/creates the parent through `durable_mkdir()` and later opens `temp_path` by pathname with `"xb"`. A hostile local actor able to mutate the storage-tree ancestor can swap a validated directory for a symlink/junction after the check but before `open()`. `durable_replace()` re-validates later, but sensitive bytes may already have been written outside the configured root. Required invariant: creation/publication must remain bound to verified parent identity across the operation, not merely re-check the pathname before and after it.

**Residual destructive-operation risk — `SEC-007`:** cleanup/purge/orphan-reconciliation similarly verify by pathname and later hash/unlink by pathname. The ATHENA runtime mutation lock does not exclude an out-of-band filesystem actor. Required invariant: deletion must prove target identity and root confinement at destructive use without traversing attacker-replaceable parent components.

**Implementation direction:** use established identity-safe OS mechanisms. On POSIX prefer dirfd/openat-style no-follow semantics where feasible; on Windows use handle/reparse-safe APIs. Add deterministic race-simulation tests and real Windows junction/reparse tests where executable. Do not treat static symlink tests as proof against TOCTOU replacement.

### Backup target -> isolated restore root

**Assets:** restored database, Raw Source replicas, runtime isolation and destination filesystem.

**Verified controls:** absolute non-overlapping restore destination, absent destination requirement, manifest/completion-marker validation, canonical object paths, content hashes, SQLite integrity/FK/schema validation and atomic publication.

**Threats to continue scanning:** ancestor replacement races on destination/target paths, Windows reparse behavior, resource amplification and retention/GC deletion confinement. Findings SEC-006/007 establish that path-based pre-checks elsewhere are not sufficient evidence for concurrent filesystem mutation safety.

### Protected Content metadata -> KDF / encryption

**Assets:** unlock/recovery availability, Root Key confidentiality and protected payload integrity.

**Verified controls:** pyca/cryptography AES-256-GCM and Argon2id; strict/versioned metadata; invalid metadata converted to integrity errors; v1 Argon2id bounded at 10 iterations, 16 lanes and 256 MiB while production defaults remain 3/4/64 MiB.

**Verification state:** `SEC-004` is FIXED by commits `be5a7f06d2f71f011aae7f30a02671ff9a5ebd18` and `fd700b85dcf8e4cbe7bc6289e7af31203c2fd0b9`; do not promote to VERIFIED without observed green targeted/CI execution.

### Configuration / credentials -> filesystem and OS secret store

**Assets:** provider/API credentials, local API token, encryption keys and proxy/Tor credentials.

**Current status:** local API token path reviewed; current bootstrap settings expose no general provider API-key field. Continue scanning future provider/keyring paths, accidental logging, backups, crash dumps and stale temp files.

### Repository / dependencies -> build and runtime

**Assets:** executable code and packaged application.

**Verified controls:** exact Python dependency pins, artifact-hashed `uv.lock`, locked CI resolution and reduced workflow permissions.

**Open risk:** `SEC-005` — external GitHub Actions are referenced by mutable major tags rather than reviewed immutable SHAs.

**Threats to continue scanning:** known dependency vulnerabilities, installer/update origin/signing, CI secret exposure and release artifact integrity.

## Adversaries considered

- Malicious or compromised external website/source.
- Untrusted imported document/file.
- Network attacker on a clearnet path.
- Local unprivileged process or another local user able to inspect or mutate incorrectly protected runtime/storage files.
- Malicious dependency/update artifact.
- Accidental application behavior that bypasses offline/Tor/network policy.

Administrator/root compromise with unrestricted process-memory/filesystem access remains outside normal application-hardening guarantees, although pATHENA should not unnecessarily increase its impact.

## Verification discipline

- A control is `VERIFIED` only for the concrete path and tested/inspected revision.
- Relevant code, dependency or configuration changes reopen the surface for review.
- Active exploit tests are restricted to isolated local pATHENA fixtures/runtimes.
- Static path checks do not prove resistance to concurrent path replacement.
- Security findings and handoffs live under stable `SEC-###` IDs in `docs/agent_coordination/security_queue.md`.
