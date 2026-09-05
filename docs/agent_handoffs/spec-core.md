# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@e25c483909881221aa1b42b868ce22993ec0f9b9`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization before this slice: `4be3b9bc52fb669756478be0031c2b8299ada533`, parents prior worker `bab57ac560c3d0fd43f2beb7501b3d4160a09064` plus exact Develop `e25c483909881221aa1b42b868ce22993ec0f9b9`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Previously READY / integrated

Normal Hybrid Search facade/application composition, production contradiction acceptance, fenced Research source coverage, Scoped Project Research, Historical Backfill enqueue/durable validation/candidate freeze/persisted-source boundaries, and truthful Local+Web enqueue/durable authorization scope are already verified and integrated on Develop.

Truthful Local+Web enqueue evidence remains product/test `6c5431f35951b7916e1db97138306de41a5da622`, exact green descendant `eaa43526398c2e5abb6efb2ec2ae58c53178e878`, focused `33986943543 = success`, canonical Quality `33987002816 = success`.

## IMPLEMENTED / focused green — Local+Web candidate freeze union

Exact product/test commit: `31a52e034c154759a2ccce2eebc77a2f2d961f37`.
Focused execution: `33992910995 = success` with `12 passed`, Ruff PASS, mypy PASS.

Implemented contract:

- `ResearchRepository.freeze_local_candidates()` admits `ResearchMode.LOCAL_PLUS_WEB` only with a canonical persisted Internet scope.
- The scope must contain canonical UUID `authorization_id` plus sorted/unique canonical `captured_source_ids`.
- Durable `external_source_captures` linkage for that authorization must exactly equal the requested captured Source set; mismatch or absence fails closed with `ResearchSnapshotError`.
- Existing `_select_sources_as_of()` remains the authoritative pinned-snapshot/time/source-type visibility selector.
- The local portion excludes every Source having any durable external-capture linkage.
- Only external Sources linked to this exact authorization may re-enter the candidate union, and existing explicit-source snapshot checks require them to be visible at the pinned snapshot.
- Another authorization's historical external capture and Sources persisted after Research initialization are excluded.
- Local Exhaustive and Historical Backfill semantics remain unchanged; project/domain/Protected/Archive scope remains fail-closed.
- No external transport occurs during freeze; only already captured durable Sources are composed.
- No synthetic Source/Claim/Evidence/Provenance/PALLAS data is introduced.

Real persistence acceptance uses `AthenaApplication`, real local Source capture, real explicit ExternalAccess authorization and real `capture_url()` persistence through `external_source_captures`, with a deterministic in-process transport only replacing network I/O. It proves the pinned union and mismatched authorization linkage failure.

## Verification state

- First executable attempt `33992843065`: product/acceptance application PASS; `12 passed`; Ruff PASS; mypy found one concrete list-vs-tuple assignment error. Fixed without weakening behavior.
- Second attempt `33992880709`: `12 passed`; Ruff PASS; mypy PASS; commit step stopped only on an EOF whitespace `git diff --check` finding. Fixed without changing assertions or product semantics.
- Final focused run `33992910995`: SUCCESS; `12 passed`; Ruff PASS; mypy PASS; product/test committed at `31a52e034c154759a2ccce2eebc77a2f2d961f37`.
- Automatic canonical Quality `33992936522` for the Actions-authored product commit was `action_required` with no usable verification. This is not a PASS.
- This documentation-only user-authored descendant exists specifically to trigger canonical Quality through the open worker PR. Do not mark this slice READY until that exact descendant obtains a successful canonical Quality run.

## Runtime / crash invariants retained

This slice does not change packaging metadata/dependencies, frozen entrypoints/argv routing, Desktop/Worker process topology, DirectChat context-budgeting or safety margin, migrations/storage bootstrap, scheduler process policy, or Windows publication. The known pypdf packaging, bounded worker tree, fail-closed unknown argv, 2048-context DirectChat regression guard, and storage-startup prevention invariants remain untouched.

## Collision avoidance

- Required Error/Backend/UI/Integrator handoffs were reviewed before mutation.
- Error reports no active Core blocker; Backend and UI active scopes are disjoint from this Research repository/test slice.
- Current Develop integration/handoff changes were preserved by the two-parent NON-FORCE synchronization.
- Only `postmerge/spec-core` was mutated; no force push or history rewrite occurred.

## Integrator handoff

`NOT_READY` for the candidate-freeze union until canonical Quality succeeds on the exact current documentation descendant carrying product/test ancestor `31a52e034c154759a2ccce2eebc77a2f2d961f37`.

Once canonical Quality is green, update this handoff with the exact green SHA/run and hand the bounded candidate-freeze slice to Integrator. Do not transplant any temporary applicator workflow/script; they were deleted before the product/test commit.

## Next Alpha/Beta gap

First consume the exact canonical Quality result for this descendant. If green, close and hand off Local+Web candidate freeze, then select the highest current unclaimed bounded Alpha/Beta Core gap from current Develop/spec coverage without broadening Protected/Archive/Internet semantics. If red, fix only the smallest exact root cause while preserving authorization linkage, pinned-snapshot visibility, provenance and fail-closed scope behavior.
