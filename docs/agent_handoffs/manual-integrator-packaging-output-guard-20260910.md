# Manual Integrator Handoff — Windows Packaging Output Guard — 2026-09-10

## Scope

This is a bounded manual Integrator/maintenance slice for Issue #96. It hardens the destructive cleanup boundary in `scripts/build_windows_portable.ps1` without changing active worker branches, product runtime behavior, canonical workflow configuration, UI, Core, Storage, Research, or the error/spec ledgers.

Branch:

`manual/integrator-packaging-output-guard-20260910`

Exact branch base:

`develop/pathena-next@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`

Issue:

`#96 Windows packaging: fail closed before recursively deleting OutputRoot`

## Finding confirmed

The current Windows portable build accepted arbitrary `-OutputRoot`, normalized it with `[System.IO.Path]::GetFullPath(...)`, then included the caller-selected path in the same unconditional recursive cleanup loop as known internal build directories.

Before this slice there was no packaging-specific proof that an existing caller-selected output directory was disposable pATHENA-owned state. A repository directory, repository ancestor, filesystem root, unrelated external directory, or other unsafe target could therefore reach `Remove-Item -Recurse -Force` if supplied as `-OutputRoot`.

No destructive reproduction was used. The defect was established from exact source trace and is covered by fail-closed tests.

## Ownership policy implemented

The build now loads a packaging-only helper:

`scripts/windows_packaging_safety.ps1`

The helper separates caller-controlled output validation from the build implementation and defines a narrow ownership contract:

1. The existing default output `dist/windows-portable` remains accepted for backward compatibility, including an existing output created by older pATHENA builds that predates the new marker.
2. Filesystem roots are rejected.
3. The repository root and every ancestor of the repository checkout are rejected.
4. Paths inside the repository are accepted only inside the managed `dist/windows-portable` subtree. Source-tree paths such as `src` are rejected even when the requested child does not yet exist.
5. A fresh custom output outside the repository is accepted only when the target does not already exist and its existing path chain contains no junction/reparse point.
6. A pre-existing custom output is accepted only when it is a directory carrying the exact pATHENA ownership marker `.pathena-windows-portable-output` with value `pATHENA Windows Portable Output v1`.
7. Existing file targets are rejected.
8. Existing junction/reparse-point aliases in the candidate path chain are rejected rather than resolved and trusted implicitly.
9. After a validated output root is recreated, the build writes the ownership marker before invoking PyInstaller. A successful or partially completed build directory is therefore recognizable as pATHENA-owned on the next explicit custom build.

The marker is intentionally an ownership sentinel, not an authentication mechanism. Its purpose is to prevent accidental recursive deletion of unrelated pre-existing directories selected through `-OutputRoot`.

## Destructive-order invariant

`build_windows_portable.ps1` now performs this order:

1. resolve default/custom output;
2. call `Assert-PathenaPortableOutputRoot`;
3. only after validation, perform the existing recursive cleanup loop;
4. recreate output/work/spec/worker directories;
5. write the pATHENA ownership marker into the validated output root;
6. continue the existing pinned PyInstaller build.

The output validation therefore runs before the first `Remove-Item -LiteralPath $path -Recurse -Force` that can operate on the caller-controlled output root.

The fixed internal cleanup roots under `build/windows-portable*` remain deterministic and unchanged.

## Packaging behavior intentionally preserved

The candidate does not weaken or redesign the package format. It retains:

- `uv sync --locked --extra desktop`;
- pinned `pyinstaller==6.15.0`;
- `--collect-all pypdf`;
- PyInstaller `--onedir` with `app_runtime`;
- the separate `pATHENA.exe` and `pATHENA-Worker.exe` topology;
- the existing fail-closed packaged-worker dispatch contract;
- `CHECK_HARDWARE.cmd` and the existing hardware-acceptance flow;
- current package assembly and worker-runtime merge semantics.

## Tests

The existing `tests/unit/test_windows_packaging_contract.py` is extended rather than adding a new workflow-only test surface. This is deliberate: `.github/workflows/quality.yml` already runs that exact file in the native `windows-path-safety` job, so the new runtime cases receive Windows evidence without changing shared workflow configuration.

Static cross-platform contracts verify:

- the packaging-only safety helper is loaded;
- output validation appears before the first recursive cleanup;
- the ownership marker is written only after the validated output root is recreated;
- release dependency and two-EXE packaging contracts remain present;
- the helper retains marker, reparse-point, source-subtree, and unowned-directory guards.

Native Windows cases cover:

- existing default output;
- fresh custom external output;
- fresh custom child below the managed output subtree;
- repeated custom output carrying the exact ownership marker;
- repository root;
- `src`;
- repository ancestor;
- filesystem/drive root;
- unrelated pre-existing external directory;
- existing file target;
- case-variant source path;
- existing junction output when junction creation is available on the runner.

Local extracted verification before publication:

- `python -m py_compile tests/unit/test_windows_packaging_contract.py`: PASS
- `pytest -q tests/unit/test_windows_packaging_contract.py`: `5 passed, 10 skipped in 0.06s`

The local environment is Linux and has no PowerShell executable. The ten skipped cases are intentionally native-Windows path tests. No local PowerShell-runtime PASS is claimed. The existing GitHub `windows-path-safety` job is authoritative for those cases.

## Exact pre-handoff branch delta

Before this handoff file was added, comparison against the exact base showed:

- ahead by 3 commits;
- behind by 0 commits;
- exactly three changed files;
- `scripts/build_windows_portable.ps1`: modified;
- `scripts/windows_packaging_safety.ps1`: added;
- `tests/unit/test_windows_packaging_contract.py`: modified.

This handoff is the intended fourth owned path.

## Worker collision review

Worker state was refreshed after implementation, not inferred from the initial snapshot.

Observed heads:

- Backend: `postmerge/backend@49ff66eeb706695d0564bf87274a5f9087b8ef98`
- Errors: `postmerge/errors@d6ef65e11106aa6d43eba8c22c4173ee9c63ce60`
- Spec/Core: `postmerge/spec-core@b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`
- UI: `postmerge/ui@af50dfb76b04e396a2dbf65ec1eeb265f30177fa`

Exact compare against the run base showed no worker delta touching any of this candidate's three implementation/test paths.

Backend has a broad divergent delta involving Quality, Core/Application, Desktop window/settings, Research Delta, Storage/WAL and associated tests, but not `scripts/build_windows_portable.ps1`, `scripts/windows_packaging_safety.ps1`, or `tests/unit/test_windows_packaging_contract.py`.

Errors changes only `docs/agent_handoffs/errors.md` and `docs/agent_logs/ERROR_LEDGER.md` relative to the run base. Spec/Core changes only its handoff. UI changes UI handoff/reference ledgers, shared UI/window code, and their tests. None overlaps this packaging slice.

The worker heads changed while this manual run was active, confirming that this candidate did not require pausing or rewriting worker branches.

## Exact owned paths

Reserve only these paths while this candidate validates:

1. `scripts/build_windows_portable.ps1`
2. `scripts/windows_packaging_safety.ps1`
3. `tests/unit/test_windows_packaging_contract.py`
4. `docs/agent_handoffs/manual-integrator-packaging-output-guard-20260910.md`

This branch is a bounded manual candidate, not a new permanent worker lane.

## Deliberate non-work

This slice intentionally does not modify:

- `develop/pathena-next` directly;
- `main`;
- any `postmerge/*` worker branch;
- `.github/workflows/quality.yml`;
- `scripts/windows_common.ps1`;
- `scripts/check_windows.ps1` or frozen PR #94;
- Core/Application;
- Desktop/MainWindow/UI product code;
- Storage/WAL/schema;
- Research Delta;
- Alpha/Beta specification content;
- shared worker handoffs;
- error ledger;
- release promotion state.

Issue #96 specifically asked that PR #94 not be widened. This candidate remains independent.

## Reparse-point boundary

This slice takes the conservative packaging-specific action of rejecting candidate output paths whose relevant existing path chain contains a junction/reparse point. It does not change the shared Windows runtime-root helper or define a repository-wide physical-path policy.

If the separate Windows physical-path investigation later establishes a different canonical reparse policy, update the packaging helper deliberately with native Windows evidence rather than silently inheriting shared-helper behavior.

## Bot consumption rules

1. Treat this branch as a frozen bounded packaging candidate once its Draft PR is opened.
2. Do not copy these changes into Backend/UI/Errors/Spec-Core while the candidate validates.
3. Do not modify the four owned paths from another worker unless ownership is explicitly transferred.
4. Keep PR #94 independent; it owns the `check_windows.ps1 -SmokeRoot` boundary and must not be folded into this candidate.
5. Native `windows-path-safety` evidence is required before integration because the destructive path semantics are Windows-specific.
6. If canonical Quality fails outside these four paths, classify baseline/platform/other-worker evidence before widening this candidate.
7. If a failure is owned by this slice, repair only the bounded packaging cause and obtain fresh exact-head evidence.
8. Do not weaken or skip the unsafe-target assertions to obtain green CI.
9. Before integration, refresh `develop/pathena-next` and all worker heads and re-check the four owned paths for collisions.
10. A green candidate SHA is evidence only for that exact SHA. Any recreated/rebased/merge-result SHA requires its own canonical evidence before promotion.
11. Do not close Issue #96 until native Windows tests and canonical Quality are green on the exact integration candidate.
12. Do not infer overall Alpha/Beta completion percentages from this maintenance slice.

## Integration state at handoff creation

Implementation: complete on the manual candidate branch.

Cross-platform static/focused test: green (`5 passed, 10 skipped`).

Native Windows guard tests: pending canonical `windows-path-safety` execution.

Canonical full Quality: pending Draft PR execution.

Merge: not performed and not claimed safe until exact-head CI is reviewed.
