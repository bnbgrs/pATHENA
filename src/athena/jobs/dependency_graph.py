"""Bounded fail-closed validation for durable job dependency edges."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Iterable


class JobDependencyGraphError(RuntimeError):
    """Raised when a durable dependency graph cannot be accepted safely."""


class JobDependencyCycleError(JobDependencyGraphError):
    """Raised when adding a dependency would create a cycle."""


class JobDependencyDanglingError(JobDependencyGraphError):
    """Raised when a dependency points at a job that does not exist."""


class JobDependencyTraversalLimitError(JobDependencyGraphError):
    """Raised before dependency traversal can exceed its configured bound."""


def validate_dependency_insertion(
    *,
    job_id: uuid.UUID,
    dependency_id: uuid.UUID,
    dependencies_of: Callable[[uuid.UUID], Iterable[uuid.UUID]],
    job_exists: Callable[[uuid.UUID], bool],
    max_nodes: int = 256,
) -> None:
    """Validate one edge without accepting cycles, dangling nodes, or unbounded work.

    The proposed edge is ``job_id -> dependency_id``. Traversal follows existing
    dependency edges from ``dependency_id`` and rejects the insertion if it can
    reach ``job_id``. Every visited node must exist. The bound is checked before
    expanding another node so corrupt or adversarial graphs fail closed.
    """
    if max_nodes <= 0:
        raise ValueError("max_nodes must be positive.")
    if job_id == dependency_id:
        raise JobDependencyCycleError("A job cannot depend on itself.")
    if not job_exists(job_id):
        raise JobDependencyDanglingError(f"Missing job: {job_id}")
    if not job_exists(dependency_id):
        raise JobDependencyDanglingError(f"Missing dependency: {dependency_id}")

    pending = [dependency_id]
    visited: set[uuid.UUID] = set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        if len(visited) >= max_nodes:
            raise JobDependencyTraversalLimitError(
                f"Dependency traversal exceeds {max_nodes} nodes."
            )
        if not job_exists(current):
            raise JobDependencyDanglingError(f"Missing dependency node: {current}")
        visited.add(current)
        for child in dependencies_of(current):
            if child == job_id:
                raise JobDependencyCycleError("Dependency insertion would create a cycle.")
            if child not in visited:
                pending.append(child)


def inherited_priority(
    *,
    job_id: uuid.UUID,
    priority_of: Callable[[uuid.UUID], int],
    dependents_of: Callable[[uuid.UUID], Iterable[uuid.UUID]],
    job_exists: Callable[[uuid.UUID], bool],
    max_nodes: int = 256,
) -> int:
    """Return the highest urgency inherited from bounded transitive dependents.

    Smaller numeric priorities are more urgent. Traversal starts at ``job_id``
    and follows reverse dependency edges (jobs waiting on the current node).
    Missing nodes and over-bound graphs fail closed instead of silently changing
    scheduler ordering.
    """
    if max_nodes <= 0:
        raise ValueError("max_nodes must be positive.")
    if not job_exists(job_id):
        raise JobDependencyDanglingError(f"Missing job: {job_id}")

    pending = [job_id]
    visited: set[uuid.UUID] = set()
    effective: int | None = None
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        if len(visited) >= max_nodes:
            raise JobDependencyTraversalLimitError(
                f"Priority inheritance traversal exceeds {max_nodes} nodes."
            )
        if not job_exists(current):
            raise JobDependencyDanglingError(f"Missing dependent node: {current}")
        priority = priority_of(current)
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise TypeError("Job priority must be an integer.")
        visited.add(current)
        effective = priority if effective is None else min(effective, priority)
        for dependent in dependents_of(current):
            if dependent not in visited:
                pending.append(dependent)

    if effective is None:
        raise JobDependencyGraphError("Priority inheritance produced no job nodes.")
    return effective
