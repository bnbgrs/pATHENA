# Quality Gate Incident: knowledge CLI provenance/evidence loop type shadowing

Date: 2026-08-23

## Failing gate

GitHub Actions run `32631752029` (run number `941`), job `97175503119`, passed specification validation and Ruff, then failed in mypy.

The related diagnostics in `src/athena/desktop/knowledge_cli.py` were:

```text
:208: error: Incompatible types in assignment (expression has type "ClaimEvidenceRef", variable has type "ProvenanceInputRef")  [assignment]
:211: error: "ProvenanceInputRef" has no attribute "evidence_role"  [attr-defined]
:212: error: "ProvenanceInputRef" has no attribute "anchor_id"  [attr-defined]
:213: error: "ProvenanceInputRef" has no attribute "message_id"  [attr-defined]
:214: error: "ProvenanceInputRef" has no attribute "evidence_entity_id"  [attr-defined]
:215: error: "ProvenanceInputRef" has no attribute "evidence_revision_id"  [attr-defined]
```

## Root cause

Within `_print_claim_show()`, the local loop variable `item` was first bound while iterating provenance inputs (`ProvenanceInputRef`) and then reused while iterating evidence refs (`ClaimEvidenceRef`). Mypy keeps a single function-local variable type and therefore interpreted the second loop variable as the earlier provenance type, producing one assignment error followed by five invalid-attribute errors.

The underlying repository APIs and runtime objects were already correct.

## Fix

Commit `fe84f88d0d0a8ad52c2164b691b11dda1f20b9fe` gives each semantic role its own local name:

- `provenance_ref` for provenance input rows.
- `evidence_ref` for claim evidence rows.

Printed output, field order, CLI protocol, evidence semantics, and repository calls are unchanged. No cast, ignore, or suppression was introduced.

## Verification plan

Re-run mypy through the quality gate. All six diagnostics above must disappear. CLI output remains byte-for-byte equivalent apart from no user-visible change at all, because only local variable names changed.
