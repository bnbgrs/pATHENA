# Long-term structured publication handoff — 2026-10-02

## Scope and ownership

- Repository: `bnbgrs/pATHENA`
- Branch: `feature/long-term-publication-20261002-sol`
- Deliberately stacked on: PR #325 / `integration/canonical-commit-bundle-fresh-20261001`
- Stack base head when created: `ea6503775d27417358e800abed5dd48faedf3028`
- Integration target after #325 is refreshed/integrated: `develop/pathena-next`
- This slice does not modify the CanonicalCommitBundle serializer, the merged
  structured-replication state machine, Backup, UI, Jobs, Research, Chat, or
  other active bot lanes.

## Ausgangslage

Beta 03 already has:

- a configured optional `long_term_root`;
- schema-v41 durable `replication_targets` / `replication_commits` state;
- monotone staging and atomic confirmation via
  `StructuredReplicationRepository`;
- a separately implemented canonical bundle serializer/verifier in #325.

The missing end-to-end boundary was physical publication. A staged commit could
exist durably in SQLite, but no code verified the expected target head, wrote an
immutable canonical bundle to `long_term_root`, read it back, advanced a
physical head, and only then confirmed the SQLite watermark.

## Root Cause

The durable state machine and serialization format were intentionally delivered
as separate bounded slices. No physical writer existed between them.

Without that writer, the following Beta invariants were not implemented:

1. the physical target history must match the locally confirmed head before a
   mutation;
2. an unexpected target history must never be silently overwritten;
3. the canonical commit object must be durable and verified before the physical
   head advances;
4. the physical head must be durable and verified before the local replication
   watermark confirms;
5. a crash between those boundaries must be restart-recoverable without
   inventing progress.

## Änderungen

New `src/athena/storage/long_term_publication.py`:

- requires an already-staged `ReplicationCommit` and verified canonical bundle;
- binds the bundle `commit_id` back to the local `commit_records` row for the
  same `commit_seq`;
- requires the persisted target locator to equal the exact absolute
  `long_term_root`;
- creates the normative `commits/` and `replication/` layout durably with the
  existing cross-platform `durable_fs` primitives;
- writes/validates `repository.json` as the stable target-identity descriptor;
- serializes pATHENA writers through a per-target cross-process publication lock;
- rejects symlink/junction/reparse control files and verifies opened file identity;
- compares `replication/head.json` against the locally confirmed watermark
  before mutation;
- writes immutable commit objects under
  `commits/<20-digit-commit-seq>.json`;
- never overwrites an already-existing divergent commit object;
- read-backs and re-verifies exact canonical commit bytes and SHA-256 bundle hash;
- advances and read-backs the physical head only after the commit object verifies;
- calls `StructuredReplicationRepository.confirm_commit()` only after both
  physical boundaries verify;
- persists explicit conflict state for unexpected/malformed target history;
- resumes a crash after commit-object publication but before head publication;
- resumes a crash after head publication but before DB confirmation;
- treats a head with no matching immutable commit object as corruption rather
  than silently reconstructing it;
- makes retries of already verified commits read-only, including older commits
  after the target head has advanced.

New `tests/unit/test_long_term_publication.py` covers:

- successful object/head/watermark publication;
- two-commit monotone advancement;
- crash after object write / before head;
- crash after head / before DB confirmation;
- unexpected physical head conflict without overwrite;
- head-without-object fail-closed behavior;
- tampered existing commit object preservation + conflict;
- bundle/local commit identity mismatch;
- target locator mismatch;
- retry of the current verified commit;
- retry of an older verified commit after later history is confirmed.

## Important files

- `src/athena/storage/long_term_publication.py`
- `tests/unit/test_long_term_publication.py`
- this handoff

## Verhalten danach

Once #325 is available underneath this branch, a caller can stage one canonical
structured-replication commit, call `publish_staged_commit(...)`, and receive an
ACTIVE/advanced target only after exact physical read-back verification.

The order is deliberately:

```text
verify bundle/local identity
-> verify expected target identity/head
-> durable immutable commit object
-> exact object read-back + bundle verification
-> durable physical head
-> exact head read-back
-> atomic SQLite replication confirmation
```

No percentage/progress state is invented.

## Validation

Local clone/test execution remains unavailable in this execution environment
because `github.com` DNS resolution fails. Do not interpret source inspection
as a runtime PASS.

Upstream stack dependency #325 exact head
`ea6503775d27417358e800abed5dd48faedf3028` has:

- pATHENA Storage Focused Candidate: PASS
- Windows path safety in ATHENA Quality: PASS
- Linux storage regressions: PASS
- Local install smoke: PASS
- Full Quality: FAIL only because
  `tests/unit/test_desktop_chat_selection_state.py` segfaulted in the old
  shared Qt process; its specification/Ruff/mypy phases had already passed.
  That failure is outside the Storage slice and has a separate active CI
  isolation fix.

Exact-head validation for this publication branch must still be recorded after
the draft PR starts CI.

## Dependencies / conflict risk

- #325 is a hard stack dependency because it introduces
  `athena.storage.canonical_commit_bundle`.
- Do not duplicate or rewrite #325 in this branch.
- The merged structured-replication state from #291 is consumed but not changed.
- Current active Backup hardening (#345), Security, Memory, Chat, Jobs, Sources,
  Research, UI, LM Studio, Settings, logging and PALLAS PRs use different files.
- If #325 is rebuilt on newer Develop, rebase/reconstruct only these three files
  on that refreshed exact head and re-run focused + canonical gates.

## Known remaining work

This slice intentionally does not claim structured long-term replication is
complete. Still separate:

1. authoritative record selection/building from SQLite into
   `CanonicalCommitRecord` values, including explicit neutral-metadata policy
   for Protected Content;
2. durable worker scheduling/composition that stages and invokes publication;
3. structured snapshots and snapshot + bundle replay;
4. recovery UX/diagnostics for a persisted replication conflict;
5. native Windows/NAS end-to-end exercise against a real configured
   `long_term_root`.

## Next owner / next action

1. Run exact-head Ruff, mypy, focused publication tests, Storage Focused and
   canonical Quality.
2. Fix only failures attributable to this slice.
3. Refresh #325 onto the then-current `develop/pathena-next`; stack/rebase this
   three-file delta on that exact serializer head.
4. After integration, implement the upstream record builder/selector with
   Protected Metadata canary coverage before wiring an automated worker.
