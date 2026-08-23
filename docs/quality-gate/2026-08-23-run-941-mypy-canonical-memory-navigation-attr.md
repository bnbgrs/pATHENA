# Quality Gate Incident: undeclared KnowledgeWorkspace navigation attribute

Date: 2026-08-23

## Failing gate

GitHub Actions run `32631752029` (run number `941`), job `97175503119`, passed the specification validator and Ruff, then failed in mypy.

The relevant diagnostic was:

```text
src/athena/desktop/canonical_memory_extensions.py:586: error:
"KnowledgeWorkspace" has no attribute "navigation"  [attr-defined]
        self.workspace.navigation = getattr(self.workspace, "navigation", None)
        ^~~~~~~~~~~~~~~~~~~~~~~~~
```

The same line was confirmed on the current `agent/pathena` head before the fix.

## Root cause

`_focus_filter()` contained a self-assignment that attempted to create or preserve a dynamic `navigation` attribute on `KnowledgeWorkspace`. `KnowledgeWorkspace` does not declare that attribute, and the assignment has no effect on the actual Ctrl+F behavior: the method immediately focuses and selects the existing search input.

This was an accidental leftover/no-op, not a required navigation contract.

## Fix

Commit `8da48a62d9fe0f9aefb4a5114bc6a98d8f797eae` removes only the invalid self-assignment. `_focus_filter()` still focuses `workspace.search_input` with `ShortcutFocusReason` and selects its text exactly as before.

No new attribute, cast, ignore, or mypy suppression was introduced.

## Verification plan

Re-run mypy through the quality gate. The `KnowledgeWorkspace.navigation` `attr-defined` error must disappear while Ctrl+F filter focus behavior remains unchanged.
