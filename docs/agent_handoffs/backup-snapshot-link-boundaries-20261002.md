# Backup/Restore filesystem redirect-boundary hardening — 2026-10-02

## Ausgangslage

Base: `develop/pathena-next` at `67174198e1494fd4c8678aad60756c39ef5c160b`.

Backup object files already used `_safe_existing_file()` for containment, but several equally trusted Backup/Restore paths still used direct `Path` reads or POSIX-only `is_symlink()` checks:

- snapshot root;
- `complete.marker`;
- `manifest.json`;
- snapshot `athena.db`;
- Backup target root and `.athena-backup-target.json`;
- light verification;
- startup recovery;
- restore copy;
- retention recovery;
- object-GC snapshot enumeration;
- metadata publication;
- best-effort recursive cleanup.

Windows junctions/reparse points therefore did not consistently receive the same fail-closed treatment as POSIX symlinks.

## Root Cause

Backup filesystem trust boundaries were implemented inconsistently. Some paths used the shared `athena.storage.durable_fs.is_link_boundary()` predicate, some used `Path.is_symlink()`, and some trusted a path after only `is_file()`/`is_dir()`.

This allowed a redirected root, ancestor, intermediate component, or control file to reach verification/recovery/restore code even when the final bytes remained checksum-valid. The defect was path provenance/containment, not hashing.

## Änderungen

### Shared trust boundary

- `_safe_existing_file()` now:
  - requires a safe relative path;
  - rejects `..`, absolute/rooted/drive-qualified paths;
  - rejects redirecting ancestors of the trusted root;
  - requires the trusted root to be a real directory;
  - walks every relative component and rejects symlink/junction/reparse boundaries;
  - keeps the existing resolved-path containment and regular-file checks.
- Existing object verification therefore gains the same Windows junction/reparse protection as snapshot metadata.

### Snapshot verification and restore

- `restore_path()` rejects a redirected snapshot directory before resolving it.
- `_verify_path()` and `_verify_payload_path()` use safe control-file resolution.
- `_verify_light_path()` now uses the same safe snapshot root/control-file boundary instead of duplicating raw reads.
- `_restore_verified_path()` rechecks `manifest.json` and `athena.db` before use rather than re-opening raw snapshot paths after prior verification.
- Crash/startup recovery reads `complete.marker` and `manifest.json` through the same boundary.
- Snapshot creation exception handling treats a completion marker as published only when the marker remains safely reachable.

### Target identity and maintenance

- Backup target roots and `.athena-backup-target.json` use `is_link_boundary()`, not `Path.is_symlink()`.
- Legacy target identity recovery refuses redirected snapshot history.
- Retention trash roots/entries use junction/reparse-aware checks.
- Object-store GC and snapshot-reference enumeration use junction/reparse-aware checks.
- Object-GC reads completion markers/manifests through `_safe_existing_file()`.
- Restored deleted-source payload cleanup uses the shared boundary predicate.
- `_write_fsynced()` rejects a redirecting destination even when it is not a POSIX symlink.

### Recursive cleanup

- Added `_remove_tree_without_redirect()`.
- All recursive deletes in this module now flow through that helper.
- Fail-closed retention cleanup raises on redirected/non-directory roots.
- Best-effort failure cleanup skips an unsafe redirected root instead of passing it to `shutil.rmtree()`.
- Existing restore publication identity comparison remains in place before deleting an atomically published destination.

## Dateien

- `src/athena/backup/service.py`
- `tests/unit/test_backup_snapshot_link_boundaries.py`
- `docs/agent_handoffs/backup-snapshot-link-boundaries-20261002.md`

No Chat, UI, LM Studio, Update, Settings, Sources, Jobs, Obsidian or storage-migration implementation files were changed.

## Verhalten danach

Backup/Restore no longer treats a redirect-backed filesystem path as trustworthy merely because the referenced bytes are readable and checksum-valid. Snapshot control files, target identity files, maintenance scans, recovery paths and recursive cleanup now share the same symlink/junction/reparse fail-closed model.

Canonical content-hash, manifest, schema, SQLite integrity, deletion-ledger and object-integrity checks remain in force.

## Regressionstests

New dedicated tests cover:

1. redirected `complete.marker`, `manifest.json`, and `athena.db` in full verification;
2. the same control-file redirects in light verification;
3. redirected snapshot root in verification;
4. redirected snapshot root in disaster-restore entry;
5. redirected completion marker before disaster-restore read;
6. Windows reparse contract for `_safe_existing_file()`;
7. redirected trusted root;
8. redirected trusted-root ancestor;
9. redirected intermediate relative component;
10. absolute and parent-traversal relative paths;
11. target descriptor reparse rejection;
12. target root reparse rejection;
13. legacy target identity recovery with redirected snapshot history;
14. retention-trash root reparse rejection;
15. retention snapshot-entry reparse rejection;
16. object-reference scan with redirected snapshots root;
17. metadata publication into a redirecting destination;
18. restore-copy recheck of manifest/database after earlier verification;
19. startup recovery refusing a redirected completion marker;
20. recursive cleanup proving `shutil.rmtree()` never receives a redirecting root.

Tests monkeypatch the shared boundary predicate where necessary so Linux and Windows exercise the same logical contract without requiring symlink privileges.

## Validierung

Local clone/execution is unavailable in this ChatGPT container because outbound DNS to `github.com` fails. No local pytest result is claimed.

GitHub Actions is therefore the executable validation path. The branch has been kept as a draft PR until the exact current head receives canonical gate evidence.

Required exact-head checks:

- specification validator;
- Ruff;
- mypy strict;
- canonical pytest suite;
- Linux storage regressions;
- local install smoke;
- Windows path safety.

## Parallelität / Konfliktrisiko

This work deliberately avoided the active parallel areas observed during the run, including:

- Chat cancellation/control-plane/UI Stop work (#329, #335, #337);
- durable chat edit/fork work (#342);
- LM Studio/runtime/model identity work (#334, #346);
- Update hardening (#332);
- Settings recovery/model persistence (#333);
- Sources packaging/import work (#336, #339);
- Jobs helper hardening (#344);
- Knowledge async ownership (#343);
- Obsidian move/import-candidate work (#341);
- storage canonical bundle (#325);
- CI lifecycle work (#327).

Conflict surface is concentrated in `src/athena/backup/service.py`. Integrator should re-check any newer Backup-specific branch created after this handoff before integrating.

## Branch / PR

Branch: `fix/backup-snapshot-link-boundaries-20261002-sol`

PR: #345 — `Backup: reject redirected snapshot control files`

Product/test commits through the pre-handoff head:

- `eb51a54ad6e403c3e42a8a73e508a42782cbe53e` — reject redirected snapshot control files
- `0462b5e7126c3b6cd994142b31ea8571ebb9d41f` — control-file regression tests
- `27f0df9a73d17fb7a62a10d5ffc768dfdd191377` — fence redirected snapshot roots
- `a927d755841803b11f946cb31817a88536a9aee7` — snapshot-root regression tests
- `072056453bd9e9ca30bc579b1ee3d64f237334a2` — harden Windows target identity boundaries
- `21977cecde1d10d76b8fb16ff1bd88bf4289f4dc` — target reparse regression tests
- `5f4dca86c445c119f6ed0b28ee313740a14d521f` — unify Windows reparse checks across recovery paths
- `1b66a7774ba1af59bf4431e144163e185db1d3e5` — recovery/metadata reparse tests
- `36d21210507ff21a3ea4118ad5ffa052dead4208` — close light-verify and legacy redirect bypasses
- `f5ff493fdde3d4298285fba886b9a1e4c89a0151` — bind file checks to a real trusted root
- `9a40e385b44561e25d3c3e065448bd21eeb30f28` — light-verify/trusted-root regression tests
- `af445e8f7f93e39a651f326fdaa7af75390815e5` — protect recovery and restore control-file reads
- `042c5b1f4c0627aa914f765262f0cf24fd2fb147` — restore/recovery redirect regression tests
- `3960fc2ffc624b2574b9f9fc9009c750c096bfd9` — avoid recursive cleanup across redirect roots
- `aab2d03e19e3ffd85132c0b11e9b2ada61a9a4d9` — prove cleanup never follows redirect roots
- `a8a23bd8a271d2091ce4f559b510e0fb6b2c3ddb` — reject redirects across full trusted path chain
- `2e328e36264d827bd8810a0000b8a7c4a19aa907` — ancestor/intermediate redirect tests
- `2b6212cfb500f186408c7eda057ba9911bd0e152` — type recovery marker optionality explicitly

## Bekannte Restprobleme

- Exact-head CI is still required; do not call this integrated or release-green without that evidence.
- The helper prevents static redirect boundaries across the path chain but does not claim to make an untrusted externally mutable filesystem cryptographically race-free. Existing target locks serialize ATHENA writers, not arbitrary external processes.
- UI was not changed in this slice; no UI claim is made.

## Nächste sinnvolle Schritte

1. Read the exact PR #345 head and canonical workflow results.
2. If a gate fails, fix the root cause on this branch; do not relax tests.
3. If exact-head gates are green, make the PR ready/integrate history-preserving according to the repository Integrator workflow.
4. After integration, continue Backup/Restore audit at the handle-identity level only if there is concrete failing evidence; do not broaden into speculative filesystem architecture.
