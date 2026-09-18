from __future__ import annotations

import uuid

import pytest

from athena.jobs.dependency_graph import (
    JobDependencyCycleError,
    JobDependencyDanglingError,
    JobDependencyTraversalLimitError,
    validate_dependency_insertion,
)


def _id(value: int) -> uuid.UUID:
    return uuid.UUID(int=value)


def test_dependency_insertion_accepts_acyclic_existing_graph() -> None:
    graph = {_id(2): (_id(3),), _id(3): ()}
    existing = {_id(1), _id(2), _id(3)}
    validate_dependency_insertion(
        job_id=_id(1),
        dependency_id=_id(2),
        dependencies_of=lambda job_id: graph.get(job_id, ()),
        job_exists=lambda job_id: job_id in existing,
    )


def test_dependency_insertion_rejects_cycle() -> None:
    graph = {_id(2): (_id(3),), _id(3): (_id(1),)}
    existing = {_id(1), _id(2), _id(3)}
    with pytest.raises(JobDependencyCycleError):
        validate_dependency_insertion(
            job_id=_id(1),
            dependency_id=_id(2),
            dependencies_of=lambda job_id: graph.get(job_id, ()),
            job_exists=lambda job_id: job_id in existing,
        )


def test_dependency_insertion_rejects_dangling_edge() -> None:
    with pytest.raises(JobDependencyDanglingError):
        validate_dependency_insertion(
            job_id=_id(1),
            dependency_id=_id(2),
            dependencies_of=lambda _job_id: (),
            job_exists=lambda job_id: job_id == _id(1),
        )


def test_dependency_insertion_rejects_bounded_traversal_overflow() -> None:
    graph = {_id(2): (_id(3),), _id(3): (_id(4),), _id(4): ()}
    existing = {_id(1), _id(2), _id(3), _id(4)}
    with pytest.raises(JobDependencyTraversalLimitError):
        validate_dependency_insertion(
            job_id=_id(1),
            dependency_id=_id(2),
            dependencies_of=lambda job_id: graph.get(job_id, ()),
            job_exists=lambda job_id: job_id in existing,
            max_nodes=2,
        )
