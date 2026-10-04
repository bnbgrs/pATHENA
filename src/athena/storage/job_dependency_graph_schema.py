"""Schema v42 for durable job dependencies and parent/child policy."""

from __future__ import annotations

import sqlite3

from athena.storage import schema_contract

_GRAPH_TABLES = frozenset({"job_parent_links", "job_dependencies"})
_PARENT_COLUMNS = (
    "job_id",
    "parent_job_id",
    "completion_policy",
    "cancellation_policy",
    "created_at_us",
)
_DEPENDENCY_COLUMNS = ("job_id", "depends_on_job_id", "created_at_us")


def _verify_compatible_existing_graph_tables(connection: sqlite3.Connection) -> None:
    """Accept only a complete canonical partial v42 graph schema."""
    present = _GRAPH_TABLES.intersection(schema_contract._user_tables(connection))
    if not present:
        return
    if present != _GRAPH_TABLES:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job dependency graph migration found an incomplete partial schema."
        )

    parent_columns = tuple(
        str(row[1])
        for row in connection.execute("PRAGMA table_info(job_parent_links)").fetchall()
    )
    dependency_columns = tuple(
        str(row[1])
        for row in connection.execute("PRAGMA table_info(job_dependencies)").fetchall()
    )
    if parent_columns != _PARENT_COLUMNS:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job parent-link partial schema is incompatible."
        )
    if dependency_columns != _DEPENDENCY_COLUMNS:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job dependency partial schema is incompatible."
        )

    parent_foreign_keys = {
        (str(row[2]), str(row[3]), str(row[4]))
        for row in connection.execute(
            "PRAGMA foreign_key_list(job_parent_links)"
        ).fetchall()
    }
    expected_parent_foreign_keys = {
        ("jobs", "job_id", "job_id"),
        ("jobs", "parent_job_id", "job_id"),
    }
    if not expected_parent_foreign_keys.issubset(parent_foreign_keys):
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job parent-link partial foreign keys are incompatible."
        )

    dependency_foreign_keys = {
        (str(row[2]), str(row[3]), str(row[4]))
        for row in connection.execute(
            "PRAGMA foreign_key_list(job_dependencies)"
        ).fetchall()
    }
    expected_dependency_foreign_keys = {
        ("jobs", "job_id", "job_id"),
        ("jobs", "depends_on_job_id", "job_id"),
    }
    if not expected_dependency_foreign_keys.issubset(dependency_foreign_keys):
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job dependency partial foreign keys are incompatible."
        )


def migrate_schema_v41_to_v42(connection: sqlite3.Connection) -> None:
    """Add explicit durable job graph edges without rewriting job payloads."""
    current = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if current != schema_contract.STRUCTURED_REPLICATION_SCHEMA_VERSION:
        raise schema_contract.DatabaseCompatibilityError(
            "Job dependency graph migration requires canonical schema v41."
        )

    _verify_compatible_existing_graph_tables(connection)

    connection.executescript(
        f"""
        BEGIN IMMEDIATE;

        CREATE TABLE IF NOT EXISTS job_parent_links (
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

        CREATE INDEX IF NOT EXISTS idx_job_parent_links_parent
            ON job_parent_links(parent_job_id, job_id);

        CREATE TABLE IF NOT EXISTS job_dependencies (
            job_id BLOB(16) NOT NULL CHECK(length(job_id) = 16),
            depends_on_job_id BLOB(16) NOT NULL CHECK(length(depends_on_job_id) = 16),
            created_at_us INTEGER NOT NULL,
            PRIMARY KEY(job_id, depends_on_job_id),
            CHECK(job_id != depends_on_job_id),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id),
            FOREIGN KEY(depends_on_job_id) REFERENCES jobs(job_id)
        ) WITHOUT ROWID;

        CREATE INDEX IF NOT EXISTS idx_job_dependencies_depends_on
            ON job_dependencies(depends_on_job_id, job_id);

        UPDATE schema_metadata
        SET schema_version = {schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION},
            last_migration_id = '{schema_contract.JOB_DEPENDENCY_GRAPH_MIGRATION_ID}',
            minimum_reader_version = {schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION}
        WHERE singleton_id = 1;

        PRAGMA user_version = {schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION};
        COMMIT;
        """
    )


def verify_schema_v42(connection: sqlite3.Connection) -> None:
    """Fail closed if the v42 graph schema or migration metadata drifted."""
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if user_version != schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION:
        raise schema_contract.DatabaseCompatibilityError(
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
        schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION,
        schema_contract.STORAGE_LAYOUT_VERSION,
        schema_contract.BLOB_FORMAT_VERSION,
        schema_contract.JOB_DEPENDENCY_GRAPH_MIGRATION_ID,
        schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION,
    )
    if metadata is None or tuple(metadata) != expected:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job dependency graph schema_metadata verification failed."
        )

    required_tables = {"job_parent_links", "job_dependencies"}
    missing = required_tables.difference(schema_contract._user_tables(connection))
    if missing:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job dependency graph schema is incomplete: "
            + ", ".join(sorted(missing))
            + "."
        )

    parent_columns = tuple(
        str(row[1])
        for row in connection.execute("PRAGMA table_info(job_parent_links)").fetchall()
    )
    if parent_columns != _PARENT_COLUMNS:
        raise schema_contract.DatabaseCompatibilityError("ATHENA job parent-link schema is incomplete.")

    dependency_columns = tuple(
        str(row[1])
        for row in connection.execute("PRAGMA table_info(job_dependencies)").fetchall()
    )
    if dependency_columns != _DEPENDENCY_COLUMNS:
        raise schema_contract.DatabaseCompatibilityError("ATHENA job dependency schema is incomplete.")

    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA job dependency graph foreign-key verification failed."
        )
