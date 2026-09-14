# Knowledge Inspection application wiring post-#158 handoff

## Status

`REQUALIFICATION_CANDIDATE`

## Exact base

- target: `develop/pathena-next`
- base: `a2dfc6b381ead94996f319ca06fc65e25992fb70`
- base meaning: merged PALLAS Living Foundation PR #158

## Carried functional evidence

This reconstruction carries the exact already-qualified product and regression blobs from PR #156 head `fd827b71a1afabedb66263ce6f5b6c966c3169e8`:

- `src/athena/core/application.py`: `9a5ac98371265da72f2bb57f29ce346651f1e2dc`
- `tests/unit/test_knowledge_application_inspection.py`: `19b0ae9acdc9b307cade12ad2adc9e920f7d7ed4`

The pre-change `application.py` blob on both the old qualified base and this exact new base is `a0c4a947ce94cb716475582f6ff0066e689a680c`. Therefore the product delta is reconstructed without overwriting unrelated application changes.

## Product contract

`AthenaApplication` builds the canonical Knowledge Inspection API from the already canonical `ClaimService` and `ReviewService`, using `ChatService.ensure_local_user` as actor provider, and attaches it to `CoreApiFacade`.

The regression starts a real temporary SQLite-backed Core, writes a chat message, promotes that exact persisted message to a Claim, and verifies capability disclosure, list/detail/history access, actor identity, provenance input identity, and ORIGINATES evidence identity through the application API.

Keep the existing `ClaimReader` protocol boundary. Do not narrow the builder to concrete `ClaimService` merely to satisfy the application wiring.

## Prior exact-head evidence

PR #156 exact head passed both Core Focused Candidate and canonical Quality. That evidence is historical only; this post-#158 reconstruction requires fresh exact-head gates before integration.

The three localized `# type: ignore[import-untyped]` annotations in the regression remain scoped to the installed-package behavior of the focused runner. They do not weaken product typing or canonical mypy policy.

## Integration rule

Merge only after:

1. exact-head Core Focused Candidate succeeds;
2. exact-head canonical Quality succeeds;
3. post-#158 Develop is canonical-green;
4. a final Develop drift and changed-path collision check is clean.
