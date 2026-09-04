"""ATHENA SQLite schema bootstrap, additive migrations, and compatibility checks."""

from __future__ import annotations

import sqlite3

from athena.news.schema import (
    migrate_news_schema_v25_to_v26,
    migrate_news_schema_v26_to_v27,
    migrate_news_schema_v27_to_v28,
    migrate_news_schema_v29_to_v30,
)
from athena.storage.archive_replication_migration import (
    migrate_schema_v30_to_v31_restart_safe as _migrate_schema_v30_to_v31,
)
from athena.storage.job_dependency_graph_schema import (
    migrate_schema_v40_to_v41 as _migrate_schema_v40_to_v41,
    verify_schema_v41 as _verify_schema_v41,
)
from athena.storage.schema_contract import *  # noqa: F403
from athena.storage.schema_contract import _user_tables as _user_tables
from athena.storage.schema_error_sanitization import (
    _PERSISTED_ERROR_CHECKPOINT_JOB_TYPES as _PERSISTED_ERROR_CHECKPOINT_JOB_TYPES,
    _PERSISTED_ERROR_CODE_RE as _PERSISTED_ERROR_CODE_RE,
    _PERSISTED_ERROR_SCALAR_FIELDS as _PERSISTED_ERROR_SCALAR_FIELDS,
    _canonical_migration_json as _canonical_migration_json,
    _sanitize_checkpoint_error_payload as _sanitize_checkpoint_error_payload,
    _sanitize_persisted_error_value as _sanitize_persisted_error_value,
)
from athena.storage.schema_evolution import (
    _create_schema_v1,
    _migrate_schema_v1_to_v2,
    _migrate_schema_v2_to_v3,
    _migrate_schema_v3_to_v4,
    _migrate_schema_v4_to_v5,
    _migrate_schema_v5_to_v6,
    _migrate_schema_v6_to_v7,
    _migrate_schema_v7_to_v8,
    _migrate_schema_v8_to_v9,
    _migrate_schema_v9_to_v10,
    _migrate_schema_v10_to_v11,
    _migrate_schema_v11_to_v12,
    _migrate_schema_v12_to_v13,
    _migrate_schema_v13_to_v14,
    _migrate_schema_v14_to_v15,
    _migrate_schema_v15_to_v16,
    _migrate_schema_v16_to_v17,
    _migrate_schema_v17_to_v18,
    _migrate_schema_v18_to_v19,
    _migrate_schema_v19_to_v20,
    _migrate_schema_v20_to_v21,
    _migrate_schema_v21_to_v22,
    _migrate_schema_v22_to_v23,
    _migrate_schema_v23_to_v24,
    _migrate_schema_v24_to_v25,
    _migrate_schema_v28_to_v29,
    _migrate_schema_v31_to_v32,
    _migrate_schema_v32_to_v33,
    _migrate_schema_v33_to_v34,
    _migrate_schema_v34_to_v35,
    _migrate_schema_v35_to_v36,
    _migrate_schema_v36_to_v37,
    _migrate_schema_v38_to_v39,
    _migrate_schema_v39_to_v40,
)
from athena.storage.schema_verification import (
    _verify_schema_v15,
    _verify_schema_v16,
    _verify_schema_v17,
    _verify_schema_v18,
    _verify_schema_v19,
    _verify_schema_v20,
    _verify_schema_v21,
    _verify_schema_v22,
    _verify_schema_v23,
    _verify_schema_v24,
    _verify_schema_v24_compatible,
    _verify_schema_v25,
    _verify_schema_v26,
    _verify_schema_v27,
    _verify_schema_v28,
    _verify_schema_v29,
    _verify_schema_v30,
    _verify_schema_v31,
    _verify_schema_v31_compatible,
    _verify_schema_v32,
    _verify_schema_v33,
    _verify_schema_v34,
    _verify_schema_v35,
    _verify_schema_v36,
    _verify_schema_v37,
    _verify_schema_v38,
    _verify_schema_v39,
    _verify_schema_v40,
)


def _configure_connection(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    mode = str(connection.execute("PRAGMA journal_mode = WAL").fetchone()[0]).lower()
    if mode != "wal":
        raise DatabaseCompatibilityError(  # noqa: F405
            f"ATHENA requires SQLite WAL mode, but SQLite returned {mode!r}."
        )
    connection.execute("PRAGMA synchronous = FULL")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA secure_delete = ON")
    connection.execute("PRAGMA read_uncommitted = OFF")
    connection.execute("PRAGMA wal_autocheckpoint = 1000")
    connection.execute("PRAGMA trusted_schema = OFF")


def initialize_schema(connection: sqlite3.Connection, *, created_at_us: int) -> None:
    """Validate, initialize, or safely advance the ATHENA SQLite schema."""
    existing_application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
    existing_user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    tables = _user_tables(connection)

    if existing_application_id not in {0, ATHENA_APPLICATION_ID}:  # noqa: F405
        raise DatabaseCompatibilityError(  # noqa: F405
            "Database application_id does not belong to ATHENA."
        )
    if existing_application_id == 0 and tables:
        raise DatabaseCompatibilityError(  # noqa: F405
            "Refusing to adopt a non-empty SQLite database without ATHENA application_id."
        )
    if existing_user_version > SCHEMA_VERSION:  # noqa: F405
        raise DatabaseCompatibilityError(  # noqa: F405
            f"Database schema version {existing_user_version} is newer than supported "
            f"version {SCHEMA_VERSION}."  # noqa: F405
        )

    supported_versions = {
        0,
        LEGACY_SCHEMA_VERSION,
        KNOWLEDGE_SCHEMA_VERSION,
        PROVENANCE_SCHEMA_VERSION,
        MODEL_RUNS_SCHEMA_VERSION,
        REVIEW_QUEUE_SCHEMA_VERSION,
        MERGE_REVIEW_SCHEMA_VERSION,
        MERGE_REVIEW_MULTI_TARGET_SCHEMA_VERSION,
        EXTRACTION_SNAPSHOT_SCHEMA_VERSION,
        LOCAL_FTS_SCHEMA_VERSION,
        LOCAL_EMBEDDINGS_SCHEMA_VERSION,
        SOURCE_CAPTURE_SCHEMA_VERSION,
        SOURCE_REPRESENTATION_SCHEMA_VERSION,
        SOURCE_CHUNK_PROFILE_SCHEMA_VERSION,
        SOURCE_ANCHOR_SCHEMA_VERSION,
        DURABLE_JOBS_SCHEMA_VERSION,
        SOURCE_PAGE_MAP_SCHEMA_VERSION,
        SOURCE_DOCUMENT_STRUCTURE_SCHEMA_VERSION,
        SOURCE_ANALYSIS_SCHEMA_VERSION,
        SOURCE_KNOWLEDGE_SCHEMA_VERSION,
        HIERARCHICAL_SOURCE_EXTRACTION_SCHEMA_VERSION,
        PERSONAL_MEMORY_SCHEMA_VERSION,
        EXHAUSTIVE_RESEARCH_SCHEMA_VERSION,
        RESEARCH_ORCHESTRATION_SCHEMA_VERSION,
        RESEARCH_SYNTHESIS_SCHEMA_VERSION,
        CONSOLIDATED_OPERATIONS_SCHEMA_VERSION,
        NEWS_SYSTEM_SCHEMA_VERSION,
        NEWS_EVENT_STRUCTURE_SCHEMA_VERSION,
        NEWS_OPERATIONAL_SCHEMA_VERSION,
        PRECISE_RESEARCH_PROVENANCE_SCHEMA_VERSION,
        NEWS_EVENT_ELIGIBILITY_SCHEMA_VERSION,
        ARCHIVE_REPLICATION_SCHEMA_VERSION,
        PROTECTED_CONTENT_SCHEMA_VERSION,
        PROTECTED_SOURCE_BLOB_SCHEMA_VERSION,
        SOURCE_PROTECTION_TRANSITION_SCHEMA_VERSION,
        BACKUP_RETENTION_SCHEMA_VERSION,
        DELETION_LEDGER_SCHEMA_VERSION,
        OPERATIONAL_ERROR_SANITIZATION_SCHEMA_VERSION,
        OPERATIONAL_ERROR_PHYSICAL_CLEANUP_SCHEMA_VERSION,
        PROTECTED_SOURCE_SEMANTIC_SCHEMA_VERSION,
        GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION,
        JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION,
    }
    if existing_user_version not in supported_versions:
        raise DatabaseCompatibilityError(  # noqa: F405
            f"Database schema version {existing_user_version} requires an unsupported "
            "migration path."
        )

    if existing_user_version == 0:
        connection.execute("PRAGMA auto_vacuum = INCREMENTAL")
        connection.execute(f"PRAGMA application_id = {ATHENA_APPLICATION_ID}")  # noqa: F405
        _create_schema_v1(connection, created_at_us=created_at_us)
        existing_user_version = LEGACY_SCHEMA_VERSION
    if existing_user_version == LEGACY_SCHEMA_VERSION:
        _migrate_schema_v1_to_v2(connection)
        existing_user_version = KNOWLEDGE_SCHEMA_VERSION
    if existing_user_version == KNOWLEDGE_SCHEMA_VERSION:
        _migrate_schema_v2_to_v3(connection)
        existing_user_version = PROVENANCE_SCHEMA_VERSION
    if existing_user_version == PROVENANCE_SCHEMA_VERSION:
        _migrate_schema_v3_to_v4(connection)
        existing_user_version = MODEL_RUNS_SCHEMA_VERSION
    if existing_user_version == MODEL_RUNS_SCHEMA_VERSION:
        _migrate_schema_v4_to_v5(connection)
        existing_user_version = REVIEW_QUEUE_SCHEMA_VERSION
    if existing_user_version == REVIEW_QUEUE_SCHEMA_VERSION:
        _migrate_schema_v5_to_v6(connection)
        existing_user_version = MERGE_REVIEW_SCHEMA_VERSION
    if existing_user_version == MERGE_REVIEW_SCHEMA_VERSION:
        _migrate_schema_v6_to_v7(connection)
        existing_user_version = MERGE_REVIEW_MULTI_TARGET_SCHEMA_VERSION
    if existing_user_version == MERGE_REVIEW_MULTI_TARGET_SCHEMA_VERSION:
        _migrate_schema_v7_to_v8(connection)
        existing_user_version = EXTRACTION_SNAPSHOT_SCHEMA_VERSION
    if existing_user_version == EXTRACTION_SNAPSHOT_SCHEMA_VERSION:
        _migrate_schema_v8_to_v9(connection)
        existing_user_version = LOCAL_FTS_SCHEMA_VERSION
    if existing_user_version == LOCAL_FTS_SCHEMA_VERSION:
        _migrate_schema_v9_to_v10(connection)
        existing_user_version = LOCAL_EMBEDDINGS_SCHEMA_VERSION
    if existing_user_version == LOCAL_EMBEDDINGS_SCHEMA_VERSION:
        _migrate_schema_v10_to_v11(connection)
        existing_user_version = SOURCE_CAPTURE_SCHEMA_VERSION
    if existing_user_version == SOURCE_CAPTURE_SCHEMA_VERSION:
        _migrate_schema_v11_to_v12(connection)
        existing_user_version = SOURCE_REPRESENTATION_SCHEMA_VERSION
    if existing_user_version == SOURCE_REPRESENTATION_SCHEMA_VERSION:
        _migrate_schema_v12_to_v13(connection)
        existing_user_version = SOURCE_CHUNK_PROFILE_SCHEMA_VERSION
    if existing_user_version == SOURCE_CHUNK_PROFILE_SCHEMA_VERSION:
        _migrate_schema_v13_to_v14(connection)
        existing_user_version = SOURCE_ANCHOR_SCHEMA_VERSION
    if existing_user_version == SOURCE_ANCHOR_SCHEMA_VERSION:
        _migrate_schema_v14_to_v15(connection)
        existing_user_version = DURABLE_JOBS_SCHEMA_VERSION
    if existing_user_version == DURABLE_JOBS_SCHEMA_VERSION:
        _migrate_schema_v15_to_v16(connection)
        existing_user_version = SOURCE_PAGE_MAP_SCHEMA_VERSION
    if existing_user_version == SOURCE_PAGE_MAP_SCHEMA_VERSION:
        _migrate_schema_v16_to_v17(connection)
        existing_user_version = SOURCE_DOCUMENT_STRUCTURE_SCHEMA_VERSION
    if existing_user_version == SOURCE_DOCUMENT_STRUCTURE_SCHEMA_VERSION:
        _migrate_schema_v17_to_v18(connection)
        existing_user_version = SOURCE_ANALYSIS_SCHEMA_VERSION
    if existing_user_version == SOURCE_ANALYSIS_SCHEMA_VERSION:
        _migrate_schema_v18_to_v19(connection)
        existing_user_version = SOURCE_KNOWLEDGE_SCHEMA_VERSION
    if existing_user_version == SOURCE_KNOWLEDGE_SCHEMA_VERSION:
        _migrate_schema_v19_to_v20(connection)
        existing_user_version = HIERARCHICAL_SOURCE_EXTRACTION_SCHEMA_VERSION
    if existing_user_version == HIERARCHICAL_SOURCE_EXTRACTION_SCHEMA_VERSION:
        _migrate_schema_v20_to_v21(connection)
        existing_user_version = PERSONAL_MEMORY_SCHEMA_VERSION
    if existing_user_version == PERSONAL_MEMORY_SCHEMA_VERSION:
        _migrate_schema_v21_to_v22(connection)
        existing_user_version = EXHAUSTIVE_RESEARCH_SCHEMA_VERSION
    if existing_user_version == EXHAUSTIVE_RESEARCH_SCHEMA_VERSION:
        _migrate_schema_v22_to_v23(connection)
        existing_user_version = RESEARCH_ORCHESTRATION_SCHEMA_VERSION
    if existing_user_version == RESEARCH_ORCHESTRATION_SCHEMA_VERSION:
        _migrate_schema_v23_to_v24(connection)
        existing_user_version = RESEARCH_SYNTHESIS_SCHEMA_VERSION
    if existing_user_version == RESEARCH_SYNTHESIS_SCHEMA_VERSION:
        _migrate_schema_v24_to_v25(connection)
        existing_user_version = CONSOLIDATED_OPERATIONS_SCHEMA_VERSION
    if existing_user_version == CONSOLIDATED_OPERATIONS_SCHEMA_VERSION:
        migrate_news_schema_v25_to_v26(
            connection,
            schema_version=NEWS_SYSTEM_SCHEMA_VERSION,
            migration_id=NEWS_SYSTEM_MIGRATION_ID,
        )
        existing_user_version = NEWS_SYSTEM_SCHEMA_VERSION
    if existing_user_version == NEWS_SYSTEM_SCHEMA_VERSION:
        migrate_news_schema_v26_to_v27(
            connection,
            schema_version=NEWS_EVENT_STRUCTURE_SCHEMA_VERSION,
            migration_id=NEWS_EVENT_STRUCTURE_MIGRATION_ID,
        )
        existing_user_version = NEWS_EVENT_STRUCTURE_SCHEMA_VERSION
    if existing_user_version == NEWS_EVENT_STRUCTURE_SCHEMA_VERSION:
        migrate_news_schema_v27_to_v28(
            connection,
            schema_version=NEWS_OPERATIONAL_SCHEMA_VERSION,
            migration_id=NEWS_OPERATIONAL_MIGRATION_ID,
        )
        existing_user_version = NEWS_OPERATIONAL_SCHEMA_VERSION
    if existing_user_version == NEWS_OPERATIONAL_SCHEMA_VERSION:
        _migrate_schema_v28_to_v29(connection)
        existing_user_version = PRECISE_RESEARCH_PROVENANCE_SCHEMA_VERSION
    if existing_user_version == PRECISE_RESEARCH_PROVENANCE_SCHEMA_VERSION:
        _verify_schema_v29(connection)
        migrate_news_schema_v29_to_v30(
            connection,
            schema_version=NEWS_EVENT_ELIGIBILITY_SCHEMA_VERSION,
            migration_id=NEWS_EVENT_ELIGIBILITY_MIGRATION_ID,
        )
        existing_user_version = NEWS_EVENT_ELIGIBILITY_SCHEMA_VERSION
    if existing_user_version == NEWS_EVENT_ELIGIBILITY_SCHEMA_VERSION:
        _verify_schema_v30(connection)
        _migrate_schema_v30_to_v31(connection)
        existing_user_version = ARCHIVE_REPLICATION_SCHEMA_VERSION
    if existing_user_version == ARCHIVE_REPLICATION_SCHEMA_VERSION:
        _verify_schema_v31(connection)
        _migrate_schema_v31_to_v32(connection)
        existing_user_version = PROTECTED_CONTENT_SCHEMA_VERSION
    if existing_user_version == PROTECTED_CONTENT_SCHEMA_VERSION:
        _verify_schema_v32(connection)
        _migrate_schema_v32_to_v33(connection)
        existing_user_version = PROTECTED_SOURCE_BLOB_SCHEMA_VERSION
    if existing_user_version == PROTECTED_SOURCE_BLOB_SCHEMA_VERSION:
        _verify_schema_v33(connection)
        _migrate_schema_v33_to_v34(connection)
        existing_user_version = SOURCE_PROTECTION_TRANSITION_SCHEMA_VERSION
    if existing_user_version == SOURCE_PROTECTION_TRANSITION_SCHEMA_VERSION:
        _verify_schema_v34(connection)
        _migrate_schema_v34_to_v35(connection)
        existing_user_version = BACKUP_RETENTION_SCHEMA_VERSION
    if existing_user_version == BACKUP_RETENTION_SCHEMA_VERSION:
        _verify_schema_v35(connection)
        _migrate_schema_v35_to_v36(connection)
        existing_user_version = DELETION_LEDGER_SCHEMA_VERSION
    if existing_user_version == DELETION_LEDGER_SCHEMA_VERSION:
        _verify_schema_v36(connection)
        _migrate_schema_v36_to_v37(connection)
        existing_user_version = OPERATIONAL_ERROR_SANITIZATION_SCHEMA_VERSION
    if existing_user_version == OPERATIONAL_ERROR_SANITIZATION_SCHEMA_VERSION:
        _verify_schema_v37(connection)
        _migrate_schema_v37_to_v38(connection)
        existing_user_version = OPERATIONAL_ERROR_PHYSICAL_CLEANUP_SCHEMA_VERSION
    if existing_user_version == OPERATIONAL_ERROR_PHYSICAL_CLEANUP_SCHEMA_VERSION:
        _verify_schema_v38(connection)
        _migrate_schema_v38_to_v39(connection)
        existing_user_version = PROTECTED_SOURCE_SEMANTIC_SCHEMA_VERSION
    if existing_user_version == PROTECTED_SOURCE_SEMANTIC_SCHEMA_VERSION:
        _verify_schema_v39(connection)
        _migrate_schema_v39_to_v40(connection)
        existing_user_version = GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION
    if existing_user_version == GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION:
        _verify_schema_v40(connection)
        _migrate_schema_v40_to_v41(connection)
        existing_user_version = JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION

    _configure_connection(connection)
    _verify_schema_v41(connection)


def _checkpoint_wal_truncate_for_physical_cleanup(
    connection: sqlite3.Connection,
) -> None:
    try:
        row = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    except sqlite3.OperationalError as exc:
        raise DatabaseCompatibilityError(  # noqa: F405
            "SQLite WAL physical-cleanup checkpoint could not run."
        ) from exc
    if row is None or len(row) < 1 or int(row[0]) != 0:
        raise DatabaseCompatibilityError(  # noqa: F405
            "SQLite WAL physical-cleanup checkpoint is busy."
        )


def _physical_cleanup_operational_error_remnants(
    connection: sqlite3.Connection,
) -> None:
    """Remove unreachable historical error bytes from SQLite storage."""
    if connection.in_transaction:
        raise RuntimeError(
            "Operational-error physical cleanup requires no active transaction."
        )
    journal_row = connection.execute("PRAGMA journal_mode").fetchone()
    if journal_row is None:
        raise DatabaseCompatibilityError(  # noqa: F405
            "SQLite journal mode could not be determined."
        )
    journal_mode = str(journal_row[0]).lower()
    if journal_mode not in {"wal", "delete"}:
        raise DatabaseCompatibilityError(  # noqa: F405
            "ATHENA physical cleanup encountered "
            f"unsupported SQLite journal mode {journal_mode!r}."
        )
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA secure_delete = ON")
    secure_delete_row = connection.execute("PRAGMA secure_delete").fetchone()
    if secure_delete_row is None or int(secure_delete_row[0]) != 1:
        raise DatabaseCompatibilityError(  # noqa: F405
            "SQLite secure_delete could not be enabled."
        )
    if journal_mode == "wal":
        _checkpoint_wal_truncate_for_physical_cleanup(connection)
    connection.execute("VACUUM")
    if journal_mode == "wal":
        _checkpoint_wal_truncate_for_physical_cleanup(connection)
    quick_check = tuple(str(row[0]) for row in connection.execute("PRAGMA quick_check"))
    if quick_check != ("ok",):
        raise DatabaseCompatibilityError(  # noqa: F405
            "ATHENA physical-cleanup integrity verification failed."
        )
    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise DatabaseCompatibilityError(  # noqa: F405
            "ATHENA physical-cleanup foreign-key verification failed."
        )


def _migrate_schema_v37_to_v38(connection: sqlite3.Connection) -> None:
    """Physically purge unreachable historical operational-error bytes."""
    if connection.in_transaction:
        raise RuntimeError(
            "Operational-error physical-cleanup migration requires no active transaction."
        )
    _verify_schema_v37(connection)
    _physical_cleanup_operational_error_remnants(connection)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            UPDATE schema_metadata
            SET schema_version = ?, last_migration_id = ?, minimum_reader_version = ?
            WHERE singleton_id = 1
            """,
            (
                OPERATIONAL_ERROR_PHYSICAL_CLEANUP_SCHEMA_VERSION,
                OPERATIONAL_ERROR_PHYSICAL_CLEANUP_MIGRATION_ID,
                OPERATIONAL_ERROR_PHYSICAL_CLEANUP_SCHEMA_VERSION,
            ),
        )
        connection.execute(
            f"PRAGMA user_version = {OPERATIONAL_ERROR_PHYSICAL_CLEANUP_SCHEMA_VERSION}"
        )
        connection.execute("COMMIT")
    except BaseException:
        connection.rollback()
        raise
