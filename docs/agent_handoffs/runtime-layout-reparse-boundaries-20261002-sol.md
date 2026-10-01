# Runtime layout reparse-boundary hardening — 2026-10-02

## Ausgangslage

The writable storage bootstrap calls `RuntimeLayoutService.start()` before opening
SQLite. Database preflight and the current Doctor path checks already use
`athena.storage.durable_fs.is_link_boundary()`, which recognizes Windows
reparse points/junctions as well as symbolic links.

`RuntimeLayoutService` still used only `Path.is_symlink()` for its required
local directories and their ancestors. A Windows junction/reparse-backed
`spool`, `derived`, `logs`, `tmp`, or ancestor could therefore pass the
layout/write-probe boundary even though the SQLite/recovery side would reject the
same class of path.

## Root Cause

Two storage trust boundaries had drifted to different filesystem predicates:

- SQLite/recovery/Doctor: shared Windows-aware `is_link_boundary()`
- Runtime layout creation/write probe: `Path.is_symlink()` only

On Windows, "not a Python symlink" is not sufficient evidence that a path is a
real local directory.

A second ownership defect existed in the write probe: the old `finally` block
unconditionally called `probe.unlink(missing_ok=True)`. If exclusive probe creation
failed because that random pathname already existed, ATHENA would delete the
pre-existing file even though it had never created or owned it.

## Änderungen

Branch: `fix/runtime-layout-reparse-boundaries-20261002-sol`

- `src/athena/storage/runtime.py`
  - imports the shared `is_link_boundary` predicate;
  - ancestor validation now rejects symbolic links **and** reparse points;
  - required runtime directory validation rejects a reparse-backed leaf before
    creation/use and rechecks it after directory creation;
  - writable probes reject a reparse-backed leaf before writing the probe;
  - probe cleanup runs only after ATHENA successfully created that probe;
  - cleanup rechecks directory/link boundaries and compares the path's current
    file identity with the descriptor identity captured at creation;
  - a collision, disappearance, or identity replacement fails closed without
    deleting the unowned/replaced pathname.
- `tests/unit/test_storage_runtime_layout.py`
  - pins reparse-aware ancestor rejection;
  - pins leaf rejection before directory use;
  - pins that writable-probe validation creates no probe when the leaf is
    classified as a reparse boundary;
  - pins that an existing colliding probe pathname is never deleted;
  - pins that a changed probe identity is not unlinked.

The existing durable-filesystem test suite already owns direct Windows attribute
coverage for `is_link_boundary()`; these new tests prove RuntimeLayout consumes
that same predicate rather than duplicating Windows detection.

## Verhalten danach

Runtime filesystem bootstrap now applies the same symlink/junction/reparse policy
as database preflight and recovery tooling. A statically reparse-backed required
runtime path fails closed with `RuntimePathError` instead of being probed through
the redirect.

This does **not** claim a complete hostile concurrent-path race solution for every
Windows pathname operation. It closes the deterministic trust-policy mismatch by
reusing the repository's established boundary predicate.

## Validierung

Local checkout execution remains unavailable in this runner because
`github.com` DNS resolution fails. No local PASS is claimed.

Required exact-head validation:

- focused unit tests for `test_storage_runtime_layout.py`;
- existing storage runtime/bootstrap/locality tests;
- Ruff/mypy;
- canonical Quality / Windows path-safety gate.

## Parallel work / Konfliktrisiko

- PR #379 touches Doctor/derived-recovery tests and does **not** modify
  `src/athena/storage/runtime.py`.
- No open PR was found owning RuntimeLayout reparse handling at branch creation.
- This slice does not touch database preflight, `durable_fs.py`, settings,
  UI, Chat, Jobs, LM Studio, Research, Sources, packaging, or bot configuration.

## Nächste Schritte

1. Read exact-head CI and fix only failures attributable to this slice.
2. If #379 integrates first, keep this runtime-side fix; the two changes are
   complementary and should leave Doctor and real startup on one predicate.
3. Windows-native smoke should include an NTFS junction/reparse-backed runtime
   directory before release.
