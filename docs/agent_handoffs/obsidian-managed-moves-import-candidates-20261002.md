# Obsidian managed moves / import candidates handoff — 2026-10-02

## Ausgangslage

Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.

Beta chapter 20 requires managed notes to remain identifiable after a user moves them into subfolders (§20/§59), Markdown without `athena_id` to become an explicit import candidate rather than an automatic merge/rejection (§37–39), and editor save bursts to be reconciled safely (§27–29).

The current watcher violated those contracts in three connected ways:

1. `ObsidianVaultWatcher._managed_files()` scanned only direct children of `Knowledge/`; a valid managed note moved to `Knowledge/<subfolder>/...` disappeared from sync.
2. Every stable Markdown file was forced through the managed-projection parser. A user-created note without ATHENA identity was therefore reported as `REJECTED`, losing the required import-candidate state.
3. A file or nested directory disappearing between discovery and `stat()/read_bytes()/iterdir()` raised `FileNotFoundError` out of the poll pass. Editors commonly save or rename through atomic replacement, so an ordinary transient filesystem race could fail the long-lived watch service.

## Root Cause

The polling boundary conflated the managed projection namespace with a flat directory layout and assumed discovered paths remained stable until read. It also had no state representing a user-owned Markdown file awaiting explicit import classification.

## Änderungen

### Product

`src/athena/knowledge/obsidian_sync.py`

- Added truthful `ObsidianWatchStatus.IMPORT_CANDIDATE`.
- Added a small front-matter identity probe for `athena_id` / legacy `athena_knowledge_id`.
  - no managed identity => `IMPORT_CANDIDATE`;
  - a file that claims managed identity still goes through strict parsing, so malformed/stale managed notes remain `REJECTED`/`CONFLICT`.
- Replaced the one-level `Knowledge/` scan with recursive managed-note discovery.
- Nested symlinks, junctions and other reparse points are skipped through the existing shared `is_link_boundary()` trust-boundary predicate.
- Transient `FileNotFoundError` during per-file stable reads or nested-directory enumeration now clears only that observation and continues the poll pass; it no longer escalates a normal atomic save/rename race into watcher failure.

No canonical Knowledge mutation semantics, revision rules, provenance semantics, export format, SQLite schema, or write-stamp hashing were changed.

### Tests

`tests/unit/test_obsidian_sync.py`

Added regression coverage for:

- managed note moved/renamed into a nested folder, resolved by front-matter identity with no new canonical revision;
- new Markdown without ATHENA identity surfaced as `IMPORT_CANDIDATE` with no canonical mutation;
- malformed Markdown that claims ATHENA identity remaining `REJECTED`, not being downgraded to an import candidate;
- nested symlink directory not being traversed;
- file disappearing during stable read being treated as a transient race, not a sync failure.

## Verhalten danach

- Users may organize managed Knowledge projections into nested folders without losing reconciliation solely because the path changed.
- New user-authored Markdown is observable as a pending import decision; filename similarity never mutates canonical Knowledge.
- Malformed/stale managed projections remain fail-closed.
- Common atomic editor save/rename races no longer terminate the whole watcher.
- Link/reparse boundaries remain excluded from traversal.

## Validierung

Local checkout/test execution is unavailable in this execution environment because direct `github.com` DNS resolution fails. No local PASS is claimed.

Required exact-head validation before integration:

1. `tests/unit/test_obsidian_sync.py`
2. `tests/unit/test_obsidian_import.py`
3. `tests/unit/test_obsidian_export.py`
4. Ruff / mypy
5. canonical ATHENA Quality
6. Windows-relevant lane if triggered by the repository workflow, because nested reparse handling is part of the contract.

## Bekannte Restprobleme

This slice only surfaces new no-ID Markdown as an import candidate. It does **not** invent the separate product UI that lets a user classify that candidate as KnowledgeUnit / Concept Note / Source / ignore; Beta §38 remains a subsequent Core/UI integration slice.

This slice also does not implement three-way automatic semantic merge for stale revisions; existing fail-closed conflict behavior remains unchanged.

## Abhängigkeiten / Konfliktrisiko

Fresh changed-filename check against active PRs #325, #327, #329, #330, #331, #332 and #333 showed no overlap with the two product/test files in this slice.

The central `docs/agent_handoffs/alpha-beta-canonical-20261001.md` is currently modified by active #330/#331 and is intentionally not changed here. This dedicated handoff follows the repository's established per-slice handoff pattern.

## Branch / Commits

Branch: `fix/obsidian-managed-move-import-candidate-20261002-sol`

Base: `67174198e1494fd4c8678aad60756c39ef5c160b`

- `e0b975b74053594410f8a6d9f3f41cef035b02cd` — recursive reconciliation + import-candidate state
- `c1bda468cae08d33eae044b513ad3e4535a6e08a` — move/import/link regression tests
- `ba2d24e4b6ebbea4a6ec2afba5697d6a68f284ae` — transient editor replacement race handling
- `55560f15803ff2222e83a5ee1f83523c163290b5` — transient race regression + test cleanup

## Nächste sinnvolle Schritte

1. Qualify this exact head in CI; fix only exact observed failures.
2. If green and Develop has not changed either owned file, Integrator may merge the bounded slice.
3. After integration, implement Beta §38 as a real import-candidate Core/API/UI workflow rather than auto-importing or simulating a button.
4. Separately assess managed-file delete intent (§41–44) and three-way conflict UX (§32–36); do not fold those larger semantics into this branch.
