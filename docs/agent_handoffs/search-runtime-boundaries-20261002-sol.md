# Search runtime-boundary handoff — 2026-10-02

## Ausgangslage

Local Search and its canonical API DTO trusted Python type annotations at runtime.
Malformed queries, bool/float limits and raw-string entity filters could fail only
after index/SQLite access. Canonical Search response text also accepted leading
or trailing whitespace, and uppercase UUID strings were accepted despite the
canonical UUID contract.

## Root Cause

`LocalSearchService.search()` performed range/semantic checks but no exact
runtime type checks. The API text helper validated `value.strip()` but returned
the untrimmed original, while UUID canonicalization compared against
`text.lower()`.

## Änderungen

- fail fast on non-text local-search queries;
- require genuine integer limits (bool excluded);
- require `SearchEntityType | None` at the filter boundary;
- prove malformed requests fail before index access;
- reject leading/trailing whitespace in canonical Search identity/method text;
- require exact lowercase canonical UUID text;
- add focused regression coverage.

## Dateien

- `src/athena/retrieval/search.py`
- `tests/unit/test_local_search.py`
- `src/athena/api/search_contracts.py`
- `tests/unit/test_search_api_contracts.py`
- this handoff

## Verhalten danach

Malformed Search requests now terminate deterministically before derived-index or
SQLite work. Search transport identities have one canonical textual
representation instead of accepting visually equivalent but byte-distinct forms.

## Validierung

No local PASS is claimed because this runner cannot resolve github.com for a
checkout. Exact-head GitHub Actions are authoritative. Earlier Quality scheduling
for pre-handoff head `62a706fdf8c460d5131ac697f795e6b729313bba`
must not be treated as final-head evidence after this documentation commit.

## Abhängigkeiten / Konfliktrisiko

Original code base:
`develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.
Before publication Develop advanced to
`467ef434236c320e4afe9d21a39c20a4a2b75728` via Chat cancellation integration.
All four product/test blobs changed by this slice were explicitly compared and
were unchanged on that newer Develop head, so no file collision was observed.

PR #368 owns the separate Universal Search feature. Do not broaden this PR into
Universal Search, API transport or Quick Switcher work.

## Nächste sinnvolle Schritte

1. Qualify this final exact head with canonical ATHENA Quality.
2. Keep #368's Universal Search work separate.
3. Integrator should re-check the four Search blobs immediately before merge and
   preserve these fail-fast/canonicalization invariants.
