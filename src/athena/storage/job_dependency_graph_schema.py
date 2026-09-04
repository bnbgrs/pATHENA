"""Schema v41 for durable job dependencies and parent/child policy."""

from __future__ import annotations

import sqlite3

from athena.storage.schema_contract import (
    JOB_DEPENDENCY_GRAPH_MIGRATION_ID,
    JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION,
    GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION,
    STORAGE_LAYOUT_VERSION,
    BLOB_FORMAT_VERSION,
    DatabaseCompatibilityError,
    _user_tables,
)


def migrate_schema_v40_to_v41(connection: sqlite3.Connection) -> None:
    """Add explicit durable job graph edges without rewriting job payloads."""
    current = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if current != GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION:
        raise DatabaseCompatibilityError(
            "Job dependency graph migration requires canonical schema v40."
        )

    connection.executescript(
        f"""
        BEGIN IMMEDIATE;

        CREATE TABLE job_parent_links (
            job_id BLOB(16) PRIMARY KEY CHECK(length(job_id) = 16),
            parent_job_id BLOB(16) NOT NULL CHECK(length(parent_job_id) = 16),
            completion_policy TEXT NOT NULL CHECK(
                completion_policy IN ('independent', 'require_success')
            ),
            cancellation_policy TEXT NOT NULL CHECK(
                cancellation_policy IN ('independent', 'cascade')
            ),
            created_at_us INTEGER NOT NULL,
            CHECK(job_id != parent_job_id),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id),
            FOREIGN KEY(parent_job_id) REFERENCES jobs(job_id)
        ) WITHOUT ROWID;

        CREATE INDEX idx_job_parent_links_parent
            ON job_parent_links(parent_job_id, job_id);

        CREATE TABLE job_dependencies (
            job_id BLOB(16) NOT NULL CHECK(length(job_id) = 16),
            depends_on_job_id BLOB(16) NOT NULL CHECK(length(depends_on_job_id) = 16),
            created_at_us INTEGER NOT NULL,
            PRIMARY KEY(job_id, depends_on_job_id),
            CHECK(job_id != depends_on_job_id),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id),
            FOREIGN KEY(depends_on_job_id) REFERENCES jobs(job_id)
        ) WITHOUT ROWID;

        CREATE INDEX idx_job_dependencies_depends_on
            ON job_dependencies(depends_on_job_id, job_id);

        UPDATE schema_metadata
        SET schema_version = {JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION},
            last_migration_id = '{JOB_DEPENDENCY_GRAPH_MIGRATION_ID}',
            minimum_reader_version = {JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION}
        WHERE singleton_id = 1;

        PRAGMA user_version = {JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION};
        COMMIT;
        """
    )


def verify_schema_v41(connection: sqlite3.Connection) -> None:
    """Fail closed if the v41 graph schema or migration metadata drifted."""
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if user_version != JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION:
        raise DatabaseCompatibilityError(
            "ATHENA job dependency graph schema version verification failed."
        )

    metadata = connection.execute(
        """
        SELECT schema_version, storage_layout_version, blob_format_version,
               last_migration_id, minimum_reader_version
        FROM schema_metadata
        WHERE singleton_id = 1
        """
    ).fetchone()
    expected = (
        JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION,
        STORAGE_LAYOUT_VERSION,
        BLOB_FORMAT_VERSION,
        JOB_DEPENDENCY_GRAPH_MIGRATION_ID,
        JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION,
    )
    if metadata is None or tuple(metadata) != expected:
        raise DatabaseCompatibilityError(
            "ATHENA job dependency graph schema_metadata verification failed."
        )

    required_tables = {"job_parent_links", "job_dependencies"}
    missing = required_tables.difference(_user_tables(connection))
    if missing:
        raise DatabaseCompatibilityError(
            "ATHENA job dependency graph schema is incomplete: "
            + ", ".join(sorted(missing))
            + "."
        )

    parent_columns = {
        str(row[1]) for row in connection.execute("PRAGMA table_info(job_parent_links)")
    }
    if not {
        "job_id",
        "parent_job_id",
        "completion_policy",
        "cancellation_policy",
        "created_at_us",
    }.issubset(parent_columns):
        raise DatabaseCompatibilityError("ATHENA job parent-link schema is incomplete.")

    dependency_columns = {
        str(row[1]) for row in connection.execute("PRAGMA table_info(job_dependencies)")
    }
    if not {"job_id", "depends_on_job_id", "created_at_us"}.issubset(
        dependency_columns
    ):
        raise DatabaseCompatibilityError("ATHENA job dependency schema is incomplete.")

    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise DatabaseCompatibilityError(
            "ATHENA job dependency graph foreign-key verification failed."
        )
