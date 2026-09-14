# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Develop checked first: `develop/pathena-next@b2063a274984448d5f0db5d1c917c7ee93ae80be`.
- Worker before this run: `postmerge/spec-core@1d1334d82af52f8055d7da06b2afa3db575eac4b`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Worker `1d1334d82af52f8055d7da06b2afa3db575eac4b` has exact-SHA Core Focused `34861762468 = SUCCESS` and canonical Quality `34861762425 = SUCCESS`.
- Current Develop adds only the integrated PR-only Quality concurrency fix over the prior Develop baseline; the verified Knowledge-read worker changes are still not represented in Develop.

## Current Core slice — canonical Knowledge-read build+attach composition

The existing `build_knowledge_read_api()` already composes truthful provenance explanation and immutable revision history over one canonical Knowledge reader. `CoreApiFacade` already provides strict `attach_knowledge_read()` semantics from the prior verified slice. This run closes the remaining composition seam between those two established boundaries without adding a parallel reader, repository, cache, provenance representation, storage path or transport layer.

Product change in `src/athena/api/knowledge_read_composition.py`:

- add a minimal `KnowledgeReadFacade` protocol exposing only `attach_knowledge_read()`;
- add `attach_knowledge_read_api()` which builds exactly one `KnowledgeReadApiService`, attaches that exact instance to the supplied facade, and returns the same instance;
- preserve the existing canonical Knowledge source for both Why-known and revision-history projections;
- preserve facade-owned single-attach/fail-closed semantics rather than duplicating them in the composition helper.

Focused acceptance in `tests/unit/test_knowledge_read_composition.py` now additionally proves:

- the helper returns the exact service instance attached to the facade;
- reads still route through the same canonical source;
- a second attach fails and does not replace the originally attached service;
- malformed Knowledge identity remains fail-closed before source access.

## History-preserving baseline integration

The candidate tree is built from current Develop so its CI-concurrency fix is retained, while all verified worker Knowledge-read files are overlaid unchanged except for the composition/test changes above. The commit has both prior worker and current Develop as parents. No force-push, rebase or history rewrite is used.

## Ownership / collision avoidance

- Backend retains deep Storage/transaction/recovery/backup ownership.
- UI retains Qt/PALLAS presentation and styling ownership.
- Protected Search remains authorization-first and is not approximated through normal Search.
- Persistent release guards remain binding: pypdf/Frozen argv/two-EXE, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures.
- No Skip/XFail or guard relaxation.

## Next distinct Core gap

After exact qualification and integration, wire `attach_knowledge_read_api(facade=self.api, knowledge=self.knowledge)` into `AthenaApplication`, retain the exact returned service instance, and add application acceptance proving exact-instance identity plus repository-backed Why-known/revision-history behavior. If central application mutation is unsafe with the available mutation interface, select another independent current Alpha/Beta Core gap rather than publishing a sync-only or docs-only follow-up.
