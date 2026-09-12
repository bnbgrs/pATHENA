# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `5eecb5f937de9325a9673df5f1a23d2f1b5e87cf`.
- Exact parent canonical Quality: `34706615596 = SUCCESS`.
- Worker heads checked: Errors `3e3915d5cb0c3964661db1fcef100f98664915c1`; Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; Backend `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`; UI `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`.

## Worker qualification

- Spec/Core exact `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`: Core Focused Candidate `34709904332 = FAILURE`; exact focused pytest passed six tests but Ruff still reports one I001. Canonical Quality `34709904327` was active at qualification time. NOT READY.
- Backend exact `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`: Backend Focused Candidate `34710537347 = SUCCESS`, but Storage Focused Candidate `34710537370 = FAILURE`; canonical Quality `34710537369` was active. Storage remains conservatively blocked. NOT READY.
- UI exact `1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`: UI Focused Candidate succeeded, but Core Focused failed because deleted Core/test paths were selected and the worker lineage is broad/diverged. No UI product slice is imported from this branch in this integration.
- Errors handoff identifies current open clusters `ERR-0042` Core Ruff formatting, `ERR-0043` Storage sidecar identity continuity, and `ERR-0044` Core Focused workflow deleted-path/remediation harness behavior.

## Cross-cutting integration

This integration closes the repository-side root cause of `ERR-0044` in `.github/workflows/core-focused-candidate.yml` without weakening any test or gate:

- changed Core Python selection now uses `git diff --diff-filter=ACMR --name-only`, excluding deleted paths while retaining added/copied/modified/renamed paths;
- changed focused-test selection uses the same fail-closed non-deletion filter;
- Ruff remediation selection uses the same filter;
- remediation cleanliness checks now ignore only untracked files via `--untracked-files=no`, so the workflow's own `.focused-evidence` artifacts no longer block diagnostic remediation while tracked candidate mutations still fail the cleanliness guard;
- the exact candidate SHA identity check, Ruff requirement, focused pytest requirement, immutable reset, diagnostics upload, and final outcome enforcement remain intact.

No Product, Storage, Recovery, Security, UI, packaging, runtime-topology, Skip/XFail, or assertion semantics are relaxed.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to current Develop and is not the sole authority for current OPEN state.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` is maintained without invented completion percentages.
- Historical signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed; no screenshot `MATCH` is inferred without opened original reference plus a real exact-SHA render.
- Worker candidate evidence superseded by later commits is not accepted without equivalent exact-head evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup, and storage-bootstrap regression signatures. No Skip/XFail, assertion weakening, test deletion, Security/Storage/Recovery guard relaxation, force push, history rewrite, auto-merge, or main mutation is introduced.

## Promotion state

`PROMOTION_READY=NO`

Consume canonical Quality for the resulting exact Develop SHA before any further Develop mutation. `main` and `bnbgrs/ATHENA` remain read-only.
