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


@dataclass(frozen=True, slots=True)
class LocalSmokeReport:
    local_root: Path
    chat_id: str
    first_core_status: str
    restarted_core_status: str
    persisted_chat_count: int


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


def run_local_smoke(local_root: Path) -> LocalSmokeReport:
    """Prove Core/API persistence across a clean process restart without a model."""
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

    restarted = CoreApiProcess(settings=settings)
    restarted.start()
    try:
        restarted_client = _client(restarted)
        restarted_health = restarted_client.health()
        chats = restarted_client.list_chats(limit=50)
        matching = tuple(chat for chat in chats if chat.chat_id == chat_id)
        if len(matching) != 1:
            raise RuntimeError(
                "Local smoke could not recover exactly one persisted chat after restart."
            )
        loaded = restarted_client.load_chat(chat_id)
        if loaded.chat_id != chat_id:
            raise RuntimeError("Local smoke reloaded a different chat after restart.")
    finally:
        restarted.stop()

    return LocalSmokeReport(
        local_root=settings.local_root,
        chat_id=chat_id,
        first_core_status=first_health.core_status,
        restarted_core_status=restarted_health.core_status,
        persisted_chat_count=len(chats),
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
        report = run_local_smoke(root)
    else:
        with tempfile.TemporaryDirectory(prefix="pathena-local-smoke-") as directory:
            report = run_local_smoke(Path(directory))

    print("pATHENA local smoke: PASS")
    print(f"Root: {report.local_root}")
    print(f"Chat: {report.chat_id}")
    print(f"First Core: {report.first_core_status}")
    print(f"Restarted Core: {report.restarted_core_status}")
    print(f"Persisted chats: {report.persisted_chat_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
