# Manual Integrator Handoff — Current-Develop Specification Validator Boundaries

Generated: 2026-09-11
Branch: `manual/integrator-spec-validator-boundaries-20260911`
Base: `develop/pathena-next@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c`
Product/test commit: `4aa2547b7adf247aa198adc9fe43760ddd860b18`

## Purpose

Provide one current-Develop integration candidate for the two related but distinct specification-validator trust boundaries that were previously split across the exact-green PR #91 and stacked PR #100.

This branch does not replace the historical evidence. It ports the exact already-published code/test blobs onto the then-current Develop head so the Integrator does not need to merge an old divergent stack.

## Included boundaries

### Relative Markdown link destinations

Origin: PR #91 `Integrator: fail closed on spec-link root escapes`.

The validator resolves a relative Markdown link target to its real path and accepts it only when the destination remains under the resolved repository root. Existing `../` traversal escapes, symlinks to existing external files, and resolution errors/loops fail closed. Missing repository-local destinations remain local and are still handled by the existing missing-target check.

### Repository scan and read inputs

Origin: issue #92 and stacked PR #100.

The validator now:

- resolves every repository scan candidate before admitting it as validation evidence;
- excludes out-of-root real targets from both the general file list and Markdown scan list;
- reports unsafe scan inputs through the explicit `Repository scan inputs stay inside root` invariant;
- applies the same real-target boundary in central `read_text()` so direct Alpha/Beta/index/README reads cannot bypass the global scan filter;
- allows symlinks whose final real target remains inside the repository;
- fails closed on resolution errors and symlink loops.

The central read guard is required. Filtering only `ROOT.rglob()` would leave direct named and `glob()` reads capable of following external symlink targets.

## Exact blob provenance

The current-Develop commit was assembled from exact existing repository blobs rather than manually retyping the implementation:

- `scripts/validate_spec.py` — `86425b26305b0e067bd2d24417548d84194e6243`
- `tests/unit/test_validate_spec_links.py` — `b1766ac4cd0f4bd53881693914cfc02bc6d4ef57`
- `tests/unit/test_validate_spec_read_boundary.py` — `02b893da7892574e968db80f493c72a80d7dc870`
- `tests/unit/test_validate_spec_scan_containment.py` — `c11a5175d71d2ce8daefe8e1ecf1a45412c18d5c`

The first two originate from the #91 lineage whose exact head `abf59e162beaaa8a0728c6354fe937e17a42255a` passed canonical Quality run `34501118537` / #4810. The scan/read additions originate from #100, whose exact-head Quality evidence remains separately authoritative when completed.

## Focused contracts

`test_validate_spec_links.py` covers:

- valid in-repository relative destination;
- existing parent traversal outside root;
- in-repository symlink resolving to an external file;
- missing but still repository-local destination.

`test_validate_spec_scan_containment.py` covers:

- ordinary Markdown scan collection;
- external Markdown symlink exclusion and explicit unsafe evidence;
- missing external symlink target;
- allowed in-repository symlink;
- ignored scan-root behavior.

`test_validate_spec_read_boundary.py` separately proves normal in-root reads and fail-closed external-symlink reads.

Symlink-dependent tests skip only when the host cannot create symlinks; no implementation failure is converted to Skip/XFail.

## Develop drift consumed

This branch starts after Develop commit `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c` (`test(ui): align design-system typography contract`). That commit repaired the sole failure from previous exact Develop Quality run `34539454111`: a stale UI design-system test expected `(14, 11, 34)` while integrated typography tokens were `(15, 12, 42)`. The preceding run otherwise reported 4830 passed / 3 skipped, with specification validation, Ruff, mypy and the dedicated Windows/Linux/local-install lanes green.

No UI file is changed by this candidate.

## Ownership / collision boundary

Owned paths are exactly:

- `scripts/validate_spec.py`
- `tests/unit/test_validate_spec_links.py`
- `tests/unit/test_validate_spec_read_boundary.py`
- `tests/unit/test_validate_spec_scan_containment.py`
- this handoff document.

No Backend, Storage/WAL, Recovery, Research, UI product, packaging, workflow, runtime or Alpha/Beta normative content is changed.

The active `agent/ui-11-reference-parity-20260911` line remains untouched. Existing Backend/Errors/Spec-Core/UI worker branches remain untouched.

## Promotion rule

This current-Develop branch requires canonical Quality on its own exact head before integration. Historical #91 success proves the parent mechanism but is not sufficient evidence for the combined current-Develop candidate.

If this branch becomes exact-head green and remains conflict-free against then-current Develop, prefer it as the integration vehicle. Do not additionally merge #91 and #100 afterward; those PRs should remain provenance/evidence and can be closed as superseded only after the equivalent combined behavior reaches Develop.

Issue #92 must remain open until the scan/read containment behavior is actually integrated.

## Bot consumption rule

Bots may consume this handoff as the preferred reconciliation plan. They must not broaden this candidate to unrelated current failures. If exact Quality fails, first classify the failing test and compare it with the five owned paths before modifying anything.
