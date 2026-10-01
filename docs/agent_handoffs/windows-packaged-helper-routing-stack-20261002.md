# Windows packaged helper routing follow-up — 2026-10-02

## Ausgangslage

This branch is intentionally stacked on PR #339 exact head
`8d985f3ad04442a3d6d87883de0a48a8743d7a60` ("Windows: restore Sources workspace
in packaged build"). It does not reimplement or replace #339's Sources work.

The supported frozen Windows desktop rewrites `sys.executable` from
`pATHENA.exe` to the strict sibling `pATHENA-Worker.exe`. #339 restores the
Sources helper role, but the same packaging contract is also used by these existing
desktop call sites:

- `athena.desktop.research_cli`
- `athena.desktop.research_results_cli`
- `athena.desktop.knowledge_cli`
- `athena.desktop.knowledge_obsidian_export`
- `athena.desktop.canonical_memory_cli`

On current Develop those roles remain absent from the worker allowlist/dispatcher,
so the corresponding source-checkout workflows can work while the packaged Windows
desktop rejects their child process with the fail-closed unknown-module path.

## Root Cause

The frozen desktop process topology is intentional and should remain fail-closed.
The explicit packaged-module allowlist drifted behind the set of real desktop
`sys.executable -m ...` helper boundaries. Package smoke coverage was too narrow to
detect that drift.

## Änderungen

Built on top of #339 without removing its Sources route, unit coverage, or durable
Sources restart smoke:

- Added explicit packaged targets/allowlist entries for Research, Research Results,
  Knowledge, Obsidian export, and canonical-memory helper modules.
- Added matching lazy dispatch in `pATHENA-Worker.exe`.
- Kept every unknown module rejected; no generic Python/module execution is enabled.
- Added route and real lazy-dispatch unit coverage for all five new roles.
- Added a source-level regression guard: every literal desktop Python file that
  contains `sys.executable` and a literal `-m <module>` dispatch must resolve
  through the packaged router. A future unregistered helper therefore fails the
  packaging contract test.
- Extended packaged worker `--help` smoke to all desktop helper roles.
- Added real packaged lifecycle/persistence smoke:
  - Research enqueue -> fresh Research show -> Jobs show for the same durable job;
  - Knowledge and canonical-memory read lifecycle;
  - Research Results reaches its real application boundary and returns an expected
    domain error for a missing result (not a worker routing error);
  - after the existing persistent Knowledge smoke, `knowledge_cli` recovers the
    promoted item and `knowledge_obsidian_export preview` executes against a real
    temporary vault.
- Updated generated `START_HERE.txt` worker-role description.

## Dateien dieses Follow-ups relativ zu #339

- `src/athena/desktop/packaged_app.py`
- `src/athena/desktop/packaged_worker.py`
- `tests/unit/test_windows_packaging_contract.py`
- `.github/workflows/windows-package.yml`
- `scripts/build_windows_portable.ps1`
- this handoff

#339 itself already owns the Sources portions of the first four files.

## Verhalten danach

With #339 + this follow-up, every currently identified desktop helper that relies on
the frozen `sys.executable` worker redirection has an explicit packaged role.
Research, Research Results, Sources, Knowledge, Obsidian export and canonical-memory
actions no longer depend on source-checkout Python semantics to start their helpers.

## Validierung bisher

- Follow-up branch created directly from #339 exact head
  `8d985f3ad04442a3d6d87883de0a48a8743d7a60`.
- Diff against #339 is **ahead 5 / behind 0** before this handoff.
- Relative-to-#339 diff contains only the five intended packaging/test/workflow/docs
  files above; no Sources workspace implementation file is touched.
- Existing active product ownership was rechecked. This follow-up does not touch:
  Chat cancellation/branching, LM Studio runtime, Settings, Storage, Source UI import
  queue/ownership, Knowledge workspace selection ownership, Jobs CLI framing, Security,
  Logging, Backup or PALLAS product files.
- Direct local checkout/test is blocked in this execution environment because
  github.com DNS resolution fails. No local PASS is claimed.
- Exact-head GitHub Actions/native Windows package results are required before merge.

## Parallel dependencies / conflict risk

- **Depends on #339.** Do not cherry-pick the Sources lines from this follow-up while
  separately merging #339; this branch already contains #339's exact commits.
- PR #353 changes the six helper CLI lifecycle implementations (storage-only instead
  of full Core start/stop) but does not touch packaged routing files. If #353 merges
  first, rerun the Windows package smoke on the rebased/updated candidate because the
  helper lifecycle behavior will have changed underneath this packaging contract.
- Historical PR #314 touches `.github/workflows/windows-package.yml` from an old
  candidate and must not overwrite the current workflow.
- The earlier broad draft #347 was an independent implementation started before #339
  appeared. It should remain closed/superseded once this stacked PR exists.

## Nächste sinnvolle Schritte

1. Run exact-head Quality + native Windows Package on the combined #339 + follow-up
   candidate.
2. Fix only failures attributable to this branch; do not weaken fail-closed routing.
3. Merge #339 first.
4. After #339 lands, retarget/refresh this follow-up against current
   `develop/pathena-next`; its Sources diff should disappear because the commit
   ancestry is shared.
5. Re-run exact-head gates after any Develop movement, especially if #353 merges.
6. On a real Windows candidate, click through Research, Research Results, Knowledge,
   canonical-memory and Obsidian preview from the desktop, not only worker CLI smoke.

## Branch

- Follow-up branch: `fix/windows-packaged-helper-routing-stack-20261002-sol`
- Stack base: `#339 @ 8d985f3ad04442a3d6d87883de0a48a8743d7a60`
- Original Develop ancestor: `67174198e1494fd4c8678aad60756c39ef5c160b`
