# Principal Engineering Run Handoff — 2026-10-02

## Baseline

- Repository: `bnbgrs/pATHENA`
- Integration target: `develop/pathena-next`
- Exact base used for all code branches: `67174198e1494fd4c8678aad60756c39ef5c160b`
- `main` was not modified.
- Parallel bot work was inspected before each slice and repeatedly re-synchronized during the run.
- Local clone/test execution is unavailable in this execution environment because `github.com` DNS resolution fails (`Could not resolve host: github.com`). No local PASS is claimed anywhere below.
- GitHub CI is therefore the executable validation source.

## Ausgangslage

The active bot set already owned Chat cancellation/composer state, LM Studio Desktop lifecycle, Settings/News recovery, Update manifests, Storage bundle work, Windows packaging/helpers, Sources, Knowledge, Jobs, Backup, Obsidian, PALLAS visual determinism, logging redaction, and later Chat branching.

This run deliberately avoided those active file sets and selected independent correctness boundaries. Five concrete defects were implemented as separate bounded draft PRs so bots can integrate or rebase them independently.

---

## Slice A — atomic persistent Chat actor identity

### Root Cause

`ChatService.ensure_local_user()` and `ensure_primary_model()` performed `find_active_actor()` and `create_actor()` as two separate operations. Two concurrent callers could both observe a missing actor before either insert committed, creating duplicate persistent identities and splitting later provenance across actor UUIDs.

`SQLiteDatabase.write_transaction()` already uses `BEGIN IMMEDIATE`; the missing piece was placing the lookup and conditional insert inside that single write transaction.

### Änderungen

- Added `ChatRepository.ensure_actor()`.
- Lookup + conditional actor insert now share one `BEGIN IMMEDIATE` transaction.
- Local-user and primary-model resolution route through that atomic repository boundary.
- Added regressions for actor reuse and for preventing service code from falling back to split lookup/create calls.

### Dateien

- `src/athena/chat/repository.py`
- `src/athena/chat/service.py`
- `tests/unit/test_chat_service.py`

### Verhalten danach

The first persistent local-user/model actor decision is serialized at the repository boundary. Repeated calls reuse the same active identity instead of depending on an unsafe read-before-write gap.

### Validierung

Draft PR: #338  
Branch: `fix/chat-actor-identity-race-20261002-sol`  
Head at handoff creation: `dd2b5de7cc0b363724c6e382edc58d691f63aad4`  
Quality run: `36937296240`

Observed on that exact head before this handoff was written:

- specification validator: PASS
- Ruff: PASS
- mypy: PASS
- Windows path safety: PASS
- Local install smoke: PASS
- Linux storage regressions: PASS
- full pytest step: still running; no final Quality PASS claimed

### Abhängigkeiten / Konfliktrisiko

After #338 was opened, parallel PR #342 (Chat immutable edits/forks) began modifying the same `chat/repository.py` and `chat/service.py` files. Its observed hunks are mostly in different methods, but the branches now share files.

Do not blindly merge or copy either branch over the other. Re-evaluate #338 against the final #342 state. Prefer rebasing/reapplying this small atomic-actor change after the larger branching slice settles if that avoids disrupting the active branching bot.

---

## Slice B — LM Studio model/runtime identity boundaries

### Root Cause

LM Studio model discovery accepted padded backend keys such as `" example/model-q4"`. Generation entry points accepted padded `model_id` values, and controlled structured generation silently trimmed a padded `model_instance_id` returned by LM Studio before caching it.

Those behaviors weaken stable identity semantics: discovery, registry lookup, runtime-instance reuse and persisted model provenance can refer to different strings for what appears to be the same model.

### Änderungen

- LM Studio discovery now requires the stable `key` to be canonical non-empty trimmed text.
- `stream_chat()`, `generate_structured()`, and `generate_controlled_structured()` reject noncanonical request model IDs.
- Controlled structured responses reject noncanonical runtime instance IDs rather than silently trimming and caching them.
- Added regressions for leading/trailing/whitespace-only discovery and request identities plus padded runtime instance IDs.

### Dateien

- `src/athena/model/adapters/lm_studio.py`
- `tests/unit/test_model_provider.py`

### Verhalten danach

LM Studio identity strings either cross the provider boundary exactly in canonical form or fail closed. ATHENA no longer silently normalizes one identity surface while leaving another untouched.

### Validierung

Draft PR: #346  
Branch: `fix/lmstudio-model-identity-boundaries-20261002-sol`  
Head: `0ffe7d6401840e51390f080d25d00738a1d4fef4`  
Latest Quality run observed: `36937798395` — queued at handoff creation; no PASS claimed.

### Abhängigkeiten / Konfliktrisiko

Active LM Studio Desktop-runtime work (#334) modifies `src/athena/desktop/lmstudio_runtime.py` and its Desktop tests, not this adapter file. The slices are complementary and file-disjoint.

---

## Slice C — canonical generic ModelInfo identities

### Root Cause

The generic `ModelInfo` domain rejected empty `provider` and `backend_model_id` values but accepted leading/trailing whitespace. `ModelRegistry` lookup boundaries already require canonical identifiers, so malformed provider output could enter the domain successfully and later become unaddressable or diverge from persisted identity strings.

### Änderungen

- Added a reusable required canonical-text domain validator.
- `ModelInfo.provider` and `ModelInfo.backend_model_id` now require canonical trimmed text.
- Optional canonical `model_revision` validation reuses the same helper without changing its semantics.
- Added direct domain tests for padded provider/model identities.

### Dateien

- `src/athena/model/domain.py`
- `tests/unit/test_model_domain_boundaries.py`

### Verhalten danach

All model providers inherit the stable provider/backend identity invariant, not only LM Studio.

### Validierung

Draft PR: #349  
Branch: `fix/model-domain-identity-contract-20261002-sol`  
Head: `710812b5ef2600458a7d7ddcaea95f14fe09c406`  
Quality run observed: `36937882529` — queued at handoff creation; no PASS claimed.

### Abhängigkeiten / Konfliktrisiko

No active parallel PR observed during this run modified either file. #349 is semantically complementary to #346. A sensible integration order is the generic domain invariant (#349) before the LM Studio-specific boundary (#346), followed by exact-head requalification of #346.

---

## Slice D — fail-closed Protected-Content persisted BLOB reads

### Root Cause

The Protected-Content repository type-checked password-slot cryptographic bytes, but Scope-Key and Protected-Payload readers used coercive `bytes(...)` conversion.

SQLite BLOB-affinity columns can hold TEXT values. A same-length TEXT nonce can satisfy `CHECK(length(nonce) = 12)` while still not being a BLOB. On read, this could escape as a raw `TypeError` instead of the repository's defined `ProtectionRepositoryIntegrityError`.

### Änderungen

- Added one small persisted-BLOB validator with exact/minimum length support.
- Scope-Key identity, scope identity, wrapping nonce and wrapped key now fail closed on wrong persisted type/length.
- Protected-Payload identities, ciphertext, nonce, wrapped DEK, DEK-wrap nonce and ciphertext hash now fail closed on wrong persisted type/length.
- Added database-level regressions that deliberately replace valid nonce BLOBs with same-length TEXT values that still satisfy SQLite length checks.

### Dateien

- `src/athena/security/repository.py`
- `tests/unit/test_security_repository_blob_boundaries.py`

### Verhalten danach

Persisted cryptographic state is validated before record construction. Malformed database types no longer leak generic Python conversion failures across the security boundary.

### Validierung

Draft PR: #354  
Branch: `fix/security-persisted-blob-types-20261002-sol`  
Head: `a7b0fa84ca8fd98551a2d704713fe3ba4c441755`  
Quality run observed: `36938120122` — queued at handoff creation; no PASS claimed.

### Abhängigkeiten / Konfliktrisiko

No active parallel PR observed during this run modified `src/athena/security/repository.py` or the new focused test file.

---

## Slice E — Personal Memory runtime domain boundaries

### Root Cause

`PersonalMemoryDraft` relied on type annotations at runtime. Several malformed values survived construction:

- strings in place of the Memory enums;
- non-text `content` (leading to later attribute errors);
- non-UUID scoped identities;
- `bool` confidence values (because `bool` is numeric in Python);
- NaN/Infinity confidence values (ordinary bound comparisons do not reject NaN);
- bool/float/string confirmation timestamps.

Those values could fail later in scope logic, JSON hashing or persistence instead of at the domain boundary.

### Änderungen

- Validate `MemoryKind`, `MemoryScopeKind`, `MemoryLearningMode`, and `MemorySensitivity`.
- Require text content and UUID-or-None scoped identity.
- Reject bool/non-numeric/non-finite confidence before the existing range and learning-mode rules.
- Require exact integer-or-None confirmation timestamps, excluding bool.
- Preserve valid text normalization and existing semantic scope constraints.
- Added focused runtime-boundary tests.

### Dateien

- `src/athena/memory/models.py`
- `tests/unit/test_memory_domain_boundaries.py`

### Verhalten danach

Malformed Memory payloads fail at construction with explicit domain errors instead of reaching hashing/repository code in an invalid state.

### Validierung

Draft PR: #356  
Branch: `fix/memory-domain-boundaries-20261002-sol`  
Head: `2318ba603aec1b8c13b75ffd5b12373a0b7f437b`  
Quality run observed: `36938281443` — queued at handoff creation; no PASS claimed.

### Abhängigkeiten / Konfliktrisiko

No active Memory PR was present at the latest synchronization before this slice.

---

## Cross-run validation and blockers

### Confirmed baseline facts

At repeated synchronization points, `develop/pathena-next` remained at:

`67174198e1494fd4c8678aad60756c39ef5c160b`

The post-Research merge Windows package workflow on that Develop SHA had already completed successfully before these slices began. Canonical Develop Quality still had a long pytest phase in progress during this run.

### Local execution blocker

A real local checkout was attempted. The environment failed on DNS resolution for `github.com`, so no local pytest, local Desktop launch or manual Qt interaction could be performed. This is an execution-environment blocker, not a product PASS/FAIL result.

No claim in this handoff substitutes source inspection for a runtime PASS.

### UI validation

This run did not change UI files. Active UI/visual bots continued running their own focused and 11-surface workflows. Because local checkout/start was blocked, this run did not claim manual Desktop validation.

---

## Known remaining problems / integration cautions

1. #338 must be requalified against the final #342 Chat branching head because those branches now share repository/service files.
2. All five code PRs are intentionally Draft until their exact current heads receive authoritative CI results.
3. The Quality queue is heavily loaded by many active bot heads. Superseded/cancelled workflow runs do not count as evidence for a newer head.
4. Native Windows acceptance remains necessary for end-to-end Desktop/LM Studio behavior; passing repository/unit gates is not equivalent to real installed-product acceptance.
5. Do not merge stale LM Studio PR #297 wholesale; active runtime work is now #334.
6. Do not resolve unrelated PALLAS/Jobs/Knowledge/Sources/Backup/Obsidian/UI failures from any branch above; those areas have active owners.

## Nächste sinnvolle Schritte

1. Read exact-head CI for #338, #346, #349, #354 and #356.
2. Fix only failures attributable to the corresponding slice; do not disable or bypass tests.
3. After #342 settles, rebase/reapply #338's small actor-identity change onto fresh Develop and rerun focused Chat tests + canonical Quality.
4. Prefer integrating the generic model invariant #349 before provider-specific #346, then rerun #346 against fresh Develop.
5. Integrate #354 and #356 independently once exact-head green and conflict-free.
6. After every Develop mutation, require fresh canonical Quality before treating the new integration base as green.
7. Continue selecting disjoint P0/P1/Alpha-Beta gaps; do not duplicate currently active bot work.
