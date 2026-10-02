# Structured long-term replication publication — 2026-10-02

## Status / ownership

Owner branch: `fix/structured-replication-publication-20261002-sol`  
Draft PR: #385 — `Storage: verify append-only long-term replication publication`

This is a stacked Storage slice. It builds on CanonicalCommitBundle serialization and
owns the verified filesystem publication boundary only. It does not own worker
composition, snapshots/replay, Core/UI integration, or schema-version expansion.

A separate agent is already building a bounded hardening follow-up in PR #395.
Do not duplicate or overwrite that work.

## Ausgangslage

Before this slice pATHENA already had durable SQLite state for structured long-term
replication:

- `replication_targets`;
- `replication_commits`;
- contiguous staging;
- monotone confirmation;
- persistent conflict/recovery states.

The canonical bundle serializer was prepared separately in #325 and has a fresh
current-Develop reconstruction in #386.

What was still missing was the actual `long_term_root` publication boundary.
There was no production path that could safely:

1. verify the expected remote target head;
2. publish immutable structured commit history;
3. survive crash windows;
4. read back and verify the published bytes;
5. advance the local confirmed watermark only after external verification;
6. refuse unexpected remote history without overwriting it.

The general durable filesystem writer used replace semantics. Replace semantics are
correct for mutable manifests/configuration but wrong for append-only replication
history because an already-published commit must never be silently replaced.

## Root Cause

The durable replication state machine and canonical serialization existed as separate
pieces, but no filesystem protocol joined them.

That left four important correctness gaps:

1. **No immutable publication primitive**
   - the existing durable write primitive could replace an existing path;
   - structured history requires create-once/no-overwrite semantics.

2. **No external head fence**
   - the DB watermark could not be reconciled against the actual target history before
     writing a new commit.

3. **No crash reconciliation**
   - the protocol needed to distinguish/recover from:
     - bundle written but manifest not yet written;
     - bundle + manifest written but DB confirmation not committed;
     - already confirmed identical retry.

4. **No verified target identity/layout boundary**
   - Beta 03 defines a concrete `long_term_root` v1 layout and monotone single-writer
     behavior, but no implementation enforced it.

During implementation the first draft used an extra
`structured-replication-v1/` wrapper and singular `manifest/`. A direct check
against `docs/beta/03_Storage_Datenbanken_und_Migrationen.md` showed this was not
the v1 contract. The code was corrected before qualification to use the specified
direct layout.

## Änderungen

### 1. Durable no-overwrite publication

Added `durable_publish_new_bytes(...)` in
`src/athena/storage/durable_fs.py`.

POSIX path:

- private `.partial` creation relative to an opened parent directory FD;
- parent identity rechecks;
- payload flush + fsync;
- atomic no-overwrite publication with a hard link into the destination name;
- parent-directory fsync after publication;
- temporary-name cleanup + second parent fsync;
- an existing destination raises `FileExistsError` and is not replaced.

Windows path:

- payload is fsynced before publication;
- publication uses bound Windows HANDLEs;
- `_windows_rename_relative(..., replace_existing=False)`;
- an existing destination is never intentionally replaced.

Dedicated tests cover existing-target preservation, symlink/reparse rejection and the
Windows no-replace HANDLE route.

### 2. Verified `long_term_root` v1 repository

Added
`src/athena/storage/structured_replication_publication.py`.

Current v1 target layout:

```text
long_term_root/
├── repository.json
├── commits/
├── snapshots/
├── manifests/
└── replication/
```

`repository.json` is canonical immutable JSON and binds:

- repository format/version;
- repository UUID;
- SHA-256 as the hash algorithm;
- CanonicalCommitBundle format/version;
- storage-layout version.

The current v41 replication schema has no separate Beta-documented
`repository_id` column. This slice therefore uses the persisted
`ReplicationTarget.target_id` UUID as the repository identity. Do not silently
introduce schema v42 from this branch; see Known Restprobleme.

### 3. Append-only commit and head history

Commit bundles are stored under immutable names derived from commit sequence + bundle
hash.

Per-sequence canonical manifests under `manifests/` contain:

- commit sequence;
- current bundle hash;
- predecessor hash;
- canonical bundle filename;
- manifest format/version.

The manifest sequence is contiguous and predecessor-linked. The highest verified
manifest is the remote structured-replication head.

There is intentionally no mutable fake progress/head cache whose contents could
silently disagree with the immutable history.

### 4. Remote/local history fencing

Before mutating the target the publisher verifies:

- canonical bundle bytes/hash;
- local staged head hash and predecessor hash;
- canonical bundle commit identity against local `commit_records`;
- repository identity/format;
- managed-directory boundaries;
- canonical manifest chain;
- current remote head bundle integrity;
- target head versus the persisted local confirmed watermark.

Unexpected remote history enters the existing persistent replication conflict state
with `unexpected_target_history`. The unexpected data is left in place and is not
overwritten.

### 5. Verification before confirmation

Publication order is:

```text
verify local/staged identity
→ verify repository + current remote head
→ no-overwrite commit bundle publication or exact-byte reuse
→ read back + canonical/hash verification
→ no-overwrite per-sequence manifest publication or exact-byte reuse
→ re-scan/re-verify remote head
→ confirm SQLite replication commit/watermark
```

The local target watermark therefore advances only after the external target state has
been verified.

### 6. Crash/restart and race handling

Covered recovery windows:

- exact orphan bundle exists, manifest missing:
  - verify/reuse bundle;
  - publish manifest;
  - confirm.

- bundle + manifest exist, local commit still pending:
  - verify exact remote head;
  - confirm without rewriting history.

- identical publisher wins DB confirmation race:
  - losing publisher refreshes commit/target state;
  - success is accepted only if the same commit is now VERIFIED and the watermark has
    advanced.

- already verified identical retry:
  - target is verified and remains read-only.

PR #395 adds additional handling for unsafe/non-file `.partial` crash residue and an
explicit regression for retrying an older verified bundle after a later head has
advanced. Keep that follow-up stacked; do not reimplement it here.

## Dateien

Owned by PR #385:

- `src/athena/storage/durable_fs.py`
- `src/athena/storage/structured_replication_publication.py`
- `tests/unit/test_durable_fs.py`
- `tests/unit/test_storage_structured_replication_publication.py`
- this handoff

PR #395 separately owns follow-up edits to:

- `src/athena/storage/structured_replication_publication.py`
- `tests/unit/test_storage_structured_replication_publication.py`
- `docs/agent_handoffs/structured-replication-partial-boundaries-20261002-sol.md`

## Verhalten danach

For the structured filesystem boundary implemented here:

- immutable target history is not silently replaced;
- pATHENA verifies the expected remote head before extending it;
- exact crash leftovers can be resumed idempotently;
- foreign/tampered/unexpected history becomes an explicit persistent conflict;
- a target is not marked confirmed merely because a write call returned;
- duplicate identical publishers do not create a false failure after one wins
  confirmation;
- the directory layout now matches Beta 03 instead of the rejected wrapper layout.

This is still not the complete long-term replication feature. No claim is made that
the Core automatically builds/publishes every application commit yet.

## Validierung

### Executable environment

A local checkout/test run is unavailable in this ChatGPT worker because outbound DNS
to `github.com` fails. GitHub Actions is the executable validation source.

### Baseline evidence

Old canonical serializer PR #325 / head
`ea6503775d27417358e800abed5dd48faedf3028`:

- Storage Focused run `36928959859`: PASS.
- Full Quality run `36928959869`:
  - specification validator: PASS;
  - Ruff: PASS;
  - mypy: PASS;
  - Windows path safety: PASS;
  - Linux storage regressions: PASS;
  - Local install smoke: PASS;
  - full pytest then hit an unrelated shared-process Qt segmentation fault in
    `tests/unit/test_desktop_chat_selection_state.py`, suite exit 139.

That Qt lifecycle failure is already being handled by separate CI/Qt isolation work
(#327/#372). It is not treated as evidence for or against this Storage slice.

### PR #385 exact-head evidence

Publication code head before this documentation commit:
`d2c29db93a69abee78ec26d14515d4c4ae97bb4d`.

Canonical Quality run `36940215024` was still fully queued when this handoff was
written. No PASS is claimed for that head.

Because #385 is historically stacked on #325 instead of directly on
`develop/pathena-next`, the Storage Focused workflow's PR-base filter does not run
for #385. Final current-Develop integration must run both Storage Focused and
canonical Quality.

## Abhängigkeiten

### #386 — current CanonicalCommitBundle reconstruction

PR #386 is the current-Develop tree-equivalent rebuild of #325.

Head observed:
`9cd1a6fb6c17d523ec00e86178aa4614bed1c294`.

Current Develop base observed:
`467ef434236c320e4afe9d21a39c20a4a2b75728`.

The following pre-existing blobs are byte-identical between #325's serializer base
and #386:

- `src/athena/storage/durable_fs.py`
- `tests/unit/test_durable_fs.py`
- `src/athena/storage/structured_replication.py`
- `tests/unit/test_storage_structured_replication.py`

Therefore a fresh reconstruction of this bounded slice onto the qualified #386/current
Develop lineage should not require overwriting unrelated current work.

### #395 — partial-boundary hardening

PR #395 is deliberately stacked on #385 and extends this exact publication protocol.
It must be folded into the final reconstruction rather than duplicated here.

## Konfliktrisiko

High overlap now exists with #395 in:

- `src/athena/storage/structured_replication_publication.py`
- `tests/unit/test_storage_structured_replication_publication.py`.

Do not edit those files in parallel unless coordinating a concrete failing test.

No overlap was introduced by #385 into current Chat, Desktop UI, LM Studio, Jobs,
Sources, Research, Plugins, Resources, Packaging, Backup or bot-configuration lanes.

Avoid a force-push/rebase of #395 or other agents' branches.

## Bekannte Restprobleme

1. **Exact-head CI is not yet terminal.**
   - Do not report this slice green until exact final integration evidence exists.

2. **Separate Beta `repository_id` is not represented in schema v41.**
   - Current implementation uses `target_id` as repository identity.
   - A later schema-alignment decision must determine whether a distinct
     `repository_id` is required and migrate it deliberately.

3. **No durable worker composition yet.**
   - Core does not yet automatically select/build/publish all structured commit
     bundles through this boundary.

4. **No periodic structured snapshot/replay yet.**
   - Replay length is not yet bounded by the Beta-required snapshot layer.
   - Full new-`athena.db` reconstruction from snapshot + commit tail is future work.

5. **No physical NAS/SMB qualification in this runner.**
   - The protocol fails closed when required no-overwrite semantics are unsupported;
     it has not been physically exercised against a real NAS target here.

6. **Windows temp creation inherits the existing durable-writer pathname limitation.**
   - Final publication is HANDLE-bound/no-replace.
   - If stronger adversarial parent-rename guarantees are required for temp creation,
     extend the shared durable Windows primitive in a separate focused slice with
     actual Windows qualification.

## Nächste sinnvolle Schritte

1. Let #395 finish/qualify without parallel edits to its two owned files.
2. Let #386 establish a fresh qualified serializer base on current Develop.
3. Reconstruct the combined #385 + #395 bounded file deltas on that fresh lineage
   rather than force-rebasing another bot's branch.
4. Run exact-head:
   - Storage Focused Candidate;
   - canonical Quality;
   - Windows path safety;
   - Linux storage regressions;
   - local install smoke.
5. Attribute any failure against the known current-Develop baseline before changing
   unrelated code.
6. After the verified filesystem boundary is integrated:
   - implement durable worker composition / outbox scheduling;
   - then implement periodic structured snapshots and snapshot+tail replay;
   - then add recovery reconstruction of a new `athena.db`.
7. Before claiming full `long_term_root` readiness, exercise the protocol on supported
   Windows local/external storage and representative NAS/SMB targets.

## Commit / Branch / PR

Branch:
`fix/structured-replication-publication-20261002-sol`

Draft PR:
#385

Publication code head before handoff:
`d2c29db93a69abee78ec26d14515d4c4ae97bb4d`

Important related PRs:
- #386 — current-Develop CanonicalCommitBundle reconstruction;
- #395 — stacked partial-boundary hardening.
