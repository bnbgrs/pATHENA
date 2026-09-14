# Core Knowledge Inspection Application Wiring — 2026-09-14

## Purpose

Wire the already-implemented canonical Claim inspection boundary into the real `AthenaApplication` on exact current Develop base `90f5439bfdb4502bc689c51b06f83586c50c9d7c`.

This is deliberately stronger than the stale Spec/Core worker proposal: it preserves the existing real `ClaimService` composition contract and adds an application-level test through actual SQLite-backed chat, Claim creation, provenance, evidence, and `CoreApiFacade` inspection.

## Product wiring

`AthenaApplication` now:

- builds `KnowledgeInspectionApiService` from the canonical `ClaimService` and `ReviewService` instances;
- uses `ChatService.ensure_local_user` as the single local decision-actor provider;
- attaches the inspection service exactly once to `CoreApiFacade`.

No repository boundary is exposed to API clients and no duplicate Claim or Review service is created.

## Real composition regression

`tests/unit/test_core_application_knowledge_inspection.py` starts a real temporary Core with startup maintenance disabled, then:

1. creates a real local chat and user message;
2. promotes that exact persisted message to a canonical factual Claim through `ClaimService`;
3. verifies the API advertises Claim inspection and contradiction-review capabilities;
4. reads the Claim through `CoreApiFacade.list_claims()` and `load_claim()`;
5. checks exact revision/actor identity;
6. verifies the persisted provenance input points to the source message revision;
7. verifies ORIGINATES evidence points to the same persisted message;
8. verifies Claim history through the Core API.

This proves the application path rather than a mock boundary.

## Rejected weaker worker delta

Do not replace `tests/unit/test_core_knowledge_inspection_composition.py` with a mock-only test from the stale `postmerge/spec-core` lineage. The current Develop test deliberately exercises the real `ClaimService.list()` method contract and is stronger.

Likewise, do not broaden the builder parameter from the structural `ClaimReader` protocol unless an actual typing failure requires it. `ClaimService` already satisfies that protocol.

## Integration rule

Require exact-head Core Focused and canonical Quality. Preserve current Develop test strength. No Skip/XFail, no API repository leakage, no actor duplication, no type-contract weakening, no auto-merge.
