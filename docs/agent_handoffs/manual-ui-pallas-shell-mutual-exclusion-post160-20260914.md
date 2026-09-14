# Manual handoff — PALLAS shell + ComfyUI exclusion post-162

Date: 2026-09-14
Branch: `manual/ui-pallas-shell-mutual-exclusion-post160-20260914`
Base: `cbe5854e35f6914cc785a2397718f6faff44eb03`
Status: CANDIDATE_NOT_YET_QUALIFIED

## Scope

This candidate closes the surviving PALLAS full-view shell gap without replacing the already-qualified living engine.

- Move the full PALLAS view from a detached `QDialog` into the existing `referenceBody` shell.
- Preserve the shared right inspector and the routed conversation workspace.
- Reuse exactly one current `PallasLivingQtController` for compact and full fields.
- Preserve Semantic, Age and Vitality lenses plus living diagnostics.
- Restore the routed center and eligible prior focus when PALLAS closes.
- Close PALLAS on primary navigation changes.
- Install the existing local-only ComfyUI integration during real desktop startup through a dedicated external-workspace coordinator.
- Enforce bidirectional PALLAS/ComfyUI mutual exclusion without modifying ComfyUI transport, workflow, VRAM or local-only safety semantics.
- Expose truthful shell state through `pathenaPallasShellOpen`, `pathenaExternalWorkspaceMutualExclusion` and `pathenaExternalWorkspaceOwner`.

## Base drift reconciliation

Develop advanced from `0ea74a990f8375039769c7726a327fd9142d5985` to `cbe5854e35f6914cc785a2397718f6faff44eb03` through #162 while this candidate was being assembled. The intervening delta only added a PALLAS living-edge Qt regression and its handoff; none of this candidate's production or regression files collided. This candidate was reconstructed directly on the newer Develop tree rather than merging a stale candidate branch.

## Non-goals

- No PALLAS graph membership, provenance, force, contradiction, vitality or age-truth changes.
- No ComfyUI HTTP/client behavior changes.
- No attempt to make ComfyUI a routed first-class workspace in this slice; its existing modeless surface remains intact.
- No CI weakening or skip-based Qt coverage.

## Files

- `src/athena/desktop/pathena_pallas_full_view.py`
- `src/athena/desktop/pathena_external_workspaces.py` (new)
- `src/athena/desktop/app.py`
- `tests/unit/test_pathena_pallas_shell_external_workspaces.py` (new)

## Required qualification

1. UI Focused Candidate on exact candidate head.
2. Canonical ATHENA Quality Gate on exact candidate head.
3. Post-#162 `develop/pathena-next` canonical Quality must be green.
4. Recheck changed-file set and base/head drift before merge.
5. Merge only with expected-head protection.
6. Require post-merge Develop canonical Quality before the next integration.

The new regression imports PySide6 directly. Missing Qt must fail rather than silently skip.
