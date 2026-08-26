# Quality incident: run #2771 local smoke extraction wiring failure

- **Repository / branch:** `bnbgrs/pATHENA` / `agent/pathena`
- **Run:** #2771 (`32665417827`)
- **Job:** Local install smoke (`97258361925`)
- **Step:** Run disposable Core/API restart smoke
- **CI checkout:** PR merge `7c4c8b718ddca7f916ec5f9a954b6fe6526d7d96`, branch head `a683577c5e69b85308588b0b6b7b1675faae91ee`
- **First observed:** 2026-08-23
- **Ownership:** BACKEND product integration; Quality owns only diagnosis/gate coverage
- **Status:** OPEN / BLOCKED on Backend owner

## Reproduction

GitHub Actions executes:

```text
uv run --locked --extra dev athena-local-smoke --restart-cycles 1
```

The package builds and installs, then Core construction fails before the smoke can create its first process:

```text
TypeError: ChatKnowledgeExtractionService.__init__() missing 1 required keyword-only argument: 'chat'
```

Call path from the executed job:

```text
athena-local-smoke
  -> run_local_smoke()
  -> CoreApiProcess(settings=settings)
  -> AthenaApplication(settings=settings)
  -> ChatKnowledgeExtractionService(...)
```

## Root cause

`ChatKnowledgeExtractionService.__init__()` requires keyword-only `chat: ChatService` in addition to `chat_generation`, `provider`, `runs`, and optional `snapshots`.

At the failing branch head, `AthenaApplication` constructs the service without `chat=self.chat`:

```python
self.extraction = ChatKnowledgeExtractionService(
    chat_generation=self.chat_generation,
    provider=self.model_provider,
    runs=self.model_runs,
    snapshots=self.extraction_snapshots,
)
```

The current branch was re-read after the CI failure and still contained the same missing argument. This is a productive application wiring regression, not a Local-Smoke harness defect.

## Primary vs. secondary failures

**Primary:** application composition is inconsistent with the constructor contract.

**Secondary:** Local install smoke cannot reach Core/API start, restart, persistence, schema, or cleanup assertions because `AthenaApplication.__init__` aborts first.

## Required fix / mitigation

Backend owner should wire the existing chat service into `ChatKnowledgeExtractionService`, preserving the service's current constructor contract and initialization ordering. No Quality-side product patch is applied.

## Required verification

After the Backend fix lands:

1. targeted application/extraction construction test(s),
2. `athena-local-smoke --restart-cycles 1`,
3. relevant knowledge-extraction tests,
4. full Quality Gate when justified by the resulting head.

## Observed verification

- Run #2771 Local install smoke: **FAIL** at Core construction.
- Run #2771 Linux focused storage regressions: **PASS — 157 tests**, unrelated storage slice remains healthy on this head.
- Run #2771 Linux API runtime path-boundary regressions: **PASS — 12 tests**.
- Full Linux Quality and native Windows jobs were still running when this incident was created.
