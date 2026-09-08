"""Durable lower-bound identity for reproducible Delta Research scopes."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass

from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.research.errors import ResearchNotFoundError, ResearchStateError
from athena.research.models import ResearchMode, ResearchScopeState
from athena.storage.database import SQLiteDatabase


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")
    return value


@dataclass(frozen=True, slots=True)
class ResearchDeltaBoundaryRecord:
    """Persisted identity of the completed snapshot that bounds one Delta scope."""

    scope_id: uuid.UUID
    base_scope_id: uuid.UUID
    lower_commit_seq: int
    created_at_us: int

    def __post_init__(self) -> None:
        if not isinstance(self.scope_id, uuid.UUID):
            raise TypeError("Research Delta boundary scope_id must be a UUID.")
        if not isinstance(self.base_scope_id, uuid.UUID):
            raise TypeError("Research Delta boundary base_scope_id must be a UUID.")
        if self.scope_id == self.base_scope_id:
            raise ValueError("Research Delta scope cannot use itself as its baseline.")
        _nonnegative_int(
            self.lower_commit_seq,
            "Research Delta boundary lower_commit_seq",
        )
        _nonnegative_int(self.created_at_us, "Research Delta boundary created_at_us")


def _delta_boundary_from_row(row: sqlite3.Row) -> ResearchDeltaBoundaryRecord:
    return ResearchDeltaBoundaryRecord(
        scope_id=uuid_from_blob(bytes(row["scope_id"])),
        base_scope_id=uuid_from_blob(bytes(row["base_scope_id"])),
        lower_commit_seq=int(row["lower_commit_seq"]),
        created_at_us=int(row["created_at_us"]),
    )


class ResearchDeltaBoundaryRepository:
    """Persist and recover exact lower bounds without wall-clock inference."""

    def __init__(self, database: SQLiteDatabase) -> None:
        if not isinstance(database, SQLiteDatabase):
            raise TypeError("Research Delta boundary repository requires SQLiteDatabase.")
        self.database = database

    def get(self, scope_id: uuid.UUID) -> ResearchDeltaBoundaryRecord | None:
        if not isinstance(scope_id, uuid.UUID):
            raise TypeError("Research Delta boundary scope_id must be a UUID.")
        row = self.database.connection.execute(
            "SELECT * FROM research_delta_boundaries WHERE scope_id = ?",
            (uuid_to_blob(scope_id),),
        ).fetchone()
        return None if row is None else _delta_boundary_from_row(row)

    def persist(
        self,
        *,
        scope_id: uuid.UUID,
        base_scope_id: uuid.UUID,
        lower_commit_seq: int,
    ) -> ResearchDeltaBoundaryRecord:
        """Bind a Delta scope to one completed baseline, fail-before-write on mismatch."""
        if not isinstance(scope_id, uuid.UUID):
            raise TypeError("Research Delta boundary scope_id must be a UUID.")
        if not isinstance(base_scope_id, uuid.UUID):
            raise TypeError("Research Delta boundary base_scope_id must be a UUID.")
        lower_commit_seq = _nonnegative_int(
            lower_commit_seq,
            "Research Delta boundary lower_commit_seq",
        )
        if scope_id == base_scope_id:
            raise ValueError("Research Delta scope cannot use itself as its baseline.")

        now_us = utc_now_us()
        with self.database.write_transaction() as connection:
            delta_scope = connection.execute(
                "SELECT mode, snapshot_commit_seq FROM research_scopes WHERE scope_id = ?",
                (uuid_to_blob(scope_id),),
            ).fetchone()
            if delta_scope is None:
                raise ResearchNotFoundError(f"Research Delta scope {scope_id} does not exist.")

            base_scope = connection.execute(
                "SELECT state, snapshot_commit_seq FROM research_scopes WHERE scope_id = ?",
                (uuid_to_blob(base_scope_id),),
            ).fetchone()
            if base_scope is None:
                raise ResearchNotFoundError(
                    f"Research Delta baseline scope {base_scope_id} does not exist."
                )

            if ResearchMode(str(delta_scope["mode"])) is not ResearchMode.DELTA:
                raise ResearchStateError(
                    "Research Delta boundary can only be attached to a delta scope."
                )
            if ResearchScopeState(str(base_scope["state"])) is not ResearchScopeState.COMPLETED:
                raise ResearchStateError(
                    "Research Delta baseline scope must be completed."
                )

            base_snapshot = int(base_scope["snapshot_commit_seq"])
            upper_snapshot = int(delta_scope["snapshot_commit_seq"])
            if lower_commit_seq != base_snapshot:
                raise ResearchStateError(
                    "Research Delta lower commit must equal the persisted baseline snapshot."
                )
            if lower_commit_seq > upper_snapshot:
                raise ResearchStateError(
                    "Research Delta lower commit cannot exceed the delta upper snapshot."
                )

            existing = connection.execute(
                "SELECT * FROM research_delta_boundaries WHERE scope_id = ?",
                (uuid_to_blob(scope_id),),
            ).fetchone()
            if existing is not None:
                existing_record = _delta_boundary_from_row(existing)
                if (
                    existing_record.base_scope_id != base_scope_id
                    or existing_record.lower_commit_seq != lower_commit_seq
                ):
                    raise ResearchStateError(
                        "Research Delta boundary is already bound to different provenance."
                    )
                return existing_record

            connection.execute(
                """
                INSERT INTO research_delta_boundaries (
                    scope_id, base_scope_id, lower_commit_seq, created_at_us
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(scope_id),
                    uuid_to_blob(base_scope_id),
                    lower_commit_seq,
                    now_us,
                ),
            )

        durable_record = self.get(scope_id)
        if durable_record is None:
            raise ResearchStateError("Research Delta boundary persistence was not durable.")
        return durable_record
