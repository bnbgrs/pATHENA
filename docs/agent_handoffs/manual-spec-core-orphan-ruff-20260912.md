# Spec/Core orphan-knowledge Ruff repair handoff — 2026-09-12

## Exact reproducer

- Worker: `postmerge/spec-core@1cef32d5f1479872d2f78cca29b2ed80fce05076`.
- Worker feature: `feat(core): support source-free user knowledge provenance`.
- Core Focused Candidate: `34680250793 = FAILURE`.
- Exact focused job: `103517491659`.
- Changed focused tests themselves passed: `tests/unit/test_orphan_knowledge.py` = `2 passed`.
- Ruff alone failed with `F841` at `tests/unit/test_orphan_knowledge.py:58`: local variable `actor_id` was assigned but never used.

The later diagnostic-remediation step also reported a dirty worktree, but that is a cascade after the Ruff failure because focused evidence had already been written. It is not treated as an independent product defect unless it reproduces after Ruff is green.

## Bounded repair

Isolated branch: `manual/spec-core-orphan-ruff-20260912`.

Product/test repair commit: `30d2497e55f4cd983efc22b3eaadce07885bd41f`.

The malformed-boundary test still calls `chat.ensure_local_user()` to preserve the original setup side effect, but no longer stores its return value in an unused local. No product file, assertion, exception expectation, database check, provenance rule, or test selection was changed.

## Why this form

Do not remove the `ensure_local_user()` call merely to satisfy lint: retaining it minimizes semantic change and preserves the exact setup performed by the failing worker candidate. The fix is therefore only an unused-binding removal, not a test weakening.

## Verification required

Before the worker consumes this repair, require on one unchanged exact candidate SHA:

1. Core Focused Candidate Ruff = SUCCESS;
2. changed focused pytest = SUCCESS;
3. canonical Specification Validator = SUCCESS;
4. canonical Ruff = SUCCESS;
5. canonical mypy = SUCCESS;
6. canonical full pytest = SUCCESS;
7. Windows path safety, Linux storage regressions, and Local install smoke remain green.

If `postmerge/spec-core` advances first, compare `tests/unit/test_orphan_knowledge.py`. If the worker has independently removed the unused binding and its exact gates are green, close the manual PR as provenance instead of merging it twice.

## Coordination

- Do not mutate `postmerge/spec-core` directly from this manual branch.
- Do not touch Develop, Backend, UI, Errors, `main`, or `bnbgrs/ATHENA` from this repair.
- Do not add `# noqa: F841`, Skip/XFail, assertion weakening, or Ruff configuration exceptions.
- Errors bot may assign the next stable ERR id if this exact-head blocker needs ledger tracking; this handoff deliberately does not invent an ID.
