# Manual handoff — Jobs CLI one-line framing — 2026-10-02

## Ausgangslage

Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.

The native Jobs workspace consumes `athena.desktop.jobs_cli list` as one TSV record
per durable job and then parses the output with Python `splitlines()`.

`_scope_summary()` included user-controlled job scope content in the final TSV field,
but sanitized only tab and `\n`. Carriage returns and other separators recognized by
`str.splitlines()` remained intact. A Research query or other requested-scope value
containing one of those separators could therefore split one durable job across multiple
logical records. The desktop parser would discard the malformed fragments or display an
incomplete/misaligned row.

Fallback JSON-object keys were also inserted without any delimiter sanitization.

## Root cause

The CLI has an implicit line-framing protocol, but user-controlled text did not pass
through one canonical single-line encoder before entering that protocol.

This is a serialization-boundary bug, not a database/job-state bug.

## Änderungen

- add `_single_line(value)` as the single framing sanitizer;
- replace tabs with spaces;
- collapse all separators recognized by Python `splitlines()` into spaces, including
  CR, LF, CRLF, vertical tab, form feed, record separators, NEL, U+2028 and U+2029;
- apply the sanitizer to invalid-JSON diagnostic scope text;
- apply it to non-object JSON scope values;
- apply it to preferred scope values;
- apply it to both fallback object keys and values;
- keep the existing length limits and TSV column contract unchanged.

No durable Job repository/service state transition or scheduler behavior is changed.

## Dateien

- `src/athena/desktop/jobs_cli.py`
- `tests/unit/test_jobs_cli_framing.py`
- this handoff

## Validation coverage

Focused tests assert:

1. all Python line-boundary classes collapse to one line;
2. preferred fields cannot inject TSV/newline framing;
3. fallback object keys and values cannot inject framing;
4. invalid JSON diagnostics remain one line;
5. the real `_print_list()` serializer emits exactly one record with exactly 8 TSV
   fields for a malicious multiline Research query.

Exact-head GitHub CI remains authoritative because this execution environment cannot
clone github.com directly.

## Parallel work / conflict risk

No active PR found during slice creation modifies either changed product/test file.
The branch deliberately avoids:
- #325 Storage
- #327 Quality harness
- #329/#335/#337 Chat cancellation
- #330 UI composer
- #331/#334/#340 LM Studio runtime
- #332 Update security
- #333 Settings
- #336 Sources import queue
- #338 Chat actor identity
- #339 Windows packaged Sources routing

Primary conflict surface: `src/athena/desktop/jobs_cli.py` only.

## Next steps

1. exact-head Quality;
2. if green, integrate history-preserving through normal supervisor flow;
3. do not weaken desktop parsing or switch to permissive malformed-row recovery as a
   substitute for keeping the producer framing valid.

## Branch / commits

Branch: `fix/jobs-cli-single-line-summary-20261002-sol`

Base: `67174198e1494fd4c8678aad60756c39ef5c160b`

- `46dae1314e007c4da4da3ab8b3f9d2454e737b27` — fix serializer framing
- `de18f80920492244c2193d2d746984935a94e843` — focused framing regressions
