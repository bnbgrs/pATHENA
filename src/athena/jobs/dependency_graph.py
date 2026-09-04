"""Durable dependency, parent/child, and priority-inheritance semantics."""

from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.jobs.models import JobPriority, JobState, WaitingReason
from athena.jobs.repository import JobNotFoundError, JobRepository

_MAX_DIRECT_DEPENDENCIES = 64
_MAX_GRAPH_DEPTH = 32
_MAX_GRAPH_NODES = 256


class ParentCompletionPolicy(str, Enum):
    """Whether an explicit child blocks parent completion."""

    INDEPENDENT = "independent"
    REQUIRE_SUCCESS = "require_success"


class ChildCancellationPolicy(str, Enum):
    """Whether cancelling a parent cascades to this child."""

    INDEPENDENT = "independent"
    CASCADE = "cascade"


class JobGraphError(RuntimeError):
    """Base error for durable job graph policy failures."""


class JobGraphCorruptionError(JobGraphError):
    """Raised when persisted graph structure is unsafe or internally inconsistent."""


class JobDependencyBlockedError(JobGraphError):
    """Raised when a job is not runnable because a dependency is incomplete."""


class JobParentCompletionBlockedError(JobGraphError):
    """Raised when an explicit child policy blocks parent completion."""


@dataclass(frozen=True, slots=True)
class JobGraphSnapshot:
    job_id: uuid.UUID
    parent_job_id: uuid.UUID | None
    parent_completion_policy: ParentCompletionPolicy | None
    child_cancellation_policy: ChildCancellationPolicy | None
    depends_on_job_ids: tuple[uuid.UUID, ...]


class JobDependencyGraph:
    """Persistent job graph with bounded fail-closed traversal."""

    def __init__(self, repository: JobRepository) -> None:
        self.repository = repository
        self.database = repository.database

    def validate_new_links(
        self,
        *,
        parent_job_id: uuid.UUID | None,
        depends_on_job_ids: Iterable[uuid.UUID],
    ) -> tuple[uuid.UUID, ...]:
        dependencies = _normalized_ids(depends_on_job_ids)
        with self.database.connection as connection:
            self._require_integrity(connection)
            if parent_job_id is not None:
                self._require_job(connection, parent_job_id)
            for dependency_id in dependencies:
                self._require_job(connection, dependency_id)
        return dependencies

    def configure(
        self,
        job_id: uuid.UUID,
        *,
        parent_job_id: uuid.UUID | None = None,
        parent_completion_policy: ParentCompletionPolicy = ParentCompletionPolicy.INDEPENDENT,
        child_cancellation_policy: ChildCancellationPolicy = ChildCancellationPolicy.INDEPENDENT,
        depends_on_job_ids: Iterable[uuid.UUID] = (),
    ) -> None:
        dependencies = _normalized_ids(depends_on_job_ids)
        completion_policy = _completion_policy(parent_completion_policy)
        cancellation_policy = _cancellation_policy(child_cancellation_policy)
        now = utc_now_us()

        with self.database.write_transaction() as connection:
            self._require_integrity(connection)
            self._require_graph_editable_job(connection, job_id)
            if parent_job_id is not None:
                self._require_job(connection, parent_job_id)
                if parent_job_id == job_id:
                    raise JobGraphError("A job cannot be its own parent.")
            for dependency_id in dependencies:
                self._require_job(connection, dependency_id)
                if dependency_id == job_id:
                    raise JobGraphError("A job cannot depend on itself.")

            dependency_graph = self._dependency_adjacency(connection)
            dependency_graph[job_id] = set(dependencies)
            self._assert_acyclic_from(job_id, dependency_graph, label="dependency")

            parent_graph = self._parent_adjacency(connection)
            parent_graph[job_id] = set() if parent_job_id is None else {parent_job_id}
            self._assert_acyclic_from(job_id, parent_graph, label="parent")

            connection.execute(
                "DELETE FROM job_dependencies WHERE job_id = ?",
                (uuid_to_blob(job_id),),
            )
            for dependency_id in dependencies:
                connection.execute(
                    """
                    INSERT INTO job_dependencies(job_id, depends_on_job_id, created_at_us)
                    VALUES (?, ?, ?)
                    """,
                    (uuid_to_blob(job_id), uuid_to_blob(dependency_id), now),
                )

            connection.execute(
                "DELETE FROM job_parent_links WHERE job_id = ?",
                (uuid_to_blob(job_id),),
            )
            if parent_job_id is not None:
                connection.execute(
                    """
                    INSERT INTO job_parent_links(
                        job_id, parent_job_id, completion_policy,
                        cancellation_policy, created_at_us
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        uuid_to_blob(job_id),
                        uuid_to_blob(parent_job_id),
                        completion_policy.value,
                        cancellation_policy.value,
                        now,
                    ),
                )

            self._reconcile_job_row(connection, job_id, now_us=now)

    def replace_dependencies(
        self,
        job_id: uuid.UUID,
        depends_on_job_ids: Iterable[uuid.UUID],
    ) -> None:
        snapshot = self.snapshot(job_id)
        self.configure(
            job_id,
            parent_job_id=snapshot.parent_job_id,
            parent_completion_policy=(
                snapshot.parent_completion_policy or ParentCompletionPolicy.INDEPENDENT
            ),
            child_cancellation_policy=(
                snapshot.child_cancellation_policy or ChildCancellationPolicy.INDEPENDENT
            ),
            depends_on_job_ids=depends_on_job_ids,
        )

    def snapshot(self, job_id: uuid.UUID) -> JobGraphSnapshot:
        connection = self.database.connection
        self._require_integrity(connection)
        self._require_job(connection, job_id)
        parent_row = connection.execute(
            """
            SELECT parent_job_id, completion_policy, cancellation_policy
            FROM job_parent_links
            WHERE job_id = ?
            """,
            (uuid_to_blob(job_id),),
        ).fetchone()
        dependency_rows = connection.execute(
            """
            SELECT depends_on_job_id
            FROM job_dependencies
            WHERE job_id = ?
            ORDER BY depends_on_job_id
            """,
            (uuid_to_blob(job_id),),
        ).fetchall()
        if parent_row is None:
            parent_job_id = None
            completion_policy = None
            cancellation_policy = None
        else:
            parent_job_id = uuid_from_blob(bytes(parent_row["parent_job_id"]))
            try:
                completion_policy = ParentCompletionPolicy(str(parent_row["completion_policy"]))
                cancellation_policy = ChildCancellationPolicy(
                    str(parent_row["cancellation_policy"])
                )
            except ValueError as exc:
                raise JobGraphCorruptionError(
                    "Persisted job parent policy is not recognized."
                ) from exc
        return JobGraphSnapshot(
            job_id=job_id,
            parent_job_id=parent_job_id,
            parent_completion_policy=completion_policy,
            child_cancellation_policy=cancellation_policy,
            depends_on_job_ids=tuple(
                uuid_from_blob(bytes(row["depends_on_job_id"]))
                for row in dependency_rows
            ),
        )

    def reconcile(self, *, now_us: int | None = None) -> tuple[uuid.UUID, ...]:
        now = utc_now_us() if now_us is None else now_us
        changed: list[uuid.UUID] = []
        with self.database.write_transaction() as connection:
            self._require_integrity(connection)
            rows = connection.execute(
                """
                SELECT DISTINCT job_id
                FROM job_dependencies
                ORDER BY job_id
                """
            ).fetchall()
            if len(rows) > _MAX_GRAPH_NODES:
                raise JobGraphCorruptionError(
                    "Job dependency reconciliation exceeded the bounded graph budget."
                )
            for row in rows:
                job_id = uuid_from_blob(bytes(row["job_id"]))
                if self._reconcile_job_row(connection, job_id, now_us=now):
                    changed.append(job_id)
        return tuple(changed)

    def require_runnable(self, job_id: uuid.UUID) -> None:
        connection = self.database.connection
        self._require_integrity(connection)
        self._require_job(connection, job_id)
        incomplete = self._incomplete_dependencies(connection, job_id)
        if incomplete:
            raise JobDependencyBlockedError(
                f"Job {job_id} is blocked by {len(incomplete)} incomplete dependency job(s)."
            )

    def assert_parent_completion_allowed(self, parent_job_id: uuid.UUID) -> None:
        connection = self.database.connection
        self._require_integrity(connection)
        self._require_job(connection, parent_job_id)
        rows = connection.execute(
            """
            SELECT l.job_id, j.state
            FROM job_parent_links AS l
            LEFT JOIN jobs AS j ON j.job_id = l.job_id
            WHERE l.parent_job_id = ?
              AND l.completion_policy = 'require_success'
            ORDER BY l.job_id
            """,
            (uuid_to_blob(parent_job_id),),
        ).fetchall()
        blocked: list[uuid.UUID] = []
        for row in rows:
            if row["state"] is None:
                raise JobGraphCorruptionError("Parent link points to a missing child job.")
            if JobState(str(row["state"])) is not JobState.COMPLETED:
                blocked.append(uuid_from_blob(bytes(row["job_id"])))
        if blocked:
            raise JobParentCompletionBlockedError(
                f"Parent job {parent_job_id} has {len(blocked)} required child job(s) not completed."
            )

    def cancellation_descendants(self, parent_job_id: uuid.UUID) -> tuple[uuid.UUID, ...]:
        connection = self.database.connection
        self._require_integrity(connection)
        self._require_job(connection, parent_job_id)
        result: list[uuid.UUID] = []
        frontier: list[tuple[uuid.UUID, int]] = [(parent_job_id, 0)]
        seen = {parent_job_id}
        while frontier:
            current, depth = frontier.pop(0)
            if depth >= _MAX_GRAPH_DEPTH:
                if self._cascade_children(connection, current):
                    raise JobGraphCorruptionError(
                        "Job cancellation cascade exceeded the bounded graph depth."
                    )
                continue
            for child_id in self._cascade_children(connection, current):
                if child_id in seen:
                    raise JobGraphCorruptionError(
                        "Cycle detected in persisted parent cancellation graph."
                    )
                seen.add(child_id)
                if len(seen) > _MAX_GRAPH_NODES:
                    raise JobGraphCorruptionError(
                        "Job cancellation cascade exceeded the bounded graph budget."
                    )
                result.append(child_id)
                frontier.append((child_id, depth + 1))
        return tuple(result)

    def effective_priority(self, job_id: uuid.UUID, *, now_us: int) -> JobPriority:
        connection = self.database.connection
        self._require_integrity(connection)
        root = self._require_job(connection, job_id)
        base = JobPriority(int(root["priority"]))
        if base is JobPriority.DATA_SAFETY:
            return base

        best = int(base)
        frontier: list[tuple[uuid.UUID, int]] = [(job_id, 0)]
        seen = {job_id}
        while frontier:
            dependency_id, depth = frontier.pop(0)
            if depth >= _MAX_GRAPH_DEPTH:
                if self._blocked_dependents(connection, dependency_id, now_us=now_us):
                    raise JobGraphCorruptionError(
                        "Priority inheritance exceeded the bounded graph depth."
                    )
                continue
            for dependent_id, dependent_priority in self._blocked_dependents(
                connection,
                dependency_id,
                now_us=now_us,
            ):
                donated = max(int(JobPriority.INTERACTIVE), int(dependent_priority))
                best = min(best, donated)
                if dependent_id not in seen:
                    seen.add(dependent_id)
                    if len(seen) > _MAX_GRAPH_NODES:
                        raise JobGraphCorruptionError(
                            "Priority inheritance exceeded the bounded graph budget."
                        )
                    frontier.append((dependent_id, depth + 1))
        return JobPriority(best)

    def _blocked_dependents(
        self,
        connection: sqlite3.Connection,
        dependency_id: uuid.UUID,
        *,
        now_us: int,
    ) -> tuple[tuple[uuid.UUID, JobPriority], ...]:
        rows = connection.execute(
            """
            SELECT j.job_id, j.priority, j.state, j.next_run_at_us, j.blocked_reason
            FROM job_dependencies AS d
            JOIN jobs AS j ON j.job_id = d.job_id
            WHERE d.depends_on_job_id = ?
            ORDER BY j.job_id
            """,
            (uuid_to_blob(dependency_id),),
        ).fetchall()
        result: list[tuple[uuid.UUID, JobPriority]] = []
        for row in rows:
            state = JobState(str(row["state"]))
            if state is JobState.QUEUED:
                next_run = row["next_run_at_us"]
                if next_run is not None and int(next_run) > now_us:
                    continue
            elif not (
                state is JobState.WAITING
                and str(row["blocked_reason"]) == WaitingReason.DEPENDENCY.value
            ):
                continue
            dependent_id = uuid_from_blob(bytes(row["job_id"]))
            if not self._incomplete_dependencies(connection, dependent_id):
                continue
            result.append((dependent_id, JobPriority(int(row["priority"]))))
        return tuple(result)

    def _reconcile_job_row(
        self,
        connection: sqlite3.Connection,
        job_id: uuid.UUID,
        *,
        now_us: int,
    ) -> bool:
        row = self._require_job(connection, job_id)
        state = JobState(str(row["state"]))
        if state.terminal or state in {JobState.RUNNING, JobState.CANCEL_REQUESTED, JobState.PAUSED}:
            return False
        incomplete = self._incomplete_dependencies(connection, job_id)
        if incomplete and state is JobState.QUEUED:
            connection.execute(
                """
                UPDATE jobs
                SET state = 'waiting', blocked_reason = ?, updated_at_us = ?
                WHERE job_id = ? AND state = 'queued'
                """,
                (WaitingReason.DEPENDENCY.value, now_us, uuid_to_blob(job_id)),
            )
            return True
        if (
            not incomplete
            and state is JobState.WAITING
            and str(row["blocked_reason"]) == WaitingReason.DEPENDENCY.value
        ):
            connection.execute(
                """
                UPDATE jobs
                SET state = 'queued', blocked_reason = NULL, updated_at_us = ?
                WHERE job_id = ? AND state = 'waiting' AND blocked_reason = ?
                """,
                (now_us, uuid_to_blob(job_id), WaitingReason.DEPENDENCY.value),
            )
            return True
        return False

    def _incomplete_dependencies(
        self,
        connection: sqlite3.Connection,
        job_id: uuid.UUID,
    ) -> tuple[uuid.UUID, ...]:
        rows = connection.execute(
            """
            SELECT d.depends_on_job_id, j.state
            FROM job_dependencies AS d
            LEFT JOIN jobs AS j ON j.job_id = d.depends_on_job_id
            WHERE d.job_id = ?
            ORDER BY d.depends_on_job_id
            """,
            (uuid_to_blob(job_id),),
        ).fetchall()
        if len(rows) > _MAX_DIRECT_DEPENDENCIES:
            raise JobGraphCorruptionError(
                "Persisted job has too many direct dependencies."
            )
        incomplete: list[uuid.UUID] = []
        for row in rows:
            if row["state"] is None:
                raise JobGraphCorruptionError("Job dependency points to a missing job.")
            dependency_id = uuid_from_blob(bytes(row["depends_on_job_id"]))
            if JobState(str(row["state"])) is not JobState.COMPLETED:
                incomplete.append(dependency_id)
        return tuple(incomplete)

    def _dependency_adjacency(
        self,
        connection: sqlite3.Connection,
    ) -> dict[uuid.UUID, set[uuid.UUID]]:
        result: dict[uuid.UUID, set[uuid.UUID]] = {}
        for row in connection.execute(
            "SELECT job_id, depends_on_job_id FROM job_dependencies ORDER BY job_id, depends_on_job_id"
        ):
            source = uuid_from_blob(bytes(row["job_id"]))
            target = uuid_from_blob(bytes(row["depends_on_job_id"]))
            result.setdefault(source, set()).add(target)
        return result

    def _parent_adjacency(
        self,
        connection: sqlite3.Connection,
    ) -> dict[uuid.UUID, set[uuid.UUID]]:
        result: dict[uuid.UUID, set[uuid.UUID]] = {}
        for row in connection.execute(
            "SELECT job_id, parent_job_id FROM job_parent_links ORDER BY job_id"
        ):
            child = uuid_from_blob(bytes(row["job_id"]))
            parent = uuid_from_blob(bytes(row["parent_job_id"]))
            result[child] = {parent}
        return result

    def _assert_acyclic_from(
        self,
        root: uuid.UUID,
        adjacency: dict[uuid.UUID, set[uuid.UUID]],
        *,
        label: str,
    ) -> None:
        visited: set[uuid.UUID] = set()
        active: set[uuid.UUID] = set()

        def visit(node: uuid.UUID, depth: int) -> None:
            if depth > _MAX_GRAPH_DEPTH:
                raise JobGraphError(f"Job {label} graph exceeds maximum depth {_MAX_GRAPH_DEPTH}.")
            if node in active:
                raise JobGraphError(f"Job {label} graph would contain a cycle.")
            if node in visited:
                return
            active.add(node)
            visited.add(node)
            if len(visited) > _MAX_GRAPH_NODES:
                raise JobGraphError(
                    f"Job {label} graph exceeds maximum traversal budget {_MAX_GRAPH_NODES}."
                )
            for target in adjacency.get(node, set()):
                visit(target, depth + 1)
            active.remove(node)

        visit(root, 0)

    def _cascade_children(
        self,
        connection: sqlite3.Connection,
        parent_job_id: uuid.UUID,
    ) -> tuple[uuid.UUID, ...]:
        rows = connection.execute(
            """
            SELECT job_id
            FROM job_parent_links
            WHERE parent_job_id = ? AND cancellation_policy = 'cascade'
            ORDER BY job_id
            """,
            (uuid_to_blob(parent_job_id),),
        ).fetchall()
        return tuple(uuid_from_blob(bytes(row["job_id"])) for row in rows)

    def _require_integrity(self, connection: sqlite3.Connection) -> None:
        dangling_dependency = connection.execute(
            """
            SELECT 1
            FROM job_dependencies AS d
            LEFT JOIN jobs AS child ON child.job_id = d.job_id
            LEFT JOIN jobs AS target ON target.job_id = d.depends_on_job_id
            WHERE child.job_id IS NULL OR target.job_id IS NULL OR d.job_id = d.depends_on_job_id
            LIMIT 1
            """
        ).fetchone()
        dangling_parent = connection.execute(
            """
            SELECT 1
            FROM job_parent_links AS l
            LEFT JOIN jobs AS child ON child.job_id = l.job_id
            LEFT JOIN jobs AS parent ON parent.job_id = l.parent_job_id
            WHERE child.job_id IS NULL OR parent.job_id IS NULL OR l.job_id = l.parent_job_id
            LIMIT 1
            """
        ).fetchone()
        if dangling_dependency is not None or dangling_parent is not None:
            raise JobGraphCorruptionError(
                "Persisted durable job graph contains a dangling or self-referential edge."
            )

    def _require_job(
        self,
        connection: sqlite3.Connection,
        job_id: uuid.UUID,
    ) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM jobs WHERE job_id = ?",
            (uuid_to_blob(job_id),),
        ).fetchone()
        if row is None:
            raise JobNotFoundError(str(job_id))
        return row

    def _require_graph_editable_job(
        self,
        connection: sqlite3.Connection,
        job_id: uuid.UUID,
    ) -> sqlite3.Row:
        row = self._require_job(connection, job_id)
        state = JobState(str(row["state"]))
        if state not in {JobState.QUEUED, JobState.WAITING, JobState.PAUSED}:
            raise JobGraphError(
                f"Job graph links cannot change while job {job_id} is {state.value!r}."
            )
        return row


def _normalized_ids(values: Iterable[uuid.UUID]) -> tuple[uuid.UUID, ...]:
    normalized: list[uuid.UUID] = []
    seen: set[uuid.UUID] = set()
    for value in values:
        if not isinstance(value, uuid.UUID):
            raise TypeError("Job dependency ids must be UUID values.")
        if value in seen:
            raise JobGraphError("Duplicate job dependencies are not permitted.")
        seen.add(value)
        normalized.append(value)
    if len(normalized) > _MAX_DIRECT_DEPENDENCIES:
        raise JobGraphError(
            f"A job may have at most {_MAX_DIRECT_DEPENDENCIES} direct dependencies."
        )
    return tuple(sorted(normalized, key=lambda item: item.bytes))


def _completion_policy(value: object) -> ParentCompletionPolicy:
    if not isinstance(value, ParentCompletionPolicy):
        raise TypeError("parent_completion_policy must be ParentCompletionPolicy.")
    return value


def _cancellation_policy(value: object) -> ChildCancellationPolicy:
    if not isinstance(value, ChildCancellationPolicy):
        raise TypeError("child_cancellation_policy must be ChildCancellationPolicy.")
    return value
