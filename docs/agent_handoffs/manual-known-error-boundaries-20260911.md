# Manual known-error boundary closure handoff — 2026-09-11

## Exact lineage

Base: `develop/pathena-next@0298f0c4f2d28e516a458390f8b462131ebaf17e`
Branch: `manual/known-error-boundaries-20260911`
Initial product commit: `cd0f4d1fc10afa8994db515eb710f30077b0dcbf`

This is an isolated Integrator repair candidate. It does not mutate `develop/pathena-next`, `main`, or any `postmerge/*` worker branch.

## Known defects closed in this candidate

### Windows explicit SmokeRoot repository escape

Ported from the bounded PR #94 implementation onto current Develop. `scripts/check_windows.ps1` now applies `Assert-PathenaRuntimeRootOutsideRepository` after canonical path normalization and before forwarding an explicit persistent `--keep-root`. The focused contract test proves guard ordering before the smoke process starts.

Owned paths:
- `scripts/check_windows.ps1`
- `tests/unit/test_windows_check_script_contract.py`

### Windows packaging recursive OutputRoot deletion

Ported from PR #97 / Issue #96 onto current Develop. Caller-controlled output is validated before any recursive cleanup. Unsafe repository roots/ancestors, source-tree paths, filesystem roots, unowned existing directories/files, and reparse-point chains fail closed. Reusable custom output requires the pATHENA ownership marker. Existing package topology and pinned PyInstaller behavior remain unchanged.

Owned paths:
- `scripts/build_windows_portable.ps1`
- `scripts/windows_packaging_safety.ps1`
- `tests/unit/test_windows_packaging_contract.py`

### Specification validator root/symlink containment

Ported from PR #102 / Issue #92 onto current Develop. Repository scan candidates and direct read paths resolve to real targets and must remain within repository root. Relative Markdown destinations escaping the repository fail closed. Symlink loops/resolution failures are rejected.

Owned paths:
- `scripts/validate_spec.py`
- `tests/unit/test_validate_spec_links.py`
- `tests/unit/test_validate_spec_read_boundary.py`
- `tests/unit/test_validate_spec_scan_containment.py`

## Exact blob provenance

The product/test blobs were reused from the existing bounded candidates rather than retyped:

- SmokeRoot script `3c6d689a7d610cf4986c52223991647f789f11d9`
- SmokeRoot test `5b5e83015c4279a530ec5abc4cfce0cc8475cd51`
- packaging script `ae91afd863af8bfd01b214a1ed2b473785a3f515`
- packaging safety helper `8c2735d6f829bb36fc540c460055988bba3bc236`
- packaging test `d06944581128eeb3ab1960ea3a404f96f468b6c4`
- spec validator `86425b26305b0e067bd2d24417548d84194e6243`
- spec-link test `b1766ac4cd0f4bd53881693914cfc02bc6d4ef57`
- spec-read test `02b893da7892574e968db80f493c72a80d7dc870`
- spec-scan test `c11a5175d71d2ce8daefe8e1ecf1a45412c18d5c`

## Bot rules

1. Do not copy these fixes into an active worker branch while this exact candidate is validating.
2. Treat failures outside the owned paths as baseline/other-worker/platform evidence until proven otherwise.
3. Never weaken or skip the unsafe-path assertions to obtain green CI.
4. PR #94, #97 and #102 remain provenance; once equivalent code reaches Develop they can be closed as superseded rather than merged again.
5. Issue #92 and #96 should remain open until the equivalent implementation is actually integrated and exact-head canonical evidence is green.
6. Issue #93 (shared Windows junction/reparse physical-path boundary) and Issue #95 (execute `check_windows.ps1` on the Windows quality runner) are separate known gaps and are not claimed closed by this commit.
7. ERR-0033 / BE-046 and ERR-0035 / BE-052 remain Backend-owned storage/recovery defects and are not claimed closed here.
8. ERR-0039 remains open until an exact Ruff-green Spec/Core import fix exists.
9. A green historical SHA is not promotion evidence for this new current-Develop SHA. Require exact-head CI.
10. Before integration, refresh `develop/pathena-next` and worker heads and re-check collision state.

## State

Implementation for the three bounded boundary defects: complete on this branch.
Canonical exact-head validation: to be obtained via Draft PR.
Merge: not authorized by this handoff until exact-head evidence is reviewed.