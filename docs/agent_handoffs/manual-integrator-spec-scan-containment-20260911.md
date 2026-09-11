# Manual Integrator Handoff — Specification Scan Containment

Generated: 2026-09-11
Branch: `manual/integrator-spec-scan-containment-20260911`
Stacked parent: PR #91 / `manual/integrator-spec-link-boundary-hardening-20260910@abf59e162beaaa8a0728c6354fe937e17a42255a`
Parent canonical Quality: run `34501118537` / #4810 = SUCCESS

## Purpose

Close issue #92 without mutating the exact-green parent candidate or entering active Backend, Errors, Spec/Core, UI, Storage/WAL, Research, packaging, local-quality, or product-runtime ownership.

PR #91 already contains the separate relative-Markdown-link destination boundary. This slice handles the distinct trust boundary for files that the canonical specification validator itself scans or reads.

## Finding

The validator built `markdown_files` from repository-lexical `Path.rglob("*.md")` results and then read those paths normally. A symlink whose lexical path lived inside the checkout but whose real target lived outside the checkout could therefore contribute host content to Markdown structure checks and aggregate normative-text checks.

A second path existed through direct Alpha/Beta reads (`glob()` and named files). Merely filtering the global Markdown list would not protect those direct reads.

## Implementation

`scripts/validate_spec.py` now has one shared real-target boundary:

- `resolve_repository_scan_target()` resolves a candidate and requires its real path to remain under the resolved repository root;
- resolution errors, loops, and out-of-root targets fail closed;
- `collect_repository_scan_files()` excludes unsafe candidates from both the general file list and Markdown scan list while returning their repository-relative names for an explicit validator failure;
- the validator adds `Repository scan inputs stay inside root` as a first-class check;
- `read_text()` applies the same real-target guard before every repository text read, covering direct Alpha/Beta/index/README reads as well as the global scan list;
- the existing PR #91 link resolver is also made fail-closed for resolution errors/loops while preserving its in-root and missing-local semantics.

Policy decision: symlinks whose resolved target remains inside the repository are allowed. This is the least disruptive containment policy and avoids silently changing legitimate repository-local alias behavior. External targets are never admitted as specification evidence.

## Focused regression coverage

`tests/unit/test_validate_spec_scan_containment.py` covers:

- ordinary repository Markdown collection;
- existing external Markdown symlink exclusion + explicit unsafe evidence;
- missing external symlink target exclusion;
- in-repository symlink allowance;
- ignored scan-root behavior remaining ignored rather than becoming evidence.

`tests/unit/test_validate_spec_read_boundary.py` separately proves:

- a normal in-repository read succeeds;
- an external symlink is refused by the central reader before content is read.

Capability-dependent symlink creation skips explicitly when the host cannot create symlinks.

## Collision / worker review

Observed live heads during this run before later drift:

- Develop: `4634bdf28c98bc114e0369701122818d474f99d9`
- Backend: `44201f9dd2c1378c98afccc9a30ddf18c98b2405` (latest commit documentation-only failure handoff)
- Errors: `298bbf8ab08a680cb5157651ffa293ce544c62e1` (documentation handoff)
- Spec/Core: `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e` (documentation handoff)
- UI: `d55877cd353f7ee598df8213b9508fb143e51e15` (documentation handoff)
- separate screenshot-parity work remains on `agent/ui-11-reference-parity-20260911` and is intentionally untouched.

This candidate is stacked on the exact-green #91 head because the two changes intentionally touch the same validator file. The parent branch is not moved. No worker branch is changed.

Before this handoff commit, the delta versus the exact parent was 4 commits ahead / 0 behind and touched only:

- `scripts/validate_spec.py`
- `tests/unit/test_validate_spec_scan_containment.py`
- `tests/unit/test_validate_spec_read_boundary.py`

## Concurrent Develop drift observed during this run

Develop advanced independently after the isolation decision from `4634bdf28c98bc114e0369701122818d474f99d9` to `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c` with `test(ui): align design-system typography contract`.

The preceding exact Develop Quality run `34539454111` was inspected read-only. Its only failure was `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales`: the test still expected typography `(14, 11, 34)` while the integrated UI token values were `(15, 12, 42)`. The run otherwise reported `4830 passed, 3 skipped`; specification validation, Ruff, mypy, native Windows path/storage/runtime lanes, Linux storage and local-install smoke were green. The new Develop commit updates that stale UI test expectation, so this manual branch deliberately does not duplicate or modify the UI fix.

This drift does not alter the child slice ownership. Rebase/recreation onto current Develop remains an Integrator step only after the exact-green parent #91 is consumed.

## Verification boundary

No local full-repository PASS is claimed from the current execution environment because direct network clone/materialization is unavailable here. The exact parent is independently canonical-green. This branch must obtain canonical GitHub Quality on its own exact head before integration.

Do not interpret a future CI failure outside these owned paths as permission to widen this candidate. Classify exact failure evidence first.

## Integration order

1. Keep PR #91 frozen at its exact-green head.
2. Validate this stacked candidate on its exact head.
3. Integrate/recreate #91 against then-current Develop first.
4. Rebase or recreate this small child delta onto that integrated state and obtain fresh exact-head evidence before promotion.
5. Close issue #92 only after the containment behavior reaches the integration branch.

## Bot consumption rules

Bots may treat the real-target containment rule as canonical intent, but must not edit this branch or copy only half of the mechanism. In particular, filtering `markdown_files` without retaining the guarded `read_text()` path is incomplete because direct Alpha/Beta reads would remain capable of following external symlinks.
