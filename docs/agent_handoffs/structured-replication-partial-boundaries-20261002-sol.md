# Structured replication partial-boundary hardening — 2026-10-02

## Ausgangslage

PR #385 owns the verified append-only long-term replication publication slice.
Its durable writers use private `.partial` files and its scanner intentionally
ignores crash residue ending in `.partial`.

The scanner and repository initializer previously ignored any matching pathname
before checking its filesystem type. A directory, symlink, Windows junction or
other reparse-backed entry named like a partial could therefore remain hidden
inside an otherwise fail-closed replication target.

## Root Cause

The "ignore crash residue" name check ran before the same link/reparse/regular-file
trust checks applied to canonical bundle and manifest files.

## Änderungen

Stack branch:
`fix/structured-replication-partial-boundaries-20261002-sol`

Base owner branch:
`fix/structured-replication-publication-20261002-sol` / PR #385

Changed production behavior:

- add one internal `_assert_safe_partial_file()` guard;
- ignored partial residue must be a real regular file;
- symlink/junction/reparse partials fail closed;
- directories/special files disguised as partials fail closed;
- apply the guard to root-level `.repository.json.*.partial` residue;
- apply the guard to managed `commits/` and `manifests/` residue;
- target history is marked `unexpected_target_history` through #385's existing
  conflict path; the unexpected entry is never removed or followed.

Regression coverage also pins #385's existing read-only behavior when an already
verified older bundle is retried after the remote/local head has advanced.

## Dateien

- `src/athena/storage/structured_replication_publication.py`
- `tests/unit/test_storage_structured_replication_publication.py`
- this handoff

## Validierung

Local checkout remains unavailable in this runner because `github.com` DNS
resolution fails. Exact-head GitHub Actions are the executable validation source.

Do not claim PASS until the stacked PR's canonical Quality result is terminal.
The parent #385 CI is also still queued at handoff creation.

## Abhängigkeiten / Konfliktrisiko

- Hard dependency: #385.
- Do not merge this without #385.
- No changes to #385's `durable_fs.py` no-overwrite primitive.
- No overlap with current UI, Chat, Jobs, Research, Sources, LM Studio, Plugins,
  Resources or packaging lanes.
- #386 is the independent current-Develop refresh of the canonical bundle base;
  #385's owner still needs to reconstruct/retarget the publication stack after
  its parent serializer integration.

## Nächste Schritte

1. Read exact-head Quality for this follow-up and fix only slice-attributable failures.
2. Fold/cherry-pick this two-file behavior into #385 before its final current-Develop
   reconstruction.
3. Re-run Storage Focused + canonical Quality on the final exact integration SHA.
