"""Persistent reproducibility metadata for SourceChunk profiles."""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
import uuid
from dataclasses import dataclass

from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase


@dataclass(frozen=True, slots=True)
class ChunkingProfile:
    chunking_profile_id: uuid.UUID
    algorithm: str
    tokenizer: str | None
    target_size: int | None
    overlap_size: int | None
    structure_rules_json: str
    profile_version: int
    configuration_hash: bytes
    created_at_us: int


_DEFAULT_STRUCTURE_RULES = {
    "anchor_unit": "unicode_codepoint_offset",
    "boundary_priority": ["paragraph", "line", "whitespace", "hard_limit"],
    "preserve_exact_text_slices": True,
}
_DOCUMENT_STRUCTURE_RULES = {
    "anchor_unit": "unicode_codepoint_offset",
    "boundary_priority": [
        "document_block",
        "nested_structure",
        "line",
        "whitespace",
        "hard_limit",
    ],
    "preserve_exact_text_slices": True,
    "structure_map": "retained_v1",
}
_DEFAULT_ALGORITHM = "paragraph_char_v1"
_DOCUMENT_ALGORITHM = "document_structure_char_v1"
_DEFAULT_TARGET_SIZE = 1200
_DEFAULT_OVERLAP_SIZE = 0
_DEFAULT_PROFILE_VERSION = 1


class ChunkingProfileRepository:
    """Store immutable versioned chunking configurations in canonical metadata."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def get_or_create_default(self) -> ChunkingProfile:
        return self.get_or_create(
            algorithm=_DEFAULT_ALGORITHM,
            tokenizer=None,
            target_size=_DEFAULT_TARGET_SIZE,
            overlap_size=_DEFAULT_OVERLAP_SIZE,
            structure_rules=dict(_DEFAULT_STRUCTURE_RULES),
            profile_version=_DEFAULT_PROFILE_VERSION,
        )

    def get_or_create_document_default(self) -> ChunkingProfile:
        return self.get_or_create(
            algorithm=_DOCUMENT_ALGORITHM,
            tokenizer=None,
            target_size=_DEFAULT_TARGET_SIZE,
            overlap_size=_DEFAULT_OVERLAP_SIZE,
            structure_rules=dict(_DOCUMENT_STRUCTURE_RULES),
            profile_version=_DEFAULT_PROFILE_VERSION,
        )

    def get_or_create(
        self,
        *,
        algorithm: str,
        tokenizer: str | None,
        target_size: int | None,
        overlap_size: int | None,
        structure_rules: dict[str, object],
        profile_version: int,
    ) -> ChunkingProfile:
        normalized_algorithm = _canonical_text(algorithm, "Chunking algorithm")
        normalized_tokenizer = _optional_canonical_text(tokenizer, "Chunking tokenizer")
        normalized_target_size = _optional_positive_int(
            target_size,
            "Chunking target_size",
        )
        normalized_overlap_size = _optional_nonnegative_int(
            overlap_size,
            "Chunking overlap_size",
        )
        normalized_profile_version = _positive_int(
            profile_version,
            "Chunking profile_version",
        )
        normalized_structure_rules = _json_object(
            structure_rules,
            "Chunking structure_rules",
        )

        structure_rules_json = _canonical_json(normalized_structure_rules)
        configuration = {
            "algorithm": normalized_algorithm,
            "tokenizer": normalized_tokenizer,
            "target_size": normalized_target_size,
            "overlap_size": normalized_overlap_size,
            "structure_rules": json.loads(structure_rules_json),
            "profile_version": normalized_profile_version,
        }
        configuration_hash = hashlib.sha256(
            _canonical_json(configuration).encode("utf-8")
        ).digest()

        with self.database.write_transaction() as connection:
            row = connection.execute(
                "SELECT * FROM chunking_profiles WHERE configuration_hash = ?",
                (configuration_hash,),
            ).fetchone()
            if row is not None:
                return _profile_from_row(row)

            profile_id = new_uuid7()
            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO chunking_profiles (
                    chunking_profile_id, algorithm, tokenizer, target_size,
                    overlap_size, structure_rules_json, profile_version,
                    configuration_hash, created_at_us
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(profile_id),
                    normalized_algorithm,
                    normalized_tokenizer,
                    normalized_target_size,
                    normalized_overlap_size,
                    structure_rules_json,
                    normalized_profile_version,
                    configuration_hash,
                    created_at_us,
                ),
            )

        return ChunkingProfile(
            chunking_profile_id=profile_id,
            algorithm=normalized_algorithm,
            tokenizer=normalized_tokenizer,
            target_size=normalized_target_size,
            overlap_size=normalized_overlap_size,
            structure_rules_json=structure_rules_json,
            profile_version=normalized_profile_version,
            configuration_hash=configuration_hash,
            created_at_us=created_at_us,
        )

    def get(self, chunking_profile_id: uuid.UUID) -> ChunkingProfile:
        row = self.database.connection.execute(
            "SELECT * FROM chunking_profiles WHERE chunking_profile_id = ?",
            (uuid_to_blob(chunking_profile_id),),
        ).fetchone()
        if row is None:
            raise LookupError(f"ChunkingProfile {chunking_profile_id} not found.")
        return _profile_from_row(row)


def _canonical_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be empty.")
    return normalized


def _optional_canonical_text(value: object | None, label: str) -> str | None:
    if value is None:
        return None
    return _canonical_text(value, label)


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be an integer >= 1.")
    return value


def _optional_positive_int(value: object | None, label: str) -> int | None:
    if value is None:
        return None
    return _positive_int(value, label)


def _optional_nonnegative_int(value: object | None, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be an integer >= 0.")
    return value


def _json_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    _validate_json_value(value, label)
    return value


def _validate_json_value(value: object, label: str) -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{label} must contain finite JSON numbers.")
        return
    if isinstance(value, list):
        for item in value:
            _validate_json_value(item, label)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{label} JSON object keys must be text.")
            _validate_json_value(item, label)
        return
    raise ValueError(f"{label} must contain JSON values only.")


def _canonical_json(value: object) -> str:
    _validate_json_value(value, "Chunking configuration")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _profile_from_row(row: sqlite3.Row) -> ChunkingProfile:
    return ChunkingProfile(
        chunking_profile_id=uuid_from_blob(row["chunking_profile_id"]),
        algorithm=str(row["algorithm"]),
        tokenizer=(str(row["tokenizer"]) if row["tokenizer"] is not None else None),
        target_size=(int(row["target_size"]) if row["target_size"] is not None else None),
        overlap_size=(int(row["overlap_size"]) if row["overlap_size"] is not None else None),
        structure_rules_json=str(row["structure_rules_json"]),
        profile_version=int(row["profile_version"]),
        configuration_hash=bytes(row["configuration_hash"]),
        created_at_us=int(row["created_at_us"]),
    )
