# Quality Gate Incident: canonical-memory merge target type shadowing

Date: 2026-08-23

## Failing gate

GitHub Actions run `32631752029` (run number `941`), job `97175503119`, passed specification validation and Ruff, then failed in mypy.

The related diagnostics in `src/athena/desktop/canonical_memory_cli.py` were:

```text
:90: error: Incompatible types in assignment (expression has type "ClaimSnapshot", variable has type "KnowledgeUnitSnapshot")  [assignment]
:93: error: "KnowledgeUnitDraft" has no attribute "claim_kind"  [attr-defined]
:96: error: "KnowledgeUnitDraft" has no attribute "statement"  [attr-defined]
```

The same variable reuse was confirmed on the newer `agent/pathena` head. A first write attempt was safely rejected with HTTP 409 because the file had changed concurrently; the fix was then rebased manually onto the new blob so the parallel claim-relation changes were preserved.

## Root cause

`_print_merge_target()` used `snapshot` and `payload` for both branches of a discriminated merge-target flow. The knowledge branch binds them to `KnowledgeUnitSnapshot` / its knowledge payload and returns. The claim branch then reused the same function-local names for `ClaimSnapshot` / its claim payload. Mypy keeps function-local variable types consistent and therefore interpreted the claim values as the earlier knowledge types.

Runtime branch semantics were correct; the local names erased the static distinction.

## Fix

Commit `4d1f9bda0ac124e50aa2dde8f164cf8669d0470d` uses distinct names:

- `knowledge_snapshot` / `knowledge_payload`
- `claim_snapshot` / `claim_payload`

The concurrent changes that prioritize message/anchor provenance in `_claim_relation_row()` were retained unchanged.

No CLI output, repository call, branch condition, merge-review semantics, cast, ignore, or suppression changed.

## Verification plan

Re-run the quality gate. The three diagnostics above must disappear. Together with the other run-941 fixes, mypy should advance beyond all twelve errors originally reported by that run.
