# Quality Gate Incident — Run 2097 mypy failures

## Scope

Repository: `bnbgrs/pATHENA`
Branch: `agent/pathena`
Verified branch HEAD before logging: `cf0ef334216ccbcb066c34188f4bdba47271a192`
PR merge commit executed by CI: `95871cc0f598d893da918d39399aeefd1cebcedb`
Workflow: `ATHENA Quality Gate`
Run: `#2097` / run id `32651803518`
Job: `Python 3.12 quality` / job id `97224473084`
Failing step: `Run ATHENA quality gate`

## Gate state

- Dependency lock: PASS
- Specification validator: PASS (`63/63`)
- Ruff: PASS
- mypy: FAIL (`7 errors in 3 files`, `299 source files` checked)
- pytest: NOT REACHED because the gate stopped after mypy failure

## Primary failures

### QG-2097-MYPY-RESEARCH-MODELS

File: `src/athena/research/models.py`
Ownership: BACKEND
Status: OPEN / BLOCKED FOR QUALITY VERIFIER

Observed errors:

```text
src/athena/research/models.py:71: error: Unsupported operand types for > ("int" and "object") [operator]
    if value < 1:

src/athena/research/models.py:239: error: Incompatible types in assignment
(expression has type "int", variable has type "str") [assignment]
    for value, label in (
```

Root cause analysis:

1. `_positive_int(value: object, ...)` calls `_nonnegative_int(value, ...)`, but the called helper returns `None`, so mypy cannot narrow `value` from `object` to `int` for the subsequent comparison. Runtime validation is present, but static narrowing does not propagate through the helper boundary.
2. In `ResearchScopeRecord.__post_init__`, repeated reuse of loop variables named `value`/`label` across heterogeneous loops causes mypy to retain/infer an incompatible type for the later integer loop. This is a local static typing/inference problem in backend domain-model code.

Mitigation/fix direction for backend owner:

- Make integer validators return the narrowed integer and consume that return value, or perform an explicit local `isinstance(value, int)` narrowing in `_positive_int` while preserving bool rejection.
- Avoid heterogeneous reuse of the same loop variable binding where mypy infers conflicting types; use distinct variable names or a typed tuple/sequence.

Required verification after owner fix:

1. Targeted mypy on `src/athena/research/models.py`.
2. Relevant research model boundary tests.
3. Full quality gate when the other P0 mypy slices are also resolved.

### QG-2097-MYPY-RESEARCH-IDEMPOTENCY

File: `src/athena/research/idempotency.py`
Ownership: BACKEND
Status: OPEN / BLOCKED FOR QUALITY VERIFIER

Observed errors:

```text
src/athena/research/idempotency.py:56: error: Subclass of
"Sequence[tuple[ResearchSynthesisInputKind, UUID]]" and "str" cannot exist ... [unreachable]
src/athena/research/idempotency.py:56: error: ... and "bytes" cannot exist ... [unreachable]
src/athena/research/idempotency.py:56: error: ... and "bytearray" cannot exist ... [unreachable]
```

Root cause analysis:

The parameter is already statically annotated as `Sequence[tuple[ResearchSynthesisInputKind, UUID]]`. The runtime guard additionally checks whether it is `str`, `bytes`, or `bytearray`. Under the declared static type those intersections are impossible, so strict mypy reports the branches as unreachable. The runtime hardening intent is valid, but the annotation/runtime-boundary design is inconsistent.

Mitigation/fix direction for backend owner:

- If this function is a true untrusted runtime boundary, accept a broader input type (for example `object`) and narrow to the required sequence shape inside the function.
- If callers are statically trusted, remove impossible guards only if equivalent validation remains at the actual external boundary.

Required verification after owner fix:

1. Targeted mypy on `src/athena/research/idempotency.py`.
2. Idempotency boundary tests including strings/bytes/bytearray and malformed tuples if those are intended runtime inputs.
3. Full quality gate when all P0 mypy slices are resolved.

### QG-2097-MYPY-SEMANTIC

File: `src/athena/retrieval/semantic.py`
Ownership: BACKEND
Status: OPEN / BLOCKED FOR QUALITY VERIFIER

Observed errors:

```text
src/athena/retrieval/semantic.py:60: error: No overload variant of "int" matches argument type "object" [call-overload]
    normalized = int(value)
src/athena/retrieval/semantic.py:68: error: Returning Any from function declared to return "int" [no-any-return]
    return normalized
```

Root cause analysis:

`_persisted_int()` intentionally accepts `object`, but `int(object)` is not statically valid because `object` does not guarantee `SupportsInt`/`SupportsIndex`/string-or-buffer semantics. The `no-any-return` report is a consequence of that unsupported call typing, not an independent runtime bug.

Mitigation/fix direction for backend owner:

Introduce an explicit supported-input narrowing/parser before conversion while preserving the current runtime invariants: reject bool, reject unsupported persisted values, translate conversion/overflow failures to `SemanticSearchError`, enforce `>=1` when `positive=True`, otherwise enforce `>=0`.

Required verification after owner fix:

1. Targeted mypy on `src/athena/retrieval/semantic.py`.
2. Semantic persisted-state/boundary tests covering bool, invalid objects/text, overflow, zero/negative, and valid persisted integer representations intended by storage adapters.
3. Full quality gate after all P0 mypy slices are resolved.

## Integration/ownership decision

No backend product code or backend tests were modified by the Quality Gate verifier. These failures are documented and queued for the Backend owner. Quality-owned work may proceed independently while these slices remain blocked.
