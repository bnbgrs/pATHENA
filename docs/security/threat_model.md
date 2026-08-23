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

**Verified controls:** non-loopback bind refusal, bounded/strict request framing, `Origin` rejection, bearer authentication with constant-time comparison, exclusive staged runtime publication, and static symlink/junction/reparse checks through the shared storage boundary predicate after SEC-011.

**Open risks:** `SEC-001` — POSIX `0600` is not equivalent to a proven private Windows DACL. The token/discovery directory must be demonstrated to exclude other interactive users on Windows, including overridden runtime roots. `SEC-012` — token/discovery staging is still created by pathname after a parent validation, so a hostile concurrent parent replacement can redirect the write before the later safety re-check; private bytes must not be written until directory identity is pinned.

**Recent hardening:** `SEC-011` replaced symlink-only runtime-root/ancestor checks with `is_link_boundary()`, covering Windows junctions/reparse points. It remains FIXED rather than VERIFIED until targeted Windows execution is observed.

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

### Storage migration -> clone / journal / activation / lock

**Assets:** live SQLite database, clone candidate, rollback copy, migration recovery state, filesystem confinement and one-owner migration semantics.

**Verified controls:** source/candidate/rollback path separation; static symlink/junction/reparse rejection; SQLite clone uses the Online Backup API; candidate integrity/foreign-key/version checks; journal reads use no-follow where available plus handle/path identity comparison; activation preserves rollback and refuses WAL/SHM sidecars; the migration lock verifies its opened lock-file handle against the pathname at acquisition and uses native process locks.

**Residual confinement risk — `SEC-009`:** clone creation, journal publication, cleanup and activation still cross check/use boundaries. `migration_clone.py` validates `candidate.parent` and then opens the candidate through `sqlite3.connect(candidate)` by pathname. `migration_journal.py` validates the parent and later creates a temporary journal by pathname. `migration_activation.py` validates files/parents and then uses path-based `durable_replace()` for source->rollback and candidate->source. `durable_replace()` itself validates parents before `os.replace()`/`MoveFileExW` but does not retain parent identity across the operation. A hostile local process able to replace an already validated migration ancestor can therefore race those operations. The fix belongs inside BE-028 and must use identity-bound OS primitives or equivalent handle-based verification, including Windows reparse/junction semantics.

**Residual resource risk — `SEC-010`:** `MigrationJournalStore.load()` verifies the journal file identity but then reads the whole file before parsing. The journal contract is tiny, so startup/recovery should reject an oversized journal using a conservative versioned byte ceiling checked from the already-open handle before full read.

**Residual lock-lifetime risk — `SEC-013`:** the lock-file handle is identity-checked only against the path at acquisition. The migration-root directory itself is not pinned for the lifetime of the `with migration_lock(root)` critical section. If an out-of-band actor renames/replaces that root, a second process can address a different `.athena-migration.lock` at the same logical pathname and may acquire an independent OS lock while process A still owns the old file. The one-owner invariant therefore needs a stable root identity or a lock anchored in a location that cannot be replaced under the threat model.

### Backup target -> isolated restore root

**Assets:** restored database, Raw Source replicas, runtime isolation and destination filesystem.

**Verified controls:** absolute non-overlapping restore destination, absent destination requirement, manifest/completion-marker validation, canonical object paths, content hashes, SQLite integrity/FK/schema validation and atomic publication.

**Threats to continue scanning:** ancestor replacement races on destination/target paths, Windows reparse behavior, resource amplification and retention/GC deletion confinement. Findings SEC-006/007/009 establish that path-based pre-checks elsewhere are not sufficient evidence for concurrent filesystem mutation safety. SEC-008 separately tracks unbounded deletion-ledger reads.

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
