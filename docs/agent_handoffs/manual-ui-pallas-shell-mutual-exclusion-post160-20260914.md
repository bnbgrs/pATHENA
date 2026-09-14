# Manual handoff — PALLAS shell + ComfyUI exclusion post-162

Date: 2026-09-14
Branch: `manual/ui-pallas-shell-mutual-exclusion-post160-20260914`
Base: `b2063a274984448d5f0db5d1c917c7ee93ae80be`
Status: CANDIDATE_RECONSTRUCTED_PENDING_EXACT_HEAD_GATES

## Scope

This candidate closes the surviving PALLAS full-view shell gap without replacing the already-qualified living engine.

- Move the full PALLAS view from a detached `QDialog` into the existing `referenceBody` shell.
- Preserve the shared right inspector and the routed conversation workspace.
- Reuse exactly one current `PallasLivingQtController` for compact and full fields.
- Preserve Semantic, Age and Vitality lenses plus living diagnostics.
- Restore the routed center and eligible prior focus when PALLAS closes.
- Close PALLAS on primary navigation changes.
- Install the existing local-only ComfyUI integration during real desktop startup through a dedicated external-workspace coordinator.
- Fail closed when optional ComfyUI configuration is invalid: keep pATHENA and PALLAS usable, expose the unavailable reason, and do not register a broken ComfyUI command.
- Keep command-palette truth side-effect free so it reports commands already registered by desktop startup instead of retrying optional ComfyUI installation.
- Enforce bidirectional PALLAS and ComfyUI mutual exclusion without modifying ComfyUI transport, workflow, VRAM or local-only safety semantics.
- Expose truthful shell state through `pathenaPallasShellOpen`, `pathenaExternalWorkspaceMutualExclusion` and `pathenaExternalWorkspaceOwner`.

## Current-base reconciliation

The corrected predecessor head was `9cd535ab519a78ab651a47250bb02563813a1acb`. Before reconstruction, every candidate path was checked against drift through current Develop `b2063a274984448d5f0db5d1c917c7ee93ae80be`; no candidate product or regression file had conflicting Develop changes.

Current Develop canonical ATHENA Quality run #5244 completed SUCCESS on `b2063a274984448d5f0db5d1c917c7ee93ae80be`.

The candidate is reconstructed directly on that green Develop tree from the exact corrected predecessor blobs, not by merging stale branch history. `src/athena/desktop/pathena_window.py` is already byte-identical on current Develop, so it intentionally drops out of the changed-file set. The resulting candidate must remain exactly one commit ahead of Develop.

## Canonical corrections carried forward

The predecessor canonical audit identified and corrected two candidate-local issues before this reconstruction:

- Ruff import ordering in `tests/unit/test_pathena_optional_comfyui_startup.py`.
- Stale detached-`QDialog` expectations in the pre-existing PALLAS full-view regression after the product contract moved to a shell-hosted reusable workspace.

The reconstructed product also carries the startup-order regression proving that invalid optional ComfyUI configuration cannot crash later command-palette truth installation.

## Changed files expected against current Develop

- `docs/agent_handoffs/manual-ui-pallas-shell-mutual-exclusion-post160-20260914.md`
- `src/athena/desktop/app.py`
- `src/athena/desktop/pathena_command_palette_truth_6500.py`
- `src/athena/desktop/pathena_external_workspaces.py` (new)
- `src/athena/desktop/pathena_pallas_full_view.py`
- `tests/unit/test_pathena_optional_comfyui_startup.py` (new)
- `tests/unit/test_pathena_pallas_shell_external_workspaces.py` (new)

No Knowledge, WAL, Source, provider, storage, persistence or CI file belongs to this candidate.

## Non-goals

- No PALLAS graph membership, provenance, force, contradiction, vitality or age-truth changes.
- No ComfyUI HTTP client behavior changes.
- No ComfyUI shell redesign in this slice; later shell-hosting work must be composed explicitly from desktop or external-workspace startup rather than command-palette truth.
- No CI weakening or skip-based Qt coverage.

## Required qualification

1. Verify the branch is exactly one commit ahead of `b2063a274984448d5f0db5d1c917c7ee93ae80be` with only the seven expected changed files.
2. UI Focused Candidate must be green on the exact reconstructed head.
3. Canonical ATHENA Quality Gate must be green on that same exact head.
4. Recheck Develop head and changed-file collisions immediately before merge.
5. Merge only with expected-head protection.
6. Require post-merge Develop canonical Quality before the next integration.

The direct PySide6 regressions are intentionally non-skipping: missing Qt must fail rather than silently hiding a desktop regression.
