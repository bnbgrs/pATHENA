"""Verified crash-recoverable publication to a structured long-term replica."""

from __future__ import annotations

import importlib
import json
import os
import stat
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Never, cast

from athena.common.ids import uuid_from_blob
from athena.storage.canonical_commit_bundle import (
    CanonicalCommitBundle,
    CanonicalCommitBundleError,
    verify_canonical_commit_bundle,
)
from athena.storage.durable_fs import durable_mkdir, durable_write_bytes, is_link_boundary
from athena.storage.structured_replication import (
    ReplicationCommitState,
    ReplicationTarget,
    ReplicationTargetState,
    StructuredReplicationRepository,
)

_REPOSITORY_FORMAT = "athena.long-term-repository"
_REPOSITORY_FORMAT_VERSION = 1
_HEAD_FORMAT = "athena.long-term-head"
_HEAD_FORMAT_VERSION = 1
_MAX_CONTROL_FILE_BYTES = 16 * 1024
_LOCK_NAME = ".publication.lock"


class LongTermPublicationError(RuntimeError):
    """A staged structured commit cannot be published safely."""


class LongTermPublicationConflictError(LongTermPublicationError):
    """The durable target does not match the locally confirmed history."""


class LongTermPublicationBusyError(LongTermPublicationError):
    """Another process currently owns this long-term publication target."""


@dataclass(frozen=True, slots=True)
class _BundleHeader:
    commit_id: uuid.UUID
    commit_seq: int
    previous_hash: str | None
    head_hash: str


@dataclass(frozen=True, slots=True)
class _PhysicalHead:
    target_id: uuid.UUID
    commit_seq: int
    head_hash: str


def _canonical_json_bytes(value: dict[str, object]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _normalized_hash(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise LongTermPublicationError(f"{field} must contain 64 hexadecimal characters.")
    normalized = value.lower()
    try:
        bytes.fromhex(normalized)
    except ValueError as exc:
        raise LongTermPublicationError(
            f"{field} must contain 64 hexadecimal characters."
        ) from exc
    if value != normalized:
        raise LongTermPublicationError(f"{field} must use lowercase canonical hexadecimal.")
    return normalized


def _canonical_uuid(value: object, *, field: str) -> uuid.UUID:
    if not isinstance(value, str):
        raise LongTermPublicationError(f"{field} must contain canonical UUID text.")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise LongTermPublicationError(
            f"{field} must contain canonical UUID text."
        ) from exc
    if str(parsed) != value:
        raise LongTermPublicationError(f"{field} must contain canonical UUID text.")
    return parsed


def _positive_integer(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise LongTermPublicationError(f"{field} must be a positive integer.")
    return value


def _bundle_header(data: bytes) -> tuple[CanonicalCommitBundle, _BundleHeader]:
    try:
        bundle = verify_canonical_commit_bundle(data)
    except (CanonicalCommitBundleError, TypeError) as exc:
        raise LongTermPublicationError("Canonical commit bundle verification failed.") from exc
    decoded = cast(dict[str, Any], json.loads(bundle.data.decode("utf-8")))
    body = cast(dict[str, Any], decoded["body"])
    return bundle, _BundleHeader(
        commit_id=_canonical_uuid(body["commit_id"], field="bundle commit_id"),
        commit_seq=_positive_integer(body["commit_seq"], field="bundle commit_seq"),
        previous_hash=(
            None
            if body["previous_hash"] is None
            else _normalized_hash(body["previous_hash"], field="bundle previous_hash")
        ),
        head_hash=bundle.bundle_hash,
    )


def _normalize_locator(path: Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def _validate_target_binding(target: ReplicationTarget, target_root: Path) -> None:
    if not target_root.is_absolute():
        raise LongTermPublicationError("long_term_root must be an absolute path.")
    locator = Path(target.target_locator)
    if not locator.is_absolute():
        raise LongTermPublicationError(
            "Structured replication target locator is not an absolute filesystem path."
        )
    if _normalize_locator(locator) != _normalize_locator(target_root):
        raise LongTermPublicationError(
            "Structured replication target locator does not match long_term_root."
        )


def _assert_commit_identity(
    repository: StructuredReplicationRepository,
    header: _BundleHeader,
) -> None:
    row = repository.database.connection.execute(
        "SELECT commit_id FROM commit_records WHERE commit_seq = ?",
        (header.commit_seq,),
    ).fetchone()
    if row is None:
        raise LongTermPublicationError("Bundle commit_seq does not exist locally.")
    expected = uuid_from_blob(bytes(row["commit_id"]))
    if expected != header.commit_id:
        raise LongTermPublicationError(
            "Canonical bundle commit_id does not match the local commit record."
        )


def _assert_handle_matches_path(path: Path, handle: BinaryIO, *, label: str) -> None:
    try:
        path_stat = os.stat(path, follow_symlinks=False)
        handle_stat = os.fstat(handle.fileno())
    except OSError as exc:
        raise LongTermPublicationError(f"{label} identity cannot be verified.") from exc
    if (
        is_link_boundary(path)
        or not stat.S_ISREG(handle_stat.st_mode)
        or not os.path.samestat(path_stat, handle_stat)
    ):
        raise LongTermPublicationError(f"{label} changed during access.")


def _read_regular_bytes(path: Path, *, max_bytes: int, label: str) -> bytes:
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 0:
        raise ValueError("max_bytes must be a non-negative integer.")
    if is_link_boundary(path):
        raise LongTermPublicationError(f"{label} is a symlink or reparse point.")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise LongTermPublicationError(f"{label} cannot be opened safely.") from exc
    try:
        handle = cast(BinaryIO, os.fdopen(descriptor, "rb"))
    except BaseException:
        os.close(descriptor)
        raise
    with handle:
        _assert_handle_matches_path(path, handle, label=label)
        size = os.fstat(handle.fileno()).st_size
        if size > max_bytes:
            raise LongTermPublicationError(f"{label} exceeds the accepted size.")
        data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise LongTermPublicationError(f"{label} exceeds the accepted size.")
        _assert_handle_matches_path(path, handle, label=label)
        return data


def _open_lock_file(path: Path) -> BinaryIO:
    if is_link_boundary(path):
        raise LongTermPublicationBusyError(
            "Long-term publication lock is a symlink or reparse point."
        )
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise LongTermPublicationBusyError(
            "Long-term publication lock cannot be opened safely."
        ) from exc
    try:
        handle = cast(BinaryIO, os.fdopen(descriptor, "r+b"))
    except BaseException:
        os.close(descriptor)
        raise
    try:
        path_stat = os.stat(path, follow_symlinks=False)
        handle_stat = os.fstat(handle.fileno())
        if is_link_boundary(path) or not os.path.samestat(path_stat, handle_stat):
            raise LongTermPublicationBusyError(
                "Long-term publication lock identity changed during acquisition."
            )
        if os.name == "posix":
            os.fchmod(handle.fileno(), 0o600)
        return handle
    except BaseException:
        handle.close()
        raise


def _lock_handle(handle: BinaryIO) -> None:
    if os.name == "nt":
        module = importlib.import_module("msvcrt")
        if os.fstat(handle.fileno()).st_size == 0:
            handle.seek(0)
            handle.write(b"\0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)
        try:
            module.locking(handle.fileno(), module.LK_NBLCK, 1)
        except OSError as exc:
            raise LongTermPublicationBusyError(
                "Long-term publication target is busy."
            ) from exc
        return
    if os.name == "posix":
        module = importlib.import_module("fcntl")
        try:
            module.flock(handle.fileno(), module.LOCK_EX | module.LOCK_NB)
        except OSError as exc:
            raise LongTermPublicationBusyError(
                "Long-term publication target is busy."
            ) from exc
        return
    raise LongTermPublicationBusyError(
        f"Long-term publication locking is unsupported on platform {os.name!r}."
    )


def _unlock_handle(handle: BinaryIO) -> None:
    if os.name == "nt":
        module = importlib.import_module("msvcrt")
        handle.seek(0)
        module.locking(handle.fileno(), module.LK_UNLCK, 1)
        return
    if os.name == "posix":
        module = importlib.import_module("fcntl")
        module.flock(handle.fileno(), module.LOCK_UN)
        return
    raise LongTermPublicationBusyError(
        f"Long-term publication unlocking is unsupported on platform {os.name!r}."
    )


@contextmanager
def _publication_lock(replication_root: Path) -> Iterator[None]:
    handle = _open_lock_file(replication_root / _LOCK_NAME)
    locked = False
    try:
        _lock_handle(handle)
        locked = True
        yield
    finally:
        try:
            if locked:
                _unlock_handle(handle)
        finally:
            handle.close()


def _repository_descriptor_bytes(target_id: uuid.UUID) -> bytes:
    return _canonical_json_bytes(
        {
            "format": _REPOSITORY_FORMAT,
            "format_version": _REPOSITORY_FORMAT_VERSION,
            "target_id": str(target_id),
        }
    )


def _head_bytes(target_id: uuid.UUID, commit_seq: int, head_hash: str) -> bytes:
    return _canonical_json_bytes(
        {
            "commit_seq": commit_seq,
            "format": _HEAD_FORMAT,
            "format_version": _HEAD_FORMAT_VERSION,
            "head_hash": head_hash,
            "target_id": str(target_id),
        }
    )


def _read_descriptor(path: Path, *, target_id: uuid.UUID) -> None:
    data = _read_regular_bytes(
        path,
        max_bytes=_MAX_CONTROL_FILE_BYTES,
        label="long-term repository descriptor",
    )
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LongTermPublicationError("Invalid long-term repository descriptor.") from exc
    expected = _repository_descriptor_bytes(target_id)
    if data != expected or not isinstance(value, dict):
        raise LongTermPublicationError(
            "Long-term repository descriptor does not match this target."
        )


def _read_head(path: Path, *, target_id: uuid.UUID) -> _PhysicalHead | None:
    if is_link_boundary(path):
        raise LongTermPublicationError(
            "Long-term replication head is a symlink or reparse point."
        )
    if not path.exists():
        return None
    data = _read_regular_bytes(
        path,
        max_bytes=_MAX_CONTROL_FILE_BYTES,
        label="long-term replication head",
    )
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LongTermPublicationError("Invalid long-term replication head.") from exc
    if not isinstance(value, dict) or set(value) != {
        "commit_seq",
        "format",
        "format_version",
        "head_hash",
        "target_id",
    }:
        raise LongTermPublicationError("Invalid long-term replication head.")
    if value["format"] != _HEAD_FORMAT or value["format_version"] != _HEAD_FORMAT_VERSION:
        raise LongTermPublicationError("Unsupported long-term replication head format.")
    physical = _PhysicalHead(
        target_id=_canonical_uuid(value["target_id"], field="target head target_id"),
        commit_seq=_positive_integer(value["commit_seq"], field="target head commit_seq"),
        head_hash=_normalized_hash(value["head_hash"], field="target head hash"),
    )
    if physical.target_id != target_id or data != _head_bytes(
        physical.target_id,
        physical.commit_seq,
        physical.head_hash,
    ):
        raise LongTermPublicationError(
            "Long-term replication head is noncanonical or belongs to another target."
        )
    return physical


def _mark_conflict(
    repository: StructuredReplicationRepository,
    target_id: uuid.UUID,
    *,
    code: str,
    message: str,
    now_us: int | None,
) -> Never:
    repository.mark_conflict(target_id, conflict_code=code, now_us=now_us)
    raise LongTermPublicationConflictError(message)


def _ensure_descriptor(
    repository: StructuredReplicationRepository,
    target: ReplicationTarget,
    descriptor_path: Path,
    *,
    now_us: int | None,
) -> None:
    if is_link_boundary(descriptor_path):
        _mark_conflict(
            repository,
            target.target_id,
            code="repository_identity_mismatch",
            message="Long-term repository descriptor is a symlink or reparse point.",
            now_us=now_us,
        )
    if descriptor_path.exists():
        try:
            _read_descriptor(descriptor_path, target_id=target.target_id)
        except LongTermPublicationError as exc:
            _mark_conflict(
                repository,
                target.target_id,
                code="repository_identity_mismatch",
                message=str(exc),
                now_us=now_us,
            )
        return
    if target.confirmed_commit_seq != 0 or target.confirmed_head_hash is not None:
        _mark_conflict(
            repository,
            target.target_id,
            code="repository_identity_missing",
            message="Confirmed long-term target lost its repository descriptor.",
            now_us=now_us,
        )
    expected = _repository_descriptor_bytes(target.target_id)
    durable_write_bytes(descriptor_path, expected)
    if _read_regular_bytes(
        descriptor_path,
        max_bytes=_MAX_CONTROL_FILE_BYTES,
        label="long-term repository descriptor",
    ) != expected:
        _mark_conflict(
            repository,
            target.target_id,
            code="repository_identity_write_verify_failed",
            message="Long-term repository descriptor failed read-back verification.",
            now_us=now_us,
        )


def _verify_or_write_commit_object(
    repository: StructuredReplicationRepository,
    target_id: uuid.UUID,
    commit_path: Path,
    bundle: CanonicalCommitBundle,
    *,
    allow_create: bool,
    now_us: int | None,
) -> None:
    if is_link_boundary(commit_path):
        _mark_conflict(
            repository,
            target_id,
            code="commit_object_invalid",
            message="Long-term commit object is a symlink or reparse point.",
            now_us=now_us,
        )
    if commit_path.exists():
        try:
            existing = _read_regular_bytes(
                commit_path,
                max_bytes=len(bundle.data),
                label="long-term commit object",
            )
            verified = verify_canonical_commit_bundle(existing)
        except (LongTermPublicationError, CanonicalCommitBundleError, TypeError) as exc:
            _mark_conflict(
                repository,
                target_id,
                code="commit_object_invalid",
                message="Existing long-term commit object is invalid.",
                now_us=now_us,
            )
        if existing != bundle.data or verified.bundle_hash != bundle.bundle_hash:
            _mark_conflict(
                repository,
                target_id,
                code="commit_object_mismatch",
                message="Existing long-term commit object differs from staged history.",
                now_us=now_us,
            )
        return

    if not allow_create:
        _mark_conflict(
            repository,
            target_id,
            code="head_without_commit_object",
            message="Published long-term head has no matching immutable commit object.",
            now_us=now_us,
        )

    durable_write_bytes(commit_path, bundle.data)
    try:
        published = _read_regular_bytes(
            commit_path,
            max_bytes=len(bundle.data),
            label="long-term commit object",
        )
        verified = verify_canonical_commit_bundle(published)
    except (LongTermPublicationError, CanonicalCommitBundleError, TypeError) as exc:
        _mark_conflict(
            repository,
            target_id,
            code="commit_object_write_verify_failed",
            message="Long-term commit object failed post-write verification.",
            now_us=now_us,
        )
    if published != bundle.data or verified.bundle_hash != bundle.bundle_hash:
        _mark_conflict(
            repository,
            target_id,
            code="commit_object_write_verify_failed",
            message="Long-term commit object failed post-write verification.",
            now_us=now_us,
        )


def publish_staged_commit(
    repository: StructuredReplicationRepository,
    *,
    target_id: uuid.UUID,
    target_root: Path,
    bundle_data: bytes,
    now_us: int | None = None,
) -> ReplicationTarget:
    """Publish one already-staged canonical bundle and then advance its DB watermark.

    The immutable commit object is written and read back before the physical head is
    advanced. The physical head is then read back before the structured-replication
    watermark is confirmed. A retry after a crash can therefore resume from either
    the commit-object boundary or the physical-head boundary without inventing state.
    """

    if not isinstance(repository, StructuredReplicationRepository):
        raise TypeError("repository must be a StructuredReplicationRepository.")
    if not isinstance(target_id, uuid.UUID):
        raise TypeError("target_id must be a UUID.")
    if not isinstance(target_root, Path):
        raise TypeError("target_root must be a pathlib.Path.")
    if not isinstance(bundle_data, bytes):
        raise TypeError("bundle_data must be bytes.")

    bundle, header = _bundle_header(bundle_data)
    target = repository.get_target(target_id)
    _validate_target_binding(target, target_root)
    _assert_commit_identity(repository, header)

    commit = repository.get_commit(target_id, header.commit_seq)
    if commit.head_hash != header.head_hash or commit.previous_head_hash != header.previous_hash:
        raise LongTermPublicationError(
            "Staged replication state does not match the canonical bundle."
        )
    if target.state is ReplicationTargetState.CONFLICT:
        raise LongTermPublicationConflictError(
            "Long-term replication target is already in conflict."
        )
    if (
        commit.state is ReplicationCommitState.PENDING
        and target.state not in {
            ReplicationTargetState.PENDING,
            ReplicationTargetState.ACTIVE,
        }
    ):
        raise LongTermPublicationError(
            f"Replication target state {target.state.value!r} cannot publish new history."
        )

    root = target_root
    commits_root = root / "commits"
    replication_root = root / "replication"
    descriptor_path = root / "repository.json"
    head_path = replication_root / "head.json"
    commit_path = commits_root / f"{header.commit_seq:020d}.json"

    durable_mkdir(root, parents=True, exist_ok=True)
    durable_mkdir(commits_root, exist_ok=True)
    durable_mkdir(replication_root, exist_ok=True)

    with _publication_lock(replication_root):
        target = repository.get_target(target_id)
        commit = repository.get_commit(target_id, header.commit_seq)
        if target.state is ReplicationTargetState.CONFLICT:
            raise LongTermPublicationConflictError(
                "Long-term replication target is already in conflict."
            )
        _ensure_descriptor(
            repository,
            target,
            descriptor_path,
            now_us=now_us,
        )

        if commit.state is ReplicationCommitState.VERIFIED:
            if target.confirmed_commit_seq < header.commit_seq:
                raise LongTermPublicationError(
                    "Verified replication commit is ahead of the target watermark."
                )
            if (
                target.confirmed_commit_seq == header.commit_seq
                and target.confirmed_head_hash != header.head_hash
            ):
                raise LongTermPublicationError(
                    "Verified replication commit disagrees with the target watermark."
                )
            try:
                physical = _read_head(head_path, target_id=target_id)
            except LongTermPublicationError as exc:
                _mark_conflict(
                    repository,
                    target_id,
                    code="confirmed_head_invalid",
                    message=str(exc),
                    now_us=now_us,
                )
            if (
                physical is None
                or physical.commit_seq != target.confirmed_commit_seq
                or physical.head_hash != target.confirmed_head_hash
            ):
                _mark_conflict(
                    repository,
                    target_id,
                    code="confirmed_head_mismatch",
                    message="Confirmed target watermark differs from physical long-term head.",
                    now_us=now_us,
                )
            _verify_or_write_commit_object(
                repository,
                target_id,
                commit_path,
                bundle,
                allow_create=False,
                now_us=now_us,
            )
            return repository.get_target(target_id)

        if target.state not in {
            ReplicationTargetState.PENDING,
            ReplicationTargetState.ACTIVE,
        }:
            raise LongTermPublicationError(
                f"Replication target state {target.state.value!r} cannot publish new history."
            )
        if (
            header.commit_seq != target.confirmed_commit_seq + 1
            or header.previous_hash != target.confirmed_head_hash
        ):
            raise LongTermPublicationError(
                "Canonical bundle does not extend the confirmed target watermark."
            )

        try:
            physical = _read_head(head_path, target_id=target_id)
        except LongTermPublicationError as exc:
            _mark_conflict(
                repository,
                target_id,
                code="unexpected_target_head",
                message=str(exc),
                now_us=now_us,
            )

        resume_after_head = (
            physical is not None
            and physical.commit_seq == header.commit_seq
            and physical.head_hash == header.head_hash
        )
        expected_physical = (
            physical is None
            and target.confirmed_commit_seq == 0
            and target.confirmed_head_hash is None
        ) or (
            physical is not None
            and physical.commit_seq == target.confirmed_commit_seq
            and physical.head_hash == target.confirmed_head_hash
        )
        if not expected_physical and not resume_after_head:
            _mark_conflict(
                repository,
                target_id,
                code="unexpected_target_head",
                message="Physical long-term head does not match confirmed or resumable history.",
                now_us=now_us,
            )

        _verify_or_write_commit_object(
            repository,
            target_id,
            commit_path,
            bundle,
            allow_create=not resume_after_head,
            now_us=now_us,
        )

        expected_head_bytes = _head_bytes(
            target_id,
            header.commit_seq,
            header.head_hash,
        )
        if not resume_after_head:
            durable_write_bytes(head_path, expected_head_bytes)
        try:
            published_head = _read_regular_bytes(
                head_path,
                max_bytes=_MAX_CONTROL_FILE_BYTES,
                label="long-term replication head",
            )
            verified_head = _read_head(head_path, target_id=target_id)
        except LongTermPublicationError as exc:
            _mark_conflict(
                repository,
                target_id,
                code="head_write_verify_failed",
                message=str(exc),
                now_us=now_us,
            )
        if (
            published_head != expected_head_bytes
            or verified_head is None
            or verified_head.commit_seq != header.commit_seq
            or verified_head.head_hash != header.head_hash
        ):
            _mark_conflict(
                repository,
                target_id,
                code="head_write_verify_failed",
                message="Long-term replication head failed post-write verification.",
                now_us=now_us,
            )

        return repository.confirm_commit(
            target_id,
            commit_seq=header.commit_seq,
            head_hash=header.head_hash,
            now_us=now_us,
        )
