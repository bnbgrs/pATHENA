"""Minimal disaster-recovery CLI that never starts the normal ATHENA Core."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from athena.config.settings import AthenaSettings, ConfigurationError
from athena.core.derived_recovery import (
    DerivedRecoveryError,
    DerivedRecoveryRequiredError,
    DerivedRecoveryService,
)
from athena.core.recovery_diagnostics import (
    RecoveryDiagnosticsService,
)
from athena.storage.paths import RuntimePaths

_DERIVED_REBUILD_TARGETS = (
    "canonical-fts",
    "archive-fts",
    "canonical-hnsw",
    "archive-hnsw",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the intentionally small disaster-recovery command surface."""
    parser = argparse.ArgumentParser(
        prog="athena-recover",
        description=(
            "ATHENA minimal disaster-recovery entry. "
            "Normal Core startup is deliberately bypassed."
        ),
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    restore = commands.add_parser(
        "restore-path",
        help=(
            "Restore one completed backup path into a new isolated ATHENA root "
            "without opening the configured live athena.db."
        ),
    )
    restore.add_argument(
        "snapshot_root",
        type=Path,
    )
    restore.add_argument(
        "destination_root",
        type=Path,
    )

    commands.add_parser(
        "diagnose",
        help=(
            "Inspect canonical and Derived State read-only and emit a "
            "payload-free Recovery failure matrix."
        ),
    )

    rebuild = commands.add_parser(
        "rebuild-derived",
        help=(
            "Explicitly rebuild one reconstructible search/index layer after "
            "Recovery diagnostics have established a safe source state."
        ),
    )
    rebuild.add_argument(
        "target",
        choices=_DERIVED_REBUILD_TARGETS,
        help=(
            "Derived layer to rebuild: canonical/archive FTS or canonical/archive "
            "HNSW from already persisted vectors."
        ),
    )

    return parser


def run_restore_path(
    snapshot_root: Path,
    *,
    destination_root: Path,
) -> int:
    """Execute one isolated restore without constructing AthenaApplication."""
    from athena.backup.service import BackupRestoreError, BackupService

    try:
        settings = AthenaSettings.from_environment()
        paths = RuntimePaths.from_settings(settings)

        destination = BackupService.restore_path_without_live_runtime(
            snapshot_root,
            destination_root=destination_root,
            paths=paths,
        )

    except ConfigurationError as exc:
        print(
            f"ATHENA recovery configuration error: {exc}",
            file=sys.stderr,
        )
        return 2

    except (
        BackupRestoreError,
        OSError,
        ValueError,
    ) as exc:
        print(
            f"ATHENA recovery error: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    print(
        f"Restored isolated ATHENA root: {destination}"
    )
    print(
        "Normal ATHENA Core startup was bypassed."
    )
    print(
        "The configured live athena.db was not opened for this restore."
    )
    print(
        "Protected scopes remain locked until normal startup and explicit unlock."
    )
    return 0


def run_diagnose() -> int:
    """Emit one machine-readable payload-free Recovery diagnosis."""
    try:
        settings = AthenaSettings.from_environment()
        paths = RuntimePaths.from_settings(
            settings
        )

    except ConfigurationError as exc:
        print(
            json.dumps(
                {
                    "error": (
                        "recovery-configuration-invalid"
                    ),
                    "error_type": type(exc).__name__,
                    "status": "recovery-required",
                },
                sort_keys=True,
            )
        )
        return 2

    report = RecoveryDiagnosticsService(
        paths=paths
    ).inspect()

    print(
        json.dumps(
            report.as_payload(),
            sort_keys=True,
        )
    )

    return report.exit_code


def run_rebuild_derived(
    target: str,
) -> int:
    """Run one explicit Derived State rebuild without starting AthenaApplication."""
    if target not in _DERIVED_REBUILD_TARGETS:
        raise ValueError(
            f"Unsupported Derived Recovery rebuild target: {target!r}"
        )

    try:
        settings = AthenaSettings.from_environment()
        paths = RuntimePaths.from_settings(
            settings
        )
        service = DerivedRecoveryService(
            database_path=paths.database_path,
            derived_root=paths.derived_root,
        )

        if target == "canonical-fts":
            count = service.rebuild_canonical_fts()
            result_name = "documents_indexed"
        elif target == "archive-fts":
            count = service.rebuild_archive_fts()
            result_name = "documents_indexed"
        elif target == "canonical-hnsw":
            count = service.rebuild_canonical_hnsw_from_persisted()
            result_name = "model_indexes_rebuilt"
        else:
            count = service.rebuild_archive_hnsw_from_persisted()
            result_name = "model_indexes_rebuilt"

    except ConfigurationError as exc:
        print(
            f"ATHENA recovery configuration error: {exc}",
            file=sys.stderr,
        )
        return 2

    except DerivedRecoveryRequiredError as exc:
        print(
            f"ATHENA recovery required: {exc}",
            file=sys.stderr,
        )
        return 4

    except (
        DerivedRecoveryError,
        OSError,
    ) as exc:
        print(
            f"ATHENA recovery rebuild error: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    print(
        "Derived Recovery rebuild complete: "
        f"target={target} {result_name}={count}"
    )
    print(
        "Normal ATHENA Core startup was bypassed."
    )
    print(
        "No model/provider call was used for this rebuild."
    )
    return 0


def main(
    argv: Sequence[str] | None = None,
) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "restore-path":
        return run_restore_path(
            args.snapshot_root,
            destination_root=args.destination_root,
        )

    if args.command == "diagnose":
        return run_diagnose()

    if args.command == "rebuild-derived":
        return run_rebuild_derived(
            args.target
        )

    raise RuntimeError(
        f"Unsupported recovery command: {args.command!r}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
