# Backup target-lock reparse boundaries — 2026-10-02

## Ausgangslage

Base: `develop/pathena-next` at `67174198e1494fd4c8678aad60756c39ef5c160b`.

`src/athena/backup/target_lock.py` already defended the backup-target lock against POSIX symbolic links and verified that the opened lock-file handle still matched the pathname. However, those checks used `Path.is_symlink()` directly.

On Windows, junctions and other reparse points can redirect filesystem traversal without being represented by that POSIX-only check. The repository already has the canonical cross-platform predicate `athena.storage.durable_fs.is_link_boundary()`.

## Root Cause

The cross-process Backup lock implemented its own narrower redirect model instead of using the repository-wide filesystem trust-boundary predicate.

This created a mismatch:

- Backup service/storage paths increasingly treat symlinks, Windows junctions and reparse points as redirect boundaries.
- Backup target locking only rejected symbolic links.

The second pathname/handle identity check also revalidated the lock file itself, but did not re-run the ancestor redirect check after lock acquisition.

## Änderungen

- Imported and reused `is_link_boundary()` from `athena.storage.durable_fs`.
- Replaced `_assert_no_symlink_ancestor()` with `_assert_no_redirect_ancestor()`.
- Target root and every lexical ancestor now reject symlink/junction/reparse boundaries.
- Lock-file preflight now rejects symlink/junction/reparse boundaries.
- `_assert_handle_matches_path()` now:
  - rechecks the entire redirect ancestor chain;
  - verifies pathname and opened handle still refer to the same filesystem object.
- Because `backup_target_lock()` already calls `_assert_handle_matches_path()` once during open and again after lock acquisition, a redirect becoming visible between those stages now fails closed before the critical section is entered.

No lock lifetime, POSIX `flock`, Windows `msvcrt.locking`, permission, or unlock semantics were changed.

## Dateien

- `src/athena/backup/target_lock.py`
- `tests/unit/test_backup_target_lock_boundaries.py`
- `docs/agent_handoffs/backup-target-lock-reparse-boundaries-20261002.md`

## Regressionstests

Existing real-symlink tests were updated to the generalized redirect contract.

New deterministic tests cover:

1. Windows-reparse contract on target root;
2. Windows-reparse contract on a target ancestor;
3. Windows-reparse contract on `.athena-backup.lock`;
4. redirect ancestor becoming visible after lock-file open/initial identity check but before the post-lock identity check.

These tests monkeypatch the shared predicate, so they exercise the Windows semantic contract without requiring junction creation privileges on the CI host.

## Verhalten danach

A Backup target cannot enter the lock critical section when its root, an ancestor, or the lock file is represented as a redirecting filesystem boundary. The post-lock identity verification also rechecks the ancestor chain, reducing the gap between preflight and critical-section entry.

## Validierung

Exact-head GitHub CI is required. Local clone/test execution is unavailable in this ChatGPT container because outbound DNS to `github.com` fails. No local green result is claimed.

## Parallelität / Konfliktrisiko

This branch was created independently from current `develop/pathena-next`; it does not depend on PR #345 and does not modify `src/athena/backup/service.py`.

PR #345 changes Backup service trust boundaries and a dedicated new test file. This target-lock slice changes only:

- `src/athena/backup/target_lock.py`;
- the existing target-lock boundary test module;
- this handoff.

No active bot/PR discovered during synchronization modified `target_lock.py`.

## Branch / Commits

Branch: `fix/backup-target-lock-reparse-boundaries-20261002-sol`

- `aebf5a3f33e7fa755a577ecf18bb5c81bc2bb56a` — reject Windows redirects in target locking
- `516ee3fd18d9d1b9fc58d0ded4b78223eadb1c0c` — target-lock reparse regressions

## Bekannte Restprobleme

- Exact-head Quality/Windows evidence is still required.
- This prevents known redirect boundaries and rechecks pathname identity; it does not claim to make an arbitrary hostile filesystem free of every nanosecond race.
- No UI behavior is changed.

## Nächste sinnvolle Schritte

1. Run exact-head canonical gates.
2. Fix any gate failure on this branch without weakening redirect checks.
3. Integrate only after #345 ordering/conflict status is rechecked; the file surfaces are disjoint, so no code-level conflict is expected.
4. After integration, do not reopen target-lock architecture unless a concrete regression or platform failure remains.
