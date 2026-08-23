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
8. Persisted cryptographic work factors and security/recovery metadata must be resource-bounded before expensive allocation/parsing executes.
9. Durable spool/archive/backup/migration writes and destructive operations must remain confined beneath configured roots even when hostile symlink/junction/reparse-point ancestors can be introduced concurrently.
10. Filesystem confinement and lock decisions must bind to stable directory/object identity across the full sensitive operation; pathname pre-checks alone are not sufficient against check/use replacement races.

## Trust boundaries

### Desktop UI -> local Core API

**Assets:** chats, knowledge, jobs, settings, provider configuration, shutdown/control operations.

**Boundary:** HTTP listener bound to `127.0.0.1` plus random bearer token in the runtime directory.

**Verified controls:** non-loopback bind refusal, bounded/strict request framing, `Origin` rejection, bearer authentication with constant-time comparison, static symlink/junction/reparse checks through the shared storage boundary predicate, and private runtime publication through the shared durable writer.

**Open risks:** `SEC-001` — POSIX `0600` is not equivalent to a proven private Windows DACL. The token/discovery directory must be demonstrated to exclude other interactive users on Windows, including overridden runtime roots. `SEC-012` — the API layer now delegates token/discovery writes to `durable_write_bytes()`. On POSIX that primitive binds create/write/publish to an opened parent directory FD and verifies parent identity, closing the secret-write parent-replacement race for that platform. The Windows branch of the shared primitive still creates the temporary file by pathname after static parent validation, so Windows remains open until equivalent handle/reparse-safe semantics are implemented.

**Recent hardening:** `SEC-011` replaced symlink-only runtime-root/ancestor checks with `is_link_boundary()`, covering Windows junctions/reparse points. Security commits `39c7b1aee5407b7537ea808070631e53ae2f5e67` and `ba05a63a7cf1002d111d2f2f28ecc90310e600cc` moved local API private publication onto `durable_write_bytes()` and added fail-closed API regression coverage for a rejected parent identity. Do not claim Windows closure until the shared Windows writer is identity-bound and executed there.

### Core -> Internet / clearnet

**Assets:** query terms, URLs, prompts/derived metadata and downloaded bytes.

**Verified controls in `ExternalFetchGateway`:** explicit scheme/host/port approval binding; URL-userinfo rejection; loopback/private/link-local/reserved destination rejection; validated/frozen direct DNS results; bounded redirects with re-authorization; response-size caps; provenance redaction for sensitive-looking query keys.

**Open risk:** `SEC-002` — explicitly approved plaintext `http://` remains supported; product intent must be resolved before HTTPS-only hardening.

### Core -> Tor / SOCKS proxy

**Assets:** destination hostname, request metadata/content and stream linkability.

**Verified controls:** SOCKS proxy constrained to loopback by default, hostname resolution delegated to SOCKS, per-request isolation credentials and fail-closed behavior rather than silent direct fallback.

**Open risk:** `SEC-003` — LM Studio remains a separate local-only network adapter using ambient `urllib` proxy behavior. Current `LMStudioProvider` still calls the default `urlopen()` path for local discovery/chat/structured requests. Local provider traffic must not be influenced by process/OS HTTP(S) proxy configuration.

### External source / imported file -> parsers and persistence

**Assets:** filesystem, database integrity, execution environment and durable knowledge.

**Verified controls so far:** DOCX uses `zipfile` as a reader without extracting members and applies size/ratio limits; HTML parsing caps bytes/tree/nodes/attribute size and executes no browser code; PDF parsing runs in an isolated supervised child with bounded input/pages/output/time/memory and framed IPC.

**Threats to continue scanning:** nested URL SSRF, parser/resource amplification inside accepted limits, filename/path injection, unsafe temporary files and equivalent boundaries in remaining importers.

### Raw Source bytes -> Durable Spool / Archive Root

**Assets:** source bytes, filesystem confinement and content-addressed storage integrity.

**Verified controls:** source-leaf symlink rejection, exclusive random capture staging, SHA-256/length verification, change detection during capture, static symlink/junction/reparse checks in durable filesystem primitives, content-addressed hash validation, root-containment checks, and POSIX identity-bound publication in `durable_replace()`.

**Residual write/publication risk — `SEC-006`:** `_copy_into_root()` still creates/writes its temporary blob by pathname before the later identity-bound publication step. A hostile local actor able to mutate the storage-tree ancestor can therefore race the temp-file creation. Required invariant: temp creation itself must be bound to verified parent identity before any source bytes are written. Current POSIX durable replace is a useful partial mitigation but occurs too late to close this risk.

**Residual destructive-operation risk — `SEC-007`:** cleanup/purge/orphan-reconciliation verify by pathname and later hash/unlink by pathname. The ATHENA runtime mutation lock does not exclude an out-of-band filesystem actor. Required invariant: deletion must prove target identity and root confinement at destructive use without traversing attacker-replaceable parent components.

**Implementation direction:** use established identity-safe OS mechanisms. On POSIX prefer dirfd/openat-style no-follow semantics; on Windows use directory/file handles with explicit reparse-safe flags and identity verification. Add deterministic race-simulation tests and real Windows junction/reparse tests where executable. Do not treat static symlink tests as proof against TOCTOU replacement.

### Storage migration -> clone / journal / activation / lock

**Assets:** live SQLite database, clone candidate, rollback copy, migration recovery state, filesystem confinement and one-owner migration semantics.

**Verified controls:** source/candidate/rollback path separation; static symlink/junction/reparse rejection; SQLite clone uses the Online Backup API; candidate integrity/foreign-key/version checks; migration-journal reads use no-follow where available plus handle/path identity comparison; migration-journal writes now use `durable_write_bytes()`; the journal is capped at 64 KiB before full decode; POSIX durable replacement uses opened parent FDs; activation preserves rollback and refuses WAL/SHM sidecars; the migration lock uses native process locks with file-identity checks.

**Residual confinement risk — `SEC-009`:** the migration stack is partially hardened but still has pathname-addressed surfaces, notably SQLite candidate creation, cleanup, Windows publication, and activation/lock interactions. BE-028 must complete identity-bound creation/cleanup/activation across relevant platforms instead of treating the POSIX writer/replace improvements as full closure.

**Resource-bound status — `SEC-010`:** the migration journal now has `_MAX_MIGRATION_JOURNAL_BYTES = 64 * 1024`; the opened handle is checked for regular-file type, identity and size before reading, and at most max+1 bytes are consumed before a second length check. This is `FIXED` statically and awaits observed green targeted/CI execution before `VERIFIED`.

**Residual lock-lifetime risk — `SEC-013`:** lock-file acquisition checks alone must not allow migration-root replacement to create a second independently lockable logical root. Preserve one-owner semantics for the entire critical section with a stable root identity or a lock anchored in a location outside the replaceable subtree.

### Backup target -> isolated restore root

**Assets:** restored database, Raw Source replicas, runtime isolation and destination filesystem.

**Verified controls:** absolute non-overlapping restore destination, absent destination requirement, manifest/completion-marker validation, canonical object paths, content hashes, SQLite integrity/FK/schema validation and atomic publication. Deletion-ledger reads now bound the head and each record to 64 KiB, record count to 250,000, aggregate record bytes to 128 MiB, and validate regular-file handle/path identity before bounded reads.

**Resource-bound status — `SEC-008`:** current deletion-ledger resource limits close the previously unbounded read/materialization path statically. Keep `FIXED` until the dedicated regression tests are observed green.

**Threats to continue scanning:** ancestor replacement races on destination/target paths, Windows reparse behavior, retention/GC deletion confinement and any write-side temp-file creation that still occurs after only pathname validation.

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

**Open risk:** `SEC-005` — current quality workflows still reference `actions/checkout@v6` and `actions/setup-python@v6` by mutable major tags rather than reviewed immutable commit SHAs.

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
