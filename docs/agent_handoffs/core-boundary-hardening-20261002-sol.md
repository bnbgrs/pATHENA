# Core boundary hardening candidate — 2026-10-02

## Baseline

- Repository: `bnbgrs/pATHENA`
- Integration target: `develop/pathena-next`
- Exact base: `467ef434236c320e4afe9d21a39c20a4a2b75728`
- Branch: `candidate/core-boundary-hardening-20261002-sol`
- This candidate intentionally consolidates the disjoint product/test work first developed in draft PRs #346, #349, #354, #356 and #365.
- Chat actor atomicity PR #338 is intentionally excluded because active Chat branching PR #342 now shares its repository/service files.

## Ausgangslage

Five independent runtime-boundary defects remained in files not owned by the active Chat, Jobs, Sources, Backup, Knowledge, Settings, Windows, PALLAS or LM-Studio-Desktop bots:

1. stable model identities admitted leading/trailing whitespace;
2. LM Studio accepted noncanonical discovery/request/runtime instance identities;
3. Protected-Content repository reads coerced persisted crypto fields instead of validating BLOB type/length;
4. Personal Memory runtime domain values relied on annotations and accepted invalid enum/scalar types;
5. external-access security grants coerced malformed persisted authorization state instead of failing closed.

The original slices were based on `67174198...`. Develop then advanced by the integrated Chat-cancellation stack to `467ef434...`. Since canonical Quality checks the branch head rather than a synthetic PR merge commit, these five disjoint slices were reapplied onto fresh Develop as one bounded candidate for current-base qualification.

## Änderungen

### Model domain identity

- `ModelInfo.provider` and `backend_model_id` require canonical non-empty trimmed text.
- Optional model revision continues to use canonical-text validation.
- Direct boundary tests cover padded provider/backend IDs.

Files:
- `src/athena/model/domain.py`
- `tests/unit/test_model_domain_boundaries.py`

### LM Studio identity boundaries

- discovery `key` must be canonical;
- `stream_chat`, `generate_structured`, and `generate_controlled_structured` reject padded/blank model IDs before transport;
- controlled structured runtime `model_instance_id` is no longer silently trimmed before cache/reuse;
- focused regressions cover discovery, request and runtime identities.

Files:
- `src/athena/model/adapters/lm_studio.py`
- `tests/unit/test_model_provider.py`

### Protected-Content persisted BLOB integrity

- Scope-Key IDs/nonces/wrapped keys are validated as persisted BLOBs with exact expected lengths;
- Protected-Payload IDs/ciphertext/nonces/wrapped DEK/hash receive the same fail-closed validation;
- regressions mutate valid SQLite rows to same-length TEXT values that can satisfy SQLite `length(...)` checks but must not escape as Python conversion errors.

Files:
- `src/athena/security/repository.py`
- `tests/unit/test_security_repository_blob_boundaries.py`

### Personal Memory runtime domain boundaries

- Memory enum fields require their actual enum types;
- content must be text;
- scoped entity identity must be UUID-or-None;
- confidence rejects bool, nonnumeric and non-finite values before range checks;
- confirmation timestamp requires exact int-or-None, excluding bool;
- existing scope and explicit-user confidence semantics remain intact.

Files:
- `src/athena/memory/models.py`
- `tests/unit/test_memory_domain_boundaries.py`

### External/TOR persisted authorization integrity

- authorization and actor IDs require exact 16-byte BLOBs;
- persisted purpose/host scope/route/origin/timestamps are validated before constructing a security grant;
- persisted host scope must parse as non-empty safe canonical host strings;
- expiry/revocation invariants are rechecked at the runtime read boundary;
- regressions cover a same-length TEXT actor identity, noncanonical stored host scope and valid-record preservation.

Files:
- `src/athena/external/gateway.py`
- `tests/unit/test_external_authorization_persistence_boundaries.py`

## Verhalten danach

Malformed identity/security/domain state is rejected at the boundary where it enters runtime logic. The candidate does not add features, UI, new services or new persistence schemas; it tightens existing invariants and preserves valid behavior.

## Validierung

Repository-level validation already performed before opening the candidate PR:

- fresh base confirmed: `467ef434236c320e4afe9d21a39c20a4a2b75728`;
- candidate comparison: ahead 10 before this handoff, behind 0;
- changed-file set re-read and limited to the intended ten product/test files;
- old-to-new Develop diff was inspected and does not modify these files.

Local checkout/test execution remains unavailable in this assistant runtime because `github.com` DNS resolution fails. No local pytest, Desktop or native Windows PASS is claimed.

Required authoritative validation after PR creation:

1. specification validator;
2. Ruff;
3. mypy;
4. full pytest;
5. Windows path-safety lane;
6. Linux storage regressions;
7. Local install smoke.

Any exact-head failure attributable to this candidate must be fixed here. Baseline/harness failures must be identified as such rather than bypassed.

## Konfliktrisiko / Parallelität

- Active LM Studio runtime work owns Desktop runtime files, not the provider adapter changed here.
- Active Chat work owns Chat/API/Desktop files and is not included here.
- Active Storage/Backup/Jobs/Sources/Knowledge/Windows/PALLAS/Settings/Observability work does not overlap this candidate's changed files at creation time.
- If Develop advances again before integration, compare its new file set against this candidate before merge; do not force-push or overwrite bot work.

## Superseded draft PRs

Once this current-base candidate PR exists, the following old-base drafts should be considered superseded and closed with pointers here:

- #346 — LM Studio identity boundaries
- #349 — generic ModelInfo canonical identity
- #354 — Protected-Content persisted BLOB integrity
- #356 — Personal Memory domain boundaries
- #365 — External authorization persistence boundaries

Their discussions remain useful historical/root-cause evidence, but they should not be independently integrated.

## Nächste sinnvolle Schritte

1. Qualify this exact candidate head in canonical Quality.
2. Fix only candidate-attributable failures.
3. Re-synchronize against latest Develop before integration.
4. If exact-head green and no overlap has appeared, integrate this candidate as one bounded hardening package.
5. Run fresh canonical Develop Quality after integration.
6. Keep #338 separate until #342 Chat branching settles, then reapply/requalify atomic actor identity on the resulting Chat files.
