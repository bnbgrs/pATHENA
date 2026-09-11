# Manual Windows runtime-boundary and wrapper-CI handoff — 2026-09-11

## Lineage

Parent candidate: `manual/known-error-boundaries-20260911@80b6c095d12da371a1e58dd1b16c0ea72a5566ea` (PR #106)
Branch: `manual/windows-runtime-boundary-ci-20260911`

This is a stacked, isolated Integrator slice. It deliberately does not modify `develop/pathena-next`, `main`, any `postmerge/*` worker branch, or the Backend-owned canonical `.github/workflows/quality.yml`.

## Known gap #93 — junction/reparse aliases

`Assert-PathenaRuntimeRootOutsideRepository` previously used only lexical `GetFullPath` normalization. That could not prove physical separation when a Windows junction/reparse point existed in the repository or runtime ancestor chain.

The candidate now fails closed if either existing path chain traverses a reparse point before applying the existing case-insensitive lexical repository-descendant check. This deliberately chooses a conservative policy instead of trusting ambiguous aliases:

- ordinary real outside paths remain accepted;
- normalized repository descendants remain rejected;
- an outside junction alias into the repository is rejected;
- a repository checkout itself reached through a junction is rejected for this boundary check;
- a future/nonexistent outside runtime directory remains accepted when its existing ancestor chain is real.

The repository-junction refusal is intentional. A caller must use the real checkout path when asking pATHENA to prove source/runtime separation.

Native Windows tests live in `tests/unit/test_windows_runtime_root_boundary.py`.

## Known gap #95 — check_windows wrapper never executed by CI

A dedicated additive workflow, `.github/workflows/windows-runtime-boundary.yml`, runs on `windows-latest` for this boundary surface. It:

1. checks out and proves the exact candidate SHA;
2. installs pinned Python/uv and validates the lock;
3. synchronizes the locked dev+desktop environment;
4. runs the native reparse boundary tests plus the SmokeRoot ordering contract;
5. executes the supported `scripts/check_windows.ps1` wrapper itself with a temporary outside-repository `ATHENA_LOCAL_ROOT` and persistent outside-repository `SmokeRoot`.

This closes the evidence gap without editing the Backend-owned canonical `quality.yml`. The additive gate can later be folded into canonical Quality by an explicit Backend/Integrator decision, but equivalent native evidence must not be removed.

## Bot rules

1. Do not duplicate these changes in `postmerge/backend` or another active worker while this stacked candidate validates.
2. Do not weaken the conservative reparse policy merely to make a junction-based checkout pass; first decide and document a different physical-path resolution policy.
3. Do not replace the native wrapper execution with source-text assertions only.
4. PR #106 is the required parent because it supplies the explicit `check_windows.ps1 -SmokeRoot` guard call site.
5. If the dedicated workflow is green, #93 and #95 have implementation/evidence candidates. Keep the issues open until the equivalent changes are integrated into Develop.
6. If the workflow is red, classify whether the failure is helper policy, Windows test capability, diagnostic-wrapper runtime, or unrelated environment setup before changing code.
7. Any future consolidation into `.github/workflows/quality.yml` must preserve exact-head checkout and native Windows execution.
