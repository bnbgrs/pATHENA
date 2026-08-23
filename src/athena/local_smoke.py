"""Model-free end-to-end smoke test for a local pATHENA installation."""

from __future__ import annotations

import argparse
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from athena.api.client import CoreApiClient
from athena.api.process import CoreApiProcess
from athena.config.settings import AthenaSettings, ConfigurationError
from athena.storage.paths import RuntimePaths
from athena.storage.recovery import inspect_database_read_only
from athena.storage.schema import SCHEMA_VERSION

_DEFAULT_RESTART_CYCLES = 2
_MAX_RESTART_CYCLES = 10


@dataclass(frozen=True, slots=True)
class LocalSmokeReport:
    local_root: Path
    chat_id: str
    first_core_status: str
    restarted_core_status: str
    persisted_chat_count: int
    database_schema_version: int
    api_runtime_clean: bool
    restart_cycles: int


def _settings(local_root: Path) -> AthenaSettings:
    return AthenaSettings(
        local_root=local_root.resolve(),
        model_request_timeout_seconds=0.1,
        model_generation_timeout_seconds=1.0,
    )


def _client(process: CoreApiProcess) -> CoreApiClient:
    return CoreApiClient(
        process.runtime_root,
        timeout_seconds=2.0,
        generation_timeout_seconds=2.0,
    )


def _assert_safe_keep_root(root: Path) -> Path:
    """Reject the configured live data root before a smoke test can mutate it."""
    resolved = root.resolve(strict=False)
    try:
        live_root = AthenaSettings.from_environment().local_root.resolve(strict=False)
    except ConfigurationError as exc:
        raise RuntimeError(
            "Cannot establish the configured pATHENA runtime root safely. "
            "Fix the local configuration before using --keep-root."
        ) from exc

    if resolved == live_root:
        raise RuntimeError(
            "athena-local-smoke refuses to use the configured live pATHENA "
            "runtime root as test data. Choose a separate --keep-root directory."
        )
    return resolved


def _assert_api_runtime_cleared(process: CoreApiProcess) -> None:
    stale = tuple(
        path
        for path in (
            process.server.runtime.discovery_path,
            process.server.runtime.token_path,
        )
        if path.exists()
    )
    if stale:
        joined = ", ".join(str(path) for path in stale)
        raise RuntimeError(
            "Local smoke found stale Core API bootstrap files after shutdown: "
            f"{joined}."
        )


def _verify_database_schema(settings: AthenaSettings) -> int:
    paths = RuntimePaths.from_settings(settings)
    report = inspect_database_read_only(paths.database_path)
    if not report.exists:
        raise RuntimeError("Local smoke database disappeared after Core restart.")
    if report.schema_version != SCHEMA_VERSION:
        raise RuntimeError(
            "Local smoke database schema mismatch after restart: "
            f"expected {SCHEMA_VERSION}, found {report.schema_version}."
        )
    return SCHEMA_VERSION


def _validate_restart_cycles(restart_cycles: int) -> int:
    if isinstance(restart_cycles, bool) or not 1 <= restart_cycles <= _MAX_RESTART_CYCLES:
        raise ValueError(
            f"Local smoke restart cycles must be between 1 and {_MAX_RESTART_CYCLES}."
        )
    return restart_cycles


def _restart_cycles_argument(value: str) -> int:
    try:
        restart_cycles = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("restart cycles must be an integer") from exc
    try:
        return _validate_restart_cycles(restart_cycles)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def run_local_smoke(
    local_root: Path,
    *,
    restart_cycles: int = _DEFAULT_RESTART_CYCLES,
) -> LocalSmokeReport:
    """Prove Core/API persistence across repeated clean restarts without a model."""
    restart_cycles = _validate_restart_cycles(restart_cycles)
    settings = _settings(local_root)

    first = CoreApiProcess(settings=settings)
    first.start()
    try:
        first_client = _client(first)
        first_health = first_client.health()
        created = first_client.create_chat()
        chat_id = created.chat_id
        if not chat_id:
            raise RuntimeError("Local smoke created a chat without durable identity.")
    finally:
        first.stop()
    _assert_api_runtime_cleared(first)

    restarted_core_status = ""
    persisted_chat_count = 0
    for cycle in range(1, restart_cycles + 1):
        restarted = CoreApiProcess(settings=settings)
        restarted.start()
        try:
            restarted_client = _client(restarted)
            restarted_health = restarted_client.health()
            restarted_core_status = restarted_health.core_status
            chats = restarted_client.list_chats(limit=50)
            persisted_chat_count = len(chats)
            matching = tuple(chat for chat in chats if chat.chat_id == chat_id)
            if len(matching) != 1:
                raise RuntimeError(
                    "Local smoke could not recover exactly one persisted chat "
                    f"after restart cycle {cycle}."
                )
            loaded = restarted_client.load_chat(chat_id)
            if loaded.chat_id != chat_id:
                raise RuntimeError(
                    "Local smoke reloaded a different chat after restart "
                    f"cycle {cycle}."
                )
        finally:
            restarted.stop()
        _assert_api_runtime_cleared(restarted)

    database_schema_version = _verify_database_schema(settings)

    return LocalSmokeReport(
        local_root=settings.local_root,
        chat_id=chat_id,
        first_core_status=first_health.core_status,
        restarted_core_status=restarted_core_status,
        persisted_chat_count=persisted_chat_count,
        database_schema_version=database_schema_version,
        api_runtime_clean=True,
        restart_cycles=restart_cycles,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="athena-local-smoke",
        description=(
            "Run a disposable model-free Core/API/restart smoke test without "
            "touching the normal pATHENA data root."
        ),
    )
    parser.add_argument(
        "--keep-root",
        type=Path,
        help=(
            "Use this explicit directory instead of a disposable temporary root. "
            "The directory is pATHENA test data, not the normal runtime root."
        ),
    )
    parser.add_argument(
        "--restart-cycles",
        type=_restart_cycles_argument,
        default=_DEFAULT_RESTART_CYCLES,
        help=(
            "Number of full stop/start verification cycles after the initial "
            f"chat creation (default: {_DEFAULT_RESTART_CYCLES}, max: {_MAX_RESTART_CYCLES})."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.keep_root is not None:
        root = args.keep_root.expanduser()
        if not root.is_absolute():
            print("athena-local-smoke: --keep-root must be an absolute path")
            return 2
        try:
            root = _assert_safe_keep_root(root)
        except RuntimeError as exc:
            print(f"athena-local-smoke: {exc}")
            return 2
        root.mkdir(parents=True, exist_ok=True)
        report = run_local_smoke(root, restart_cycles=args.restart_cycles)
    else:
        with tempfile.TemporaryDirectory(prefix="pathena-local-smoke-") as directory:
            report = run_local_smoke(
                Path(directory),
                restart_cycles=args.restart_cycles,
            )

    print("pATHENA local smoke: PASS")
    print(f"Root: {report.local_root}")
    print(f"Chat: {report.chat_id}")
    print(f"First Core: {report.first_core_status}")
    print(f"Restarted Core: {report.restarted_core_status}")
    print(f"Restart cycles: {report.restart_cycles}")
    print(f"Persisted chats: {report.persisted_chat_count}")
    print(f"Database schema: {report.database_schema_version}")
    print(f"API bootstrap cleanup: {'PASS' if report.api_runtime_clean else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
