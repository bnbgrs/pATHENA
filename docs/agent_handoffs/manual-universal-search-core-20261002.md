# Manual handoff — Universal Search Core + local transport — 2026-10-02

## Ausgangslage

Issue #296 verlangt einen Core-backed Universal-Search-Pfad über Chats,
KnowledgeUnits, Claims, ResearchResults, Sources und Jobs. Vor diesem Run gab
es nur den bestehenden Normal-Hybrid-Search-Pfad für revisionierte Knowledge-,
Claim- und Chat-Message-Inhalte. Der Desktop-Command-Palette-Pfad hatte keinen
einheitlichen Core-Result-Stream für alle sechs Domänen.

Der Run startete auf `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.
Während der Arbeit integrierte Develop die Chat-Cancellation-Arbeit und rückte
auf `467ef434236c320e4afe9d21a39c20a4a2b75728` vor. Der Arbeitsbranch wurde
daraufhin per normalem Merge-Commit synchronisiert; kein Rebase, Reset,
Force-Push oder Fremdbranch-Edit.

## Root Cause

Der bestehende Search-Vertrag setzt eine echte Canonical Revision voraus.
Das ist für KnowledgeUnits, Claims und ChatMessages korrekt, aber nicht für
Sources, Durable Jobs und immutable ResearchResults. Diese Typen in den
bestehenden revisionierten FTS-/Semantic-Contract zu zwingen hätte Fake-
Revisionen oder einen zweiten UI-Index erzeugt.

Zusätzlich wären direkte Mehrwortabfragen über die neuen SQL-Pfade zunächst
als zusammenhängende Phrase behandelt worden. Das hätte gegenüber der
bestehenden tokenbasierten FTS-Suche falsche Negative erzeugt. Der Pfad wurde
vor Abschluss auf deterministisches AND über normalisierte Suchterme korrigiert.

## Änderungen

### Core

- Neuer `UniversalSearchService` mit stabiler Taxonomie:
  - `knowledge`
  - `claim`
  - `chat_message`
  - `research_result`
  - `source`
  - `job`
- Knowledge/Claim/Chat nutzen weiterhin den bestehenden lexical Hybrid-Pfad.
- Sources, ResearchResults und Jobs werden aus canonical SQLite state gelesen.
- Für nicht-revisionierte Typen bleibt `revision_id=None`; keine Fake-Revision.
- Stabile typisierte `result_ref`-Identitäten, z. B. `source:<uuid>`.
- Deterministische Filter, Limits, Ranking und Tie-Breaks.
- Mehrwortsuche der direkten SQL-Pfade verwendet AND-Semantik über Suchterme.
- Protected Sources, Jobs und ResearchResults werden aus diesem unprotected
  Suchpfad ausgeschlossen.
- Sources in einer laufenden `source_protection_transitions`-Transition werden
  ebenfalls fail-closed ausgeschlossen, bevor Metadaten in Search gelangen.

### Core API / Transport

- `CoreApiFacade.universal_search(...)`.
- Capability `search.universal.local`.
- `CoreApiSurface` und `SerializedCoreApiSurface` erweitert.
- Authentifizierter GET `/api/v1/search` mit:
  - `q`
  - `limit` (1..100)
  - optional `types` als kanonische, komma-separierte Typfilter.
- Query-Parameter werden fail-closed validiert; unbekannte Typen/Parameter
  liefern `invalid_request`.
- Desktop `CoreApiClient.universal_search(...)` dekodiert den vorhandenen
  `SearchResultResponse`-Vertrag und erhält `revision_id=None` unverändert.

### Application Composition

- `AthenaApplication` baut `UniversalSearchService` auf dem bereits
  vorhandenen `HybridRetrievalService` auf.
- Kein zweiter Desktop-Index, kein neuer Worker/Event-Bus/Manager.

## Wichtige Dateien

Produktcode:

- `src/athena/retrieval/universal.py`
- `src/athena/api/search_adapter.py`
- `src/athena/api/service.py`
- `src/athena/api/ports.py`
- `src/athena/api/executor.py`
- `src/athena/api/asgi.py`
- `src/athena/api/client.py`
- `src/athena/core/application.py`

Tests:

- `tests/unit/test_universal_search.py`
- `tests/unit/test_core_api_universal_search_wiring.py`
- `tests/unit/test_core_api_asgi.py`
- `tests/unit/test_core_api_client.py`
- `tests/integration/test_universal_search_app.py`

## Verhalten danach

Der Core besitzt jetzt einen einzigen lokalen Search-Result-Stream für die
sechs in #296 geforderten Domänen. Desktop-/Transport-Clients müssen keine
zweite Suchdatenbank pflegen. Search-Result-Identitäten sind stabil und der
Protection-/Revision-Status bleibt wahrheitsgetreu.

Der Quick Switcher selbst ist in diesem Branch noch **nicht** auf den neuen
Client verdrahtet. Das ist bewusst nicht parallel umgesetzt worden, weil der
aktive UI-PR #337 derzeit `desktop/api_controller.py`,
`desktop/pathena_window.py` und `desktop/window.py` besitzt.

## Validierung

Implementiert sind fokussierte Regressionen für:

- Cross-domain Aggregation.
- Protection-Ausschluss inklusive Source-Protection-Transition-Fence.
- Filter-/Limit-Validierung.
- order-independent Multi-Term-Matching.
- Core-Facade Capability/Wiring.
- HTTP Query-/Filter-Parsing und Fehlerfall.
- Desktop-Client URL/DTO-Decoding.
- echter `AthenaApplication`-Start mit realem Schema, echter Source-Capture,
  echtem validierten Durable Job und Universal-Search-Leseweg.

Lokaler Checkout/Testlauf war in diesem Runner nicht möglich: direkter Zugriff
auf `github.com` scheitert hier an DNS-Auflösung. Daher wird **kein lokaler
PASS** behauptet.

Der finale GitHub-Actions-Status wird nach diesem letzten Handoff-Commit im
Draft-PR #368 dokumentiert. Für den tatsächlichen Gate-Status ist der PR-Head
maßgeblich; nach diesem Commit werden keine weiteren Code-/Dokument-Commits
mehr erzeugt, damit der validierte SHA stabil bleibt.

## Bekannte Restprobleme / nächste Schritte

1. Quality-Gate #36939853971 auswerten und jeden branch-eigenen Fehler beheben.
2. Nach Merge/Abschluss des aktiven UI-PR #337 den Quick Switcher auf
   `CoreApiClient.universal_search` verdrahten.
3. Result-Navigation über `result_ref` je Workspace exakt auflösen; nicht nur
   auf den Workspace springen.
4. ResearchResult-Suche ist Core-seitig implementiert und durch Unit-Schema
   abgesichert; ein zusätzlicher realer Research-Orchestration-Integrationstest
   wäre sinnvoll, wenn die Testkosten vertretbar sind.
5. Die direkten Source/Job/Research-SQL-Pfade sind derzeit lexical table scans.
   Erst bei gemessener realer Latenz einen Derived-State-Index ergänzen; keinen
   zweiten UI-Index vorab einführen.

## Abhängigkeiten / Konfliktrisiko

- PR #337 besitzt aktuell die relevanten Desktop-Window/API-Controller-Dateien;
  dort keine parallele UI-Verdrahtung begonnen.
- PR #333 ist offen und verändert `src/athena/api/asgi.py` sowie
  `src/athena/api/service.py` für News Enable/Disable. Semantisch getrennt,
  aber potenzielles Git-Hunk-Risiko um Capability/Route/attach-Blöcke.
  Beim Integrieren von #333 Universal-Search-Routen/Capability explizit erhalten.
- Chat-Cancellation PR #329 ist bereits geschlossen/in Develop integriert und
  wurde beim Merge-Sync dieses Branches erhalten.

## Branch / PR / Commit

- Branch: `feature/universal-search-core-20261002-sol`
- Draft PR: #368 — `Search: add real cross-domain Core universal search`
- PR: https://github.com/bnbgrs/pATHENA/pull/368
- Handoff-Stand vor finalem Gate: `343a1985e7c5d05709f81fdb3b8e3077d0e60a7d`
