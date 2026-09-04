# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@5d7061678afd2e2f6195d5a3ce6e15cde2797007`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `edec1568cf60d9708bcbb05beb5338b82c7e0ee1`, with parents `482dc5a376c288979d30d9c63132582ae951a254` and current Develop `5d7061678afd2e2f6195d5a3ce6e15cde2797007`.

## Verified slice — Exhaustive Research coverage accounting

Spec source: `docs/beta/11_Exhaustive_Research.md` plus the integrated Alpha/Beta progress contract.

Canonical policy files:
- `src/athena/research/coverage.py`
- `tests/unit/test_research_coverage.py`

Exact worker Quality run `33839840564` completed `success` on `482dc5a376c288979d30d9c63132582ae951a254`. Develop independently records the integrated coverage slice as `VERIFIED`.

Contract retained:
- eligible = candidate_total - excluded_count;
- processed = successful + irrelevant + failed + unavailable;
- only successful + explicitly irrelevant work contributes to coverage;
- failed/unavailable work remains terminal and visible but cannot inflate coverage;
- zero eligible work does not synthesize 100% coverage;
- invalid, bool, negative, or impossible counter combinations fail closed.

## Current Core gap — durable ResearchScope / ResearchResult composition

`ResearchRepository._recompute_scope_counters()` still manually duplicates the same processed/coverage arithmetic before persisting `research_scopes`. `finalize_result_fenced()` calls that recomputation and then copies the persisted counters into the durable `ResearchResult`, so this single bounded composition point governs both Scope and Result truthfulness.

The required product mutation is now versioned exactly in:

`docs/agent_handoffs/spec-core-research-coverage-composition.patch`

The patch is based on the current repository blob `src/athena/research/repository.py@dde58860ae0008b8d24cb0a868fb9420faeef405` and does only the following:

1. imports the verified pure coverage policy as `CoverageAccounting`;
2. removes the duplicate SQL/manual processed/ratio arithmetic;
3. derives persisted `processed_count` and `coverage_ratio` from `CoverageAccounting` using the same real SQL counters;
4. adds a focused SQLite acceptance test proving the durable recomputation invokes the canonical policy and persists failed/unavailable work as processed without counting it as coverage.

No schema, transaction, snapshot, recovery, fence, state-transition, source/provider, security, provenance, PALLAS, or UI semantics are changed.

## Write-path blocker and mandatory next action

The available GitHub contents mutation action can replace an existing file only by sending its complete UTF-8 contents. `repository.py` is a large central persistence file. Local checkout/download is currently unavailable because the execution environment cannot resolve `github.com`. Reconstructing the large file from partial ranges would violate the Core safety rule and risk overwriting unrelated worker changes.

This blocker is therefore recorded only for this run. It must not be repeated unchanged. The next Core run must use a safe alternative that applies the versioned patch against the exact `dde58860...` base (for example a restored checkout/download path or another patch-capable mutation route), or, if that exact base has moved, regenerate/review the patch against the new complete blob before mutation. Once applied, run `tests/unit/test_research_coverage.py`, the new persistence-focused test, smallest Research repository/result regressions, then canonical Quality.

## Ownership / collision avoidance

- Backend owns Research runtime/source-types/input-boundary hardening; Core does not modify those paths.
- UI owns styling/Desktop/UI slices; no UI files are touched.
- Error worker owns independent defect ledger/recovery validation; no new ERR root cause is asserted here.
- Integrator must not integrate the composition patch as product code until it has actually been applied to `postmerge/spec-core` and verified.

## Integrator handoff

The pure Research coverage policy itself is `VERIFIED` and already integrated on Develop. The new durable Scope/Result composition is `PATCH_READY_BLOCKED_ON_SAFE_EXISTING_FILE_MUTATION`, not product-ready. Do not infer implementation from the patch file.

## Next Alpha/Beta gap

Priority remains applying `spec-core-research-coverage-composition.patch` safely, committing the bounded product/test slice, and verifying it. After green verification, immediately select the next highest unclaimed P0/P1/P2 CHAT/KNOWLEDGE/RESEARCH/PALLAS composition gap from current Alpha/Beta evidence.
