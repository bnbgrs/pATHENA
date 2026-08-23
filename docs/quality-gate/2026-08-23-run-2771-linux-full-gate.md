# Quality incident: run #2771 Linux full gate

- **Repository / branch:** `bnbgrs/pATHENA` / `agent/pathena`
- **Run:** #2771 (`32665417827`)
- **Job:** Python 3.12 quality (`97258361719`)
- **CI checkout:** PR merge `7c4c8b718ddca7f916ec5f9a954b6fe6526d7d96`, branch head `a683577c5e69b85308588b0b6b7b1675faae91ee`
- **First observed:** 2026-08-23
- **Status:** OPEN; primary failures split by ownership below

## Executed gate result

- Specification validator: **PASS — 63/63**
- Ruff: **FAIL — 14 diagnostics**
- mypy: **FAIL — 25 errors in 16 files**
- pytest: **FAIL — native SIGSEGV / exit -11 at about 65% of 3941 collected tests**
- Keep-going behavior: **PASS**; mypy and pytest ran after Ruff failed.

## Primary failure A — productive extraction wiring

**Ownership:** BACKEND

Both executed runtime smoke and mypy independently identify the same productive application-composition defect:

```text
src/athena/core/application.py:538: error: Missing named argument "chat" for
"ChatKnowledgeExtractionService"  [call-arg]
```

`ChatKnowledgeExtractionService.__init__()` requires keyword-only `chat: ChatService`, but the run's `AthenaApplication` construction omitted `chat=self.chat`. The independent Local install smoke job failed with the corresponding runtime `TypeError` before Core startup.

Detailed log: `docs/quality-gate/2026-08-23-run-2771-local-smoke-extraction-chat-integration.md`.

The large set of integration/system pytest failures before the native crash must not be counted as independent root causes until retested after this application-construction defect is fixed: many tests instantiate or transitively start `AthenaApplication`/Core services and are therefore plausible secondary failures.

## Primary failure B — native PALLAS/Qt crash

**Ownership:** UI

pytest again terminated the interpreter with SIGSEGV / exit `-11` while constructing the pATHENA command-palette presentation test:

```text
src/athena/desktop/ascii_panel.py:253 in _bind_pallas_target
src/athena/desktop/ascii_panel.py:166 in set_context
src/athena/desktop/window.py:2660 in _select_page
src/athena/desktop/pathena_window.py:566 in _select_page
tests/unit/test_pathena_command_palette_presentation.py:16
```

This independently reconfirms `QG-2677-UI-PALLAS-SEGFAULT`; it prevents normal full-suite completion and therefore still blocks full timeout-headroom measurement.

## Ruff ownership split

The run reported 14 Ruff diagnostics.

**UI-owned:** import-order diagnostics across current `src/athena/desktop/pathena_*` modules; B009 in `pathena_enablement_rationale_5700.py`; unused `QListWidget` in `pathena_research_proposal_density.py`; unused local in `tests/unit/test_pathena_offline_comprehension.py`.

**Quality-owned:** one I001 in `tests/unit/test_quality_workflow_contract.py`. Quality subsequently corrected the import-to-module spacing in commit `008647cf4e20617c70ff8f9918b3d53632c99b62` without touching UI files.

## mypy ownership split

**Backend-owned errors include:**

- `research/models.py`: 2
- `model/registry.py`: 3
- `storage/migration_recovery.py`: 1
- `research/idempotency.py`: 3
- `retrieval/semantic.py`: 2
- `chat/grounded_context_package.py`: 1
- `core/application.py`: 1 new missing-`chat` composition error

**UI-owned errors include:** `pathena_state_transition_integrity_4600.py`, `pathena_selection_loading_5400.py`, `pathena_result_scope_clarity.py`, `pathena_message_action_tab_order.py`, `pathena_detail_provenance_6300.py`, `pathena_backup_action_context_6800.py`, `pathena_accessible_state_sync_5600.py`, `pathena_research_proposal_density.py`, and `pathena_command_palette_truth_6500.py`.

Quality does not patch those product scopes.

## Independent jobs on the same CI head

These results are valuable because they are not masked by the UI crash:

- Linux focused storage regressions: **PASS — 157 tests**
- Linux API runtime path-boundary regressions: **PASS — 12 tests**
- Native Windows locality probe: **PASS**
- Windows locality selection: **PASS — 5 tests, 3 deselected**
- Windows storage regressions: **PASS — 109 tests**
- Windows API runtime path-boundary regressions: **PASS — 12 tests**
- Local install smoke: **FAIL** due primary failure A above

Both Linux and Windows locality tests emitted two non-fatal Python `SyntaxWarning`s for invalid escape `\(` in regex strings at `tests/unit/test_storage_locality.py:53,74`; tracked separately as `QG-STORAGE-LOCALITY-REGEX-WARNINGS`.

## Verification / mitigation status

- Quality-owned Ruff I001: **FIXED in Quality scope**, executed rerun pending.
- Backend application wiring: **OPEN / BLOCKED on Backend owner**; current branch was re-read after the run and still omitted the required `chat` dependency at the time this log was created.
- UI native crash: **OPEN / BLOCKED on UI owner**, independently reproduced again.
- Full pytest completion: **NOT ACHIEVED** because of SIGSEGV.
- 10-minute full-gate headroom: **NOT VERIFIABLE** until pytest reaches ordinary completion.

## Next verification

1. Re-read current head for Backend/UI fixes before any action.
2. After application wiring fix, rerun targeted application/extraction construction and Local install smoke; then classify the broad pytest failures that remain.
3. After UI crash fix, require the full pytest process to exit normally before closing the native-crash slice or measuring timeout headroom.
4. Recheck Ruff on the Quality workflow-contract test after commit `008647cf...`.
