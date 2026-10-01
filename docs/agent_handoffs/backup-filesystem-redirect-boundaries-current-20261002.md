# Backup filesystem redirect boundaries — current Develop candidate — 2026-10-02

## Ausgangslage

Candidate base: `develop/pathena-next` at `467ef434236c320e4afe9d21a39c20a4a2b75728`.

This candidate consolidates two independently developed Backup hardening slices that were originally based on `67174198e1494fd4c8678aad60756c39ef5c160b`.

Before consolidation, Develop advanced by 31 commits. A commit-range comparison confirmed that none of those 31 commits changed `src/athena/backup/**` or Backup test files touched by these slices. The two changes were therefore reapplied intact to the current Develop head without rebase, force-push, or modification of other bots' work.

Superseded draft PRs/branches remain available as history/evidence but should not be integrated:

- PR #345 / `fix/backup-snapshot-link-boundaries-20261002-sol`
- PR #364 / `fix/backup-target-lock-reparse-boundaries-20261002-sol`

Use this consolidated branch as the only integration candidate:

`fix/backup-filesystem-redirect-boundaries-current-20261002-sol`

## Root Cause

Backup filesystem trust boundaries were inconsistent.

The codebase already provides `athena.storage.durable_fs.is_link_boundary()` as the canonical cross-platform redirect predicate for:

- POSIX symlinks;
- Windows junctions;
- Windows reparse points.

Backup service and target-lock paths nevertheless mixed:

- direct `Path.is_symlink()`;
- `is_file()`/`is_dir()` without redirect validation;
- raw re-opens of snapshot control files after an earlier verification;
- recursive cleanup without a root redirect guard.

That created inconsistent Windows behavior and allowed path provenance to become weaker than the existing checksum/schema/SQLite verification.

## Work package A — Backup service/read/recovery boundaries

### Shared safe-file boundary

`_safe_existing_file()` now:

- requires a safe relative path;
- rejects absolute/rooted/drive-qualified paths and `..`;
- rejects redirecting ancestors of the trusted root;
- requires the trusted root to be a real directory;
- walks every relative component and rejects redirect boundaries;
- preserves resolved-path containment and regular-file checks.

### Snapshot verification and restore

Hardened:

- disaster-restore snapshot root;
- `complete.marker`;
- `manifest.json`;
- snapshot `athena.db`;
- full verification;
- light verification;
- restore-copy recheck;
- startup/crash recovery;
- object-GC snapshot enumeration.

Control files no longer bypass the same filesystem trust model used for backup objects.

### Target identity and maintenance

Hardened:

- Backup target root;
- `.athena-backup-target.json`;
- legacy target identity recovery;
- retention trash roots/entries;
- object store roots/entries;
- restored deleted-source payload cleanup;
- durable metadata destination checks.

### Recursive cleanup

Added `_remove_tree_without_redirect()`.

Every recursive delete in `backup/service.py` now passes through one redirect guard. Best-effort failure cleanup skips an unsafe redirected root rather than handing it to `shutil.rmtree()`; normal retention cleanup fails closed.

## Work package B — Backup target locking

`backup/target_lock.py` now uses the same `is_link_boundary()` contract.

Changes:

- target root and every lexical ancestor reject symlink/junction/reparse boundaries;
- lock-file preflight rejects the same boundaries;
- pathname/handle identity verification rechecks the full redirect ancestor chain;
- because identity is checked once during open and again after lock acquisition, a redirect that becomes visible between those stages prevents entry into the critical section.

POSIX `flock`, Windows `msvcrt.locking`, permission handling, handle lifetime and unlock behavior were not otherwise changed.

## Dateien

Product:

- `src/athena/backup/service.py`
- `src/athena/backup/target_lock.py`

Tests:

- `tests/unit/test_backup_snapshot_link_boundaries.py`
- `tests/unit/test_backup_target_lock_boundaries.py`

Handoff:

- `docs/agent_handoffs/backup-filesystem-redirect-boundaries-current-20261002.md`

No Chat, UI, LM Studio, Update, Settings, Sources, Jobs, Knowledge, Obsidian or migration implementation file is changed.

## Regression coverage

Snapshot/service suite covers:

1. redirected `complete.marker`, `manifest.json`, and `athena.db`;
2. full and light verification;
3. redirected snapshot roots;
4. disaster restore;
5. safe trusted-root handling;
6. redirecting root ancestors and intermediate path components;
7. unsafe relative paths;
8. target descriptor/root reparse boundaries;
9. legacy target identity recovery;
10. retention recovery;
11. object-GC enumeration;
12. metadata publication;
13. restore-copy recheck;
14. startup recovery;
15. recursive cleanup refusing redirect roots.

Target-lock suite additionally covers:

16. real symbolic-link target roots/ancestors/lock files;
17. deterministic Windows-reparse target-root contract;
18. deterministic Windows-reparse ancestor contract;
19. deterministic Windows-reparse lock-file contract;
20. a redirect becoming visible after initial open but before post-lock identity verification;
21. existing pathname replacement and POSIX permission contracts remain covered.

## Validation state

Local execution is unavailable in this ChatGPT container because outbound DNS to `github.com` prevents cloning the repository. No local pytest/mypy/Ruff result is claimed.

The candidate must receive exact-head GitHub evidence for:

- specification validator;
- Ruff;
- mypy strict;
- canonical pytest suite;
- Linux storage regressions;
- local install smoke;
- Windows path safety.

Do not describe the candidate as release-green until those checks complete successfully.

## Parallel bot coordination

The run synchronized open branches/PRs repeatedly.

Active work intentionally avoided included Chat cancellation/forks, LM Studio/model lifecycle, Update, Settings, Sources, Jobs, Knowledge UI ownership, Obsidian move/import work, storage migration bundle and CI lifecycle slices.

When Develop advanced from `671741...` to `467ef434...`, comparison showed zero overlapping Backup files. The fresh candidate was therefore rebuilt on current Develop instead of rebasing or force-pushing the old branches.

Conflict surface is now limited to the five files listed above. Before integration, check only for newer Backup-specific work created after this handoff.

## Current candidate commits

Branch: `fix/backup-filesystem-redirect-boundaries-current-20261002-sol`

- `f4ac11bb12fe33edec6514ee85c80fcfbdebbfe9` — Backup service redirect-boundary implementation on current Develop
- `454c92ec12bd9d59e898054c4d37fce0095e5eb4` — target-lock redirect-boundary implementation
- `d63e0468a228d3ae0a5e457fc96d1f907187b1af` — snapshot/service redirect regression suite
- `f08688625d339c71562cb5b50089a9f24f0738d5` — target-lock redirect regression suite

## Known limitations / non-claims

- This work rejects known redirect boundaries and strengthens path provenance. It does not claim to make an arbitrarily hostile, externally mutable filesystem free of every possible nanosecond-level race.
- Existing durable filesystem primitives remain the authority for atomic publication and directory-handle durability.
- No UI surface was changed; no UI validation claim is made.
- Old draft PRs #345 and #364 are superseded and should be closed after the consolidated PR is created.

## Next steps

1. Create one draft PR from this branch to current `develop/pathena-next`.
2. Close/supersede #345 and #364 to avoid duplicate CI/integration.
3. Run exact-head canonical gates.
4. On any failure, fix the product/root cause on this consolidated branch.
5. If all gates are green and Develop still has no conflicting Backup changes, integrate history-preserving according to the repository Integrator workflow.
6. After integration, add Backup target-lock modules to the dedicated Windows path-safety job only if that gate coverage change can be made without competing CI-workflow edits; canonical pytest already executes the tests cross-platform-independently.
