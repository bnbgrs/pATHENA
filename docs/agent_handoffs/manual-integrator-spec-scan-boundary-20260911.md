# Manual Integrator handoff — specification scan containment — 2026-09-11

## Status

IMPLEMENTED -> STACKED ON CANONICAL-GREEN PR #91 -> CANONICAL EXACT-HEAD QUALITY REQUIRED

This is a bounded follow-up for GitHub issue #92. It is intentionally stacked on the exact head of PR #91 instead of widening PR #91 or mutating current Develop directly.

## Lineage

- Parent branch: `manual/integrator-spec-link-boundary-hardening-20260910`
- Parent exact head: `abf59e162beaaa8a0728c6354fe937e17a42255a`
- Parent canonical Quality: run `34501118537` / #4810 = SUCCESS
- Follow-up branch: `manual/integrator-spec-scan-boundary-20260911`
- Stable `main` remains untouched.
- Current `develop/pathena-next` continues independently and must not be frozen by this stacked candidate.

PR #91 already hardens relative Markdown link destinations against real-path escape. This follow-up addresses the distinct scan-input trust boundary recorded in issue #92.

## Problem

The canonical validator builds `all_files` and `markdown_files` from `ROOT.rglob(...)`. Before this follow-up, `included_in_repository_scan()` only checked the lexical first path component against the ignore list.

For a file symlink such as:

`repo/docs/external.md -> /outside/host-file.md`

`ROOT.rglob("*.md")` can yield the in-repository lexical path and `read_text(path)` follows the symlink. Host content outside the repository candidate could therefore participate in Markdown structure checks, link checks and aggregate normative-text checks.

That weakens auditability: canonical specification validation must evaluate the checked-out candidate rather than arbitrary host files reachable through repository symlinks.

## Implementation

`scripts/validate_spec.py` now makes `included_in_repository_scan()` enforce two boundaries:

1. lexical containment under the supplied repository root plus the existing ignored-root policy;
2. physical/real-path containment after `Path.resolve()`.

The helper fails closed when:

- the candidate is not lexically below the repository root;
- the resolved target leaves the resolved repository root;
- real-path resolution raises an `OSError`, `RuntimeError`, or containment `ValueError`.

An in-repository symlink whose resolved target stays inside the repository remains eligible. This is deliberate: issue #92 required a clear policy rather than accidentally banning every repository-local alias. The invariant implemented here is containment, not a blanket no-symlink policy.

No Markdown parsing, Alpha/Beta normative content, ignored-root names, link-destination semantics from PR #91, product runtime, UI, Storage, WAL, Research, networking, packaging or Quality workflow is changed.

## Focused tests

`tests/unit/test_validate_spec_links.py` retains the four PR #91 link-boundary cases and adds three scan-boundary cases:

- a lexically external path is rejected;
- an in-repository symlink resolving outside the root is rejected;
- an in-repository symlink resolving to another in-repository file is accepted.

Symlink cases skip only when the host cannot create symlinks.

The fixture now loads `validate_spec.py` once per module and exposes both boundary helpers from that exact namespace.

No local full-repository PASS is fabricated. Canonical GitHub Quality on the exact published follow-up head is the integration authority.

## Ownership and collision avoidance

This follow-up intentionally depends on PR #91 because it touches the same validator/test surface. It does not compete with PR #91 as an independent Develop-targeted implementation.

Owned delta beyond the PR #91 head is exactly:

- `scripts/validate_spec.py`
- `tests/unit/test_validate_spec_links.py`
- `docs/agent_handoffs/manual-integrator-spec-scan-boundary-20260911.md`

Active worker ownership remains excluded:

- Backend/System product and Storage/WAL work: untouched;
- Errors verification/ledger work: untouched;
- Spec/Core product semantics and Search composition: untouched;
- UI/Desktop/visual work: untouched;
- Windows packaging/runtime-boundary candidates: untouched;
- `.github/workflows/quality.yml`: untouched;
- `develop/pathena-next`: untouched directly;
- `main`: untouched.

## Integration rule

Treat this as a stacked candidate:

1. PR #91 must remain independently reviewable and must not be amended with this work.
2. Validate this follow-up on its exact head.
3. Before consumption, refresh current Develop and worker ownership.
4. Integrate the parent link-boundary behavior and this scan-boundary behavior in dependency order, or recreate the combined bounded diff on then-current Develop and obtain fresh exact-SHA evidence.
5. Do not reuse the parent green run as proof for this new head.
6. Do not auto-merge either PR.

## Issue #92 closure criterion

Issue #92 can be closed only after the scan-containment behavior is present on the intended integration branch and exact-head canonical validation is green. A green stacked PR alone is candidate evidence, not proof of Develop integration.
