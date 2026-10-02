# Recovery derived-state rebuild — current Develop port

## Scope

Current-Develop reconstruction of historical PR #366.

## Operator command

`athena-recover rebuild-derived <target>`

Supported bounded targets:
- `canonical-fts`
- `archive-fts`
- `canonical-hnsw`
- `archive-hnsw`

The command uses the existing guarded `DerivedRecoveryService` and never starts the normal `AthenaApplication`. HNSW rebuilds consume already-persisted vectors; this path does not call a model/provider.

## Error truth

Recovery diagnostics now distinguishes known canonical/Derived recovery conditions from unexpected diagnostic implementation failures. Unexpected failures block normal Core startup but are not mislabeled as database corruption or Derived-State corruption, and their exception text is not copied into the structured report.

## Import boundary

`BackupService` is lazy-imported only by `restore-path`, keeping diagnose/rebuild entrypoints independent from the broader Backup graph.

## Validation

Ported focused tests cover all four targets, exit semantics, unmasked programming defects, parser bounds, installed CLI dispatch, diagnostic classification/privacy, and the minimal import boundary.

Base: `develop/pathena-next` @ `3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5`.
Historical source: PR #366.

Do not merge until exact-head repository CI is terminal green.
