"""Storage-aware extension of the desktop Core API refresh controller."""

from __future__ import annotations

from dataclasses import dataclass
from queue import SimpleQueue
from typing import Protocol, cast

from PySide6.QtCore import QMetaObject, QObject, Qt, QThreadPool, Slot

from athena.api.client import CoreApiClientError
from athena.api.contracts import StorageHealthResponse
from athena.desktop.api_controller import (
    CoreApiGateway,
    DesktopApiController,
    DesktopApiSnapshot,
    _collect_snapshot,
    _RefreshOutcome,
    _RefreshTask,
)


class StorageCoreApiGateway(CoreApiGateway, Protocol):
    """Desktop Core surface including read-only storage health."""

    def storage_health(self) -> StorageHealthResponse: ...


@dataclass(frozen=True, slots=True)
class StorageDesktopApiSnapshot(DesktopApiSnapshot):
    """Desktop snapshot augmented with independently fallible storage telemetry."""

    storage: StorageHealthResponse | None = None
    storage_error: str | None = None


class _StorageRefreshTask(_RefreshTask):
    """Collect the normal desktop snapshot plus storage health off the UI thread."""

    def __init__(
        self,
        *,
        gateway: StorageCoreApiGateway,
        chat_limit: int,
        outcomes: SimpleQueue[_RefreshOutcome],
        receiver: QObject,
    ) -> None:
        super().__init__(
            gateway=gateway,
            chat_limit=chat_limit,
            outcomes=outcomes,
            receiver=receiver,
        )
        self.storage_gateway = gateway

    @Slot()
    def run(self) -> None:
        try:
            base = _collect_snapshot(
                self.storage_gateway,
                chat_limit=self.chat_limit,
            )
            try:
                storage = self.storage_gateway.storage_health()
            except CoreApiClientError as exc:
                storage = None
                storage_error = str(exc)
            except Exception:
                storage = None
                storage_error = "ATHENA storage status refresh failed."
            else:
                storage_error = None

            snapshot = StorageDesktopApiSnapshot(
                health=base.health,
                provider=base.provider,
                models=base.models,
                chats=base.chats,
                chat_error=base.chat_error,
                model_error=base.model_error,
                chat_freshness=base.chat_freshness,
                model_freshness=base.model_freshness,
                storage=storage,
                storage_error=storage_error,
            )
        except CoreApiClientError as exc:
            outcome = _RefreshOutcome(error=str(exc))
        except Exception:
            outcome = _RefreshOutcome(error="ATHENA Core status refresh failed.")
        else:
            outcome = _RefreshOutcome(snapshot=snapshot)

        self.outcomes.put(outcome)
        queued = QMetaObject.invokeMethod(
            self.receiver,
            "_drain_worker_outcome",
            Qt.ConnectionType.QueuedConnection,
        )
        if not queued:
            raise RuntimeError(
                "ATHENA desktop could not queue the API refresh result."
            )


class StorageDesktopApiController(DesktopApiController):
    """Desktop controller that preserves storage health in emitted snapshots."""

    def __init__(
        self,
        gateway: StorageCoreApiGateway,
        *,
        thread_pool: QThreadPool | None = None,
        chat_limit: int = 50,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(
            gateway,
            thread_pool=thread_pool,
            chat_limit=chat_limit,
            parent=parent,
        )

    def _start_refresh_task(self) -> None:
        gateway = cast(StorageCoreApiGateway, self.gateway)
        task = _StorageRefreshTask(
            gateway=gateway,
            chat_limit=self.chat_limit,
            outcomes=self._outcomes,
            receiver=self,
        )
        self._active_task = task
        if not self._refreshing:
            self._refreshing = True
            self.refresh_state_changed.emit(True)
        self.thread_pool.start(task)

    def _stabilize_snapshot(
        self,
        snapshot: DesktopApiSnapshot,
    ) -> DesktopApiSnapshot:
        stable = super()._stabilize_snapshot(snapshot)
        if not isinstance(snapshot, StorageDesktopApiSnapshot):
            return stable
        return StorageDesktopApiSnapshot(
            health=stable.health,
            provider=stable.provider,
            models=stable.models,
            chats=stable.chats,
            chat_error=stable.chat_error,
            model_error=stable.model_error,
            chat_freshness=stable.chat_freshness,
            model_freshness=stable.model_freshness,
            storage=snapshot.storage,
            storage_error=snapshot.storage_error,
        )
