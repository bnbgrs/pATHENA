"""Verified append-only publication for structured long-term replication.

The durable SQLite repository owns local staging/confirmation state. This module
owns the external filesystem boundary: commit bundles and manifest records are
immutable, published without replacement, read back and verified before the
local replication watermark may advance.
"""

from __future__ import annotations

import json
import os
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from athena.common.ids import uuid_from_blob
from athena.storage.canonical_commit_bundle import (
    FORMAT as COMMIT_FORMAT,
    FORMAT_VERSION as COMMIT_FORMAT_VERSION,
)
from athena.storage.canonical_commit_bundle import (
    CanonicalCommitBundle,
    CanonicalCommitBundleError,
    verify_canonical_commit_bundle,
)
from athena.storage.durable_fs import (
    durable_mkdir,
    durable_publish_new_bytes,
    is_link_boundary,
)
from athena.storage.structured_replication import (
    ReplicationCommitState,
    ReplicationTarget,
    ReplicationTargetState,
    StructuredReplicationInvariantError,
    StructuredReplicationRepository,
)

_REPOSITORY_FORMAT = "athena.structured-replication-repository"
_REPOSITORY_VERSION = 1
_STORAGE_LAYOUT_VERSION = 1
_REPOSITORY_LIMIT = 16 * 1024
_REPOSITORY_KEYS = frozenset(
    {
        "format",
        "format_version",
        "repository_id",
        "hash_algorithm",
        "commit_format",
        "commit_format_version",
        "storage_layout_version",
    }
)
_MANIFEST_FORMAT = "athena.structured-replication-head"
_MANIFEST_VERSION = 1
_MANIFEST_LIMIT = 16 * 1024
_BUNDLE_LIMIT = 256 * 1024 * 1024
_HASH_LENGTH = 64
_MANIFEST_KEYS = frozenset(
    {
        "format",
        "format_version",
        "commit_seq",
        "head_hash",
        "previous_head_hash",
        "bundle_file",
    }
)


class StructuredReplicationPublicationError(RuntimeError):
    """Base error for verified long-term filesystem publication."""


class StructuredReplicationConflictError(StructuredReplicationPublicationError):
    """Raised after unexpected target history is persisted as a conflict."""


class _TargetHistoryError(StructuredReplicationPublicationError):
    """Internal signal for remote history that cannot be trusted."""


@dataclass(frozen=True, slots=True)
class _ManifestEntry:
    commit_seq: int
    head_hash: str
    previous_head_hash: str | None
    bundle_file: str
    data: bytes


def _hash(value: object, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or len(value) != _HASH_LENGTH:
        raise _TargetHistoryError(
            "Structured replication target contains an invalid hash."
        )
    normalized = value.lower()
    try:
        bytes.fromhex(normalized)
    except ValueError as exc:
        raise _TargetHistoryError(
            "Structured replication target contains an invalid hash."
        ) from exc
    return normalized


def _positive_int(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise _TargetHistoryError(f"{label} must be a positive integer.")
    return value


def _canonical_repository_bytes(repository_id: uuid.UUID) -> bytes:
    payload = {
        "commit_format": COMMIT_FORMAT,
        "commit_format_version": COMMIT_FORMAT_VERSION,
        "format": _REPOSITORY_FORMAT,
        "format_version": _REPOSITORY_VERSION,
        "hash_algorithm": "sha256",
        "repository_id": str(repository_id),
        "storage_layout_version": _STORAGE_LAYOUT_VERSION,
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _verify_repository_bytes(
    data: bytes,
    *,
    expected_repository_id: uuid.UUID,
) -> None:
    try:
        payload: Any = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _TargetHistoryError(
            "Structured replication repository manifest is invalid JSON."
        ) from exc
    if not isinstance(payload, dict) or set(payload) != _REPOSITORY_KEYS:
        raise _TargetHistoryError(
            "Structured replication repository manifest has an invalid shape."
        )
    if (
        payload.get("format") != _REPOSITORY_FORMAT
        or payload.get("format_version") != _REPOSITORY_VERSION
        or payload.get("hash_algorithm") != "sha256"
        or payload.get("commit_format") != COMMIT_FORMAT
        or payload.get("commit_format_version") != COMMIT_FORMAT_VERSION
        or payload.get("storage_layout_version") != _STORAGE_LAYOUT_VERSION
    ):
        raise _TargetHistoryError(
            "Structured replication repository manifest has an unsupported format."
        )
    repository_id = payload.get("repository_id")
    if not isinstance(repository_id, str):
        raise _TargetHistoryError(
            "Structured replication repository identity is invalid."
        )
    try:
        parsed = uuid.UUID(repository_id)
    except ValueError as exc:
        raise _TargetHistoryError(
            "Structured replication repository identity is invalid."
        ) from exc
    if str(parsed) != repository_id or parsed != expected_repository_id:
        raise _TargetHistoryError(
            "Structured replication repository identity does not match the target."
        )
    if data != _canonical_repository_bytes(expected_repository_id):
        raise _TargetHistoryError(
            "Structured replication repository manifest bytes are not canonical."
        )


def _canonical_manifest_bytes(
    *,
    commit_seq: int,
    head_hash: str,
    previous_head_hash: str | None,
    bundle_file: str,
) -> bytes:
    payload = {
        "bundle_file": bundle_file,
        "commit_seq": commit_seq,
        "format": _MANIFEST_FORMAT,
        "format_version": _MANIFEST_VERSION,
        "head_hash": head_hash,
        "previous_head_hash": previous_head_hash,
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _manifest_name(commit_seq: int) -> str:
    return f"{commit_seq:020d}.json"


def _bundle_name(commit_seq: int, head_hash: str) -> str:
    return f"{commit_seq:020d}-{head_hash}.json"


def _read_regular_file(path: Path, *, max_bytes: int) -> bytes:
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive.")
    if is_link_boundary(path):
        raise _TargetHistoryError(
            f"Structured replication target file is a link boundary: {path}"
        )

    cursor = path.parent
    while True:
        if is_link_boundary(cursor):
            raise _TargetHistoryError(
                "Structured replication target has a link-backed ancestor: "
                f"{cursor}"
            )
        parent = cursor.parent
        if parent == cursor:
            break
        cursor = parent

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise StructuredReplicationPublicationError(
            f"Structured replication target file could not be opened: {path}"
        ) from exc

    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise _TargetHistoryError(
                f"Structured replication target entry is not a regular file: {path}"
            )
        if before.st_size > max_bytes:
            raise _TargetHistoryError(
                f"Structured replication target file exceeds its size bound: {path}"
            )
        try:
            pathname_stat = os.stat(path, follow_symlinks=False)
        except OSError as exc:
            raise _TargetHistoryError(
                f"Structured replication target file identity is unstable: {path}"
            ) from exc
        if not os.path.samestat(before, pathname_stat):
            raise _TargetHistoryError(
                f"Structured replication target file identity changed: {path}"
            )

        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) > max_bytes:
            raise _TargetHistoryError(
                f"Structured replication target file exceeds its size bound: {path}"
            )

        after = os.fstat(descriptor)
        try:
            pathname_after = os.stat(path, follow_symlinks=False)
        except OSError as exc:
            raise _TargetHistoryError(
                f"Structured replication target file disappeared during read: {path}"
            ) from exc
        if (
            not os.path.samestat(before, after)
            or not os.path.samestat(after, pathname_after)
            or before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or before.st_ctime_ns != after.st_ctime_ns
            or after.st_size != len(data)
        ):
            raise _TargetHistoryError(
                f"Structured replication target file changed during read: {path}"
            )
        return data
    finally:
        os.close(descriptor)



def _assert_safe_partial_file(path: Path) -> None:
    """Allow only inert regular files as crash residue inside managed storage."""
    if is_link_boundary(path):
        raise _TargetHistoryError(
            f"Structured replication partial entry is a link boundary: {path.name}"
        )
    try:
        mode = path.stat(follow_symlinks=False).st_mode
    except OSError as exc:
        raise _TargetHistoryError(
            f"Structured replication partial entry identity is unstable: {path.name}"
        ) from exc
    if not stat.S_ISREG(mode):
        raise _TargetHistoryError(
            f"Structured replication partial entry is not a regular file: {path.name}"
        )

def _ensure_managed_directory(path: Path) -> None:
    """Create or verify one managed directory without tolerating type redirection."""
    if is_link_boundary(path):
        raise _TargetHistoryError(
            f"Structured replication managed path is a link boundary: {path.name}"
        )
    if path.exists() and not path.is_dir():
        raise _TargetHistoryError(
            f"Structured replication managed path is not a directory: {path.name}"
        )
    try:
        durable_mkdir(path, parents=False, exist_ok=True)
    except (FileExistsError, NotADirectoryError) as exc:
        raise _TargetHistoryError(
            f"Structured replication managed path changed during preparation: {path.name}"
        ) from exc


def _parse_manifest(path: Path) -> _ManifestEntry:
    data = _read_regular_file(path, max_bytes=_MANIFEST_LIMIT)
    try:
        payload: Any = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _TargetHistoryError(
            f"Structured replication manifest is invalid JSON: {path.name}"
        ) from exc
    if not isinstance(payload, dict) or set(payload) != _MANIFEST_KEYS:
        raise _TargetHistoryError(
            f"Structured replication manifest has an invalid shape: {path.name}"
        )
    if (
        payload.get("format") != _MANIFEST_FORMAT
        or payload.get("format_version") != _MANIFEST_VERSION
    ):
        raise _TargetHistoryError(
            f"Structured replication manifest has an unsupported format: {path.name}"
        )

    commit_seq = _positive_int(payload.get("commit_seq"), label="Manifest commit_seq")
    head_hash = _hash(payload.get("head_hash"))
    if head_hash is None:
        raise _TargetHistoryError(
            f"Structured replication manifest head hash is missing: {path.name}"
        )
    previous_head_hash = _hash(
        payload.get("previous_head_hash"),
        optional=True,
    )
    bundle_file = payload.get("bundle_file")
    if not isinstance(bundle_file, str) or bundle_file != _bundle_name(
        commit_seq,
        head_hash,
    ):
        raise _TargetHistoryError(
            f"Structured replication manifest bundle identity is invalid: {path.name}"
        )
    if path.name != _manifest_name(commit_seq):
        raise _TargetHistoryError(
            f"Structured replication manifest filename is invalid: {path.name}"
        )

    expected = _canonical_manifest_bytes(
        commit_seq=commit_seq,
        head_hash=head_hash,
        previous_head_hash=previous_head_hash,
        bundle_file=bundle_file,
    )
    if data != expected:
        raise _TargetHistoryError(
            f"Structured replication manifest bytes are not canonical: {path.name}"
        )
    return _ManifestEntry(
        commit_seq=commit_seq,
        head_hash=head_hash,
        previous_head_hash=previous_head_hash,
        bundle_file=bundle_file,
        data=data,
    )


class StructuredReplicationPublisher:
    """Publish one staged canonical bundle and confirm it only after verification."""

    def __init__(self, repository: StructuredReplicationRepository) -> None:
        self.repository = repository

    def publish_staged_bundle(
        self,
        target_id: uuid.UUID,
        bundle: CanonicalCommitBundle,
    ) -> ReplicationTarget:
        if not isinstance(bundle, CanonicalCommitBundle):
            raise TypeError("Structured replication publication requires a canonical bundle.")

        try:
            verified = verify_canonical_commit_bundle(bundle.data)
        except CanonicalCommitBundleError as exc:
            raise StructuredReplicationPublicationError(
                "Structured replication bundle failed canonical verification."
            ) from exc
        if verified.bundle_hash != bundle.bundle_hash:
            raise StructuredReplicationPublicationError(
                "Structured replication bundle hash does not match its verified bytes."
            )

        body = json.loads(verified.data.decode("utf-8"))["body"]
        commit_seq = int(body["commit_seq"])
        previous_head_hash = body["previous_hash"]
        commit_id = str(body["commit_id"])

        try:
            local_commit = self.repository.get_commit(target_id, commit_seq)
            target = self.repository.get_target(target_id)
        except (LookupError, TypeError, ValueError) as exc:
            raise StructuredReplicationPublicationError(
                "Structured replication publication requires a staged local commit."
            ) from exc

        if (
            local_commit.head_hash != verified.bundle_hash
            or local_commit.previous_head_hash != previous_head_hash
        ):
            raise StructuredReplicationPublicationError(
                "Staged replication state does not match the canonical bundle."
            )
        self._assert_canonical_commit_identity(commit_seq, commit_id)

        if target.state is ReplicationTargetState.CONFLICT:
            raise StructuredReplicationConflictError(
                "Conflicted replication target must enter recovery before publication."
            )
        if target.state is ReplicationTargetState.PAUSED:
            raise StructuredReplicationPublicationError(
                "Paused replication target cannot publish."
            )

        target_root = Path(target.target_locator).expanduser()
        if not target_root.is_absolute():
            raise StructuredReplicationPublicationError(
                "Structured replication target locator must be an absolute path."
            )
        durable_mkdir(target_root, parents=True, exist_ok=True)
        commits_dir = target_root / "commits"
        snapshots_dir = target_root / "snapshots"
        manifest_dir = target_root / "manifests"
        replication_dir = target_root / "replication"

        try:
            self._ensure_repository_manifest(
                target=target,
                target_root=target_root,
            )
            _ensure_managed_directory(commits_dir)
            _ensure_managed_directory(snapshots_dir)
            _ensure_managed_directory(manifest_dir)
            _ensure_managed_directory(replication_dir)

            entries = self._scan_target(
                commits_dir=commits_dir,
                manifest_dir=manifest_dir,
                current_bundle=verified,
                current_commit_seq=commit_seq,
            )
            remote_seq, remote_hash = self._remote_head(entries)
            self._assert_local_remote_alignment(
                target=target,
                local_state=local_commit.state,
                commit_seq=commit_seq,
                bundle_hash=verified.bundle_hash,
                remote_seq=remote_seq,
                remote_hash=remote_hash,
            )

            if local_commit.state is ReplicationCommitState.VERIFIED:
                self._verify_committed_entry(
                    entries=entries,
                    commits_dir=commits_dir,
                    commit_seq=commit_seq,
                    bundle=verified,
                )
                return self.repository.get_target(target_id)

            if remote_seq == commit_seq and remote_hash == verified.bundle_hash:
                self._verify_committed_entry(
                    entries=entries,
                    commits_dir=commits_dir,
                    commit_seq=commit_seq,
                    bundle=verified,
                )
                return self._confirm_or_observe(
                    target_id=target_id,
                    commit_seq=commit_seq,
                    head_hash=verified.bundle_hash,
                )

            bundle_name = _bundle_name(commit_seq, verified.bundle_hash)
            bundle_path = commits_dir / bundle_name
            self._publish_or_verify_bundle(bundle_path, verified)

            manifest_data = _canonical_manifest_bytes(
                commit_seq=commit_seq,
                head_hash=verified.bundle_hash,
                previous_head_hash=previous_head_hash,
                bundle_file=bundle_name,
            )
            manifest_path = manifest_dir / _manifest_name(commit_seq)
            self._publish_or_verify_exact(manifest_path, manifest_data)

            entries = self._scan_target(
                commits_dir=commits_dir,
                manifest_dir=manifest_dir,
                current_bundle=verified,
                current_commit_seq=commit_seq,
            )
            remote_seq, remote_hash = self._remote_head(entries)
            if remote_seq != commit_seq or remote_hash != verified.bundle_hash:
                raise _TargetHistoryError(
                    "Structured replication target head changed before confirmation."
                )
            self._verify_committed_entry(
                entries=entries,
                commits_dir=commits_dir,
                commit_seq=commit_seq,
                bundle=verified,
            )
        except _TargetHistoryError as exc:
            self.repository.mark_conflict(
                target_id,
                conflict_code="unexpected_target_history",
            )
            raise StructuredReplicationConflictError(str(exc)) from exc

        return self._confirm_or_observe(
            target_id=target_id,
            commit_seq=commit_seq,
            head_hash=verified.bundle_hash,
        )

    def _confirm_or_observe(
        self,
        *,
        target_id: uuid.UUID,
        commit_seq: int,
        head_hash: str,
    ) -> ReplicationTarget:
        latest_commit = self.repository.get_commit(target_id, commit_seq)
        latest_target = self.repository.get_target(target_id)
        if latest_commit.state is ReplicationCommitState.VERIFIED:
            if latest_target.confirmed_commit_seq < commit_seq:
                raise StructuredReplicationPublicationError(
                    "Verified replication commit is not reflected by the target watermark."
                )
            return latest_target

        try:
            return self.repository.confirm_commit(
                target_id,
                commit_seq=commit_seq,
                head_hash=head_hash,
            )
        except StructuredReplicationInvariantError:
            latest_commit = self.repository.get_commit(target_id, commit_seq)
            latest_target = self.repository.get_target(target_id)
            if (
                latest_commit.state is ReplicationCommitState.VERIFIED
                and latest_target.confirmed_commit_seq >= commit_seq
            ):
                return latest_target
            raise

    def _ensure_repository_manifest(
        self,
        *,
        target: ReplicationTarget,
        target_root: Path,
    ) -> None:
        repository_path = target_root / "repository.json"
        expected = _canonical_repository_bytes(target.target_id)
        try:
            existing = _read_regular_file(
                repository_path,
                max_bytes=_REPOSITORY_LIMIT,
            )
        except FileNotFoundError:
            unexpected: list[Path] = []
            for item in target_root.iterdir():
                if (
                    item.name.startswith(".repository.json.")
                    and item.name.endswith(".partial")
                ):
                    _assert_safe_partial_file(item)
                    continue
                unexpected.append(item)
            if unexpected:
                raise _TargetHistoryError(
                    "Structured replication repository manifest is missing "
                    "from a non-empty target."
                ) from None
            try:
                durable_publish_new_bytes(repository_path, expected)
            except FileExistsError:
                pass
            try:
                existing = _read_regular_file(
                    repository_path,
                    max_bytes=_REPOSITORY_LIMIT,
                )
            except FileNotFoundError as exc:
                raise _TargetHistoryError(
                    "Structured replication repository manifest disappeared "
                    "during initialization."
                ) from exc

        if existing != expected:
            _verify_repository_bytes(
                existing,
                expected_repository_id=target.target_id,
            )
            raise _TargetHistoryError(
                "Structured replication repository manifest differs "
                "from the expected target identity."
            )
        _verify_repository_bytes(
            existing,
            expected_repository_id=target.target_id,
        )

        allowed = {
            "repository.json",
            "commits",
            "snapshots",
            "manifests",
            "replication",
        }
        for item in target_root.iterdir():
            if item.name in allowed:
                continue
            if (
                item.name.startswith(".repository.json.")
                and item.name.endswith(".partial")
            ):
                _assert_safe_partial_file(item)
                continue
            raise _TargetHistoryError(
                f"Unexpected long-term repository entry: {item.name}"
            )

    def _assert_canonical_commit_identity(
        self,
        commit_seq: int,
        commit_id: str,
    ) -> None:
        row = self.repository.database.connection.execute(
            "SELECT commit_id FROM commit_records WHERE commit_seq = ?",
            (commit_seq,),
        ).fetchone()
        if row is None:
            raise StructuredReplicationPublicationError(
                "Canonical commit bundle references an unknown local commit sequence."
            )
        local_commit_id = str(uuid_from_blob(bytes(row["commit_id"])))
        if local_commit_id != commit_id:
            raise StructuredReplicationPublicationError(
                "Canonical commit bundle identity does not match local commit history."
            )

    @staticmethod
    def _remote_head(
        entries: tuple[_ManifestEntry, ...],
    ) -> tuple[int, str | None]:
        if not entries:
            return 0, None
        latest = entries[-1]
        return latest.commit_seq, latest.head_hash

    @staticmethod
    def _assert_local_remote_alignment(
        *,
        target: ReplicationTarget,
        local_state: ReplicationCommitState,
        commit_seq: int,
        bundle_hash: str,
        remote_seq: int,
        remote_hash: str | None,
    ) -> None:
        if local_state is ReplicationCommitState.PENDING:
            if commit_seq != target.confirmed_commit_seq + 1:
                raise StructuredReplicationPublicationError(
                    "Only the next unconfirmed structured commit may be published."
                )
            if (
                remote_seq == target.confirmed_commit_seq
                and remote_hash == target.confirmed_head_hash
            ):
                return
            if remote_seq == commit_seq and remote_hash == bundle_hash:
                return
            raise _TargetHistoryError(
                "Structured replication target head does not match local confirmed history."
            )

        if target.confirmed_commit_seq < commit_seq:
            raise StructuredReplicationPublicationError(
                "Verified local replication commit is ahead of the target watermark."
            )
        if (
            remote_seq != target.confirmed_commit_seq
            or remote_hash != target.confirmed_head_hash
        ):
            raise _TargetHistoryError(
                "Structured replication target head differs from the confirmed local watermark."
            )

    def _scan_target(
        self,
        *,
        commits_dir: Path,
        manifest_dir: Path,
        current_bundle: CanonicalCommitBundle,
        current_commit_seq: int,
    ) -> tuple[_ManifestEntry, ...]:
        if (
            is_link_boundary(commits_dir)
            or is_link_boundary(manifest_dir)
            or not commits_dir.is_dir()
            or not manifest_dir.is_dir()
        ):
            raise _TargetHistoryError(
                "Structured replication managed directories are unsafe."
            )

        entries: list[_ManifestEntry] = []
        for path in sorted(manifest_dir.iterdir(), key=lambda item: item.name):
            if path.name.startswith(".") and path.name.endswith(".partial"):
                _assert_safe_partial_file(path)
                continue
            if not path.name.endswith(".json"):
                raise _TargetHistoryError(
                    f"Unexpected structured replication manifest entry: {path.name}"
                )
            entries.append(_parse_manifest(path))

        previous_hash: str | None = None
        expected_seq = 1
        referenced_bundles: set[str] = set()
        for entry in entries:
            if entry.commit_seq != expected_seq:
                raise _TargetHistoryError(
                    "Structured replication manifest history is not contiguous."
                )
            if entry.previous_head_hash != previous_hash:
                raise _TargetHistoryError(
                    "Structured replication manifest predecessor chain is invalid."
                )
            referenced_bundles.add(entry.bundle_file)
            previous_hash = entry.head_hash
            expected_seq += 1

        allowed_orphan = _bundle_name(
            current_commit_seq,
            current_bundle.bundle_hash,
        )
        present_bundles: set[str] = set()
        for path in sorted(commits_dir.iterdir(), key=lambda item: item.name):
            if path.name.startswith(".") and path.name.endswith(".partial"):
                _assert_safe_partial_file(path)
                continue
            if is_link_boundary(path):
                raise _TargetHistoryError(
                    f"Structured replication bundle is a link boundary: {path.name}"
                )
            try:
                mode = path.stat(follow_symlinks=False).st_mode
            except OSError as exc:
                raise _TargetHistoryError(
                    f"Structured replication bundle identity is unstable: {path.name}"
                ) from exc
            if not stat.S_ISREG(mode):
                raise _TargetHistoryError(
                    f"Structured replication bundle entry is not a file: {path.name}"
                )
            present_bundles.add(path.name)
            if path.name in referenced_bundles or path.name == allowed_orphan:
                continue
            raise _TargetHistoryError(
                f"Unexpected structured replication bundle entry: {path.name}"
            )

        missing = referenced_bundles - present_bundles
        if missing:
            name = sorted(missing)[0]
            raise _TargetHistoryError(
                f"Structured replication manifest references a missing bundle: {name}"
            )
        if entries:
            self._verify_manifest_bundle(commits_dir, entries[-1])
        return tuple(entries)

    @staticmethod
    def _verify_manifest_bundle(
        commits_dir: Path,
        entry: _ManifestEntry,
    ) -> None:
        bundle_path = commits_dir / entry.bundle_file
        try:
            data = _read_regular_file(bundle_path, max_bytes=_BUNDLE_LIMIT)
        except FileNotFoundError as exc:
            raise _TargetHistoryError(
                f"Structured replication manifest references a missing bundle: "
                f"{entry.bundle_file}"
            ) from exc
        try:
            verified = verify_canonical_commit_bundle(data)
        except CanonicalCommitBundleError as exc:
            raise _TargetHistoryError(
                f"Structured replication bundle is invalid: {entry.bundle_file}"
            ) from exc
        if verified.bundle_hash != entry.head_hash:
            raise _TargetHistoryError(
                f"Structured replication bundle hash disagrees with manifest: "
                f"{entry.bundle_file}"
            )
        verified_body = json.loads(verified.data.decode("utf-8"))["body"]
        if (
            verified_body["commit_seq"] != entry.commit_seq
            or verified_body["previous_hash"] != entry.previous_head_hash
        ):
            raise _TargetHistoryError(
                f"Structured replication bundle history disagrees with manifest: "
                f"{entry.bundle_file}"
            )

    @staticmethod
    def _publish_or_verify_bundle(
        path: Path,
        bundle: CanonicalCommitBundle,
    ) -> None:
        try:
            durable_publish_new_bytes(path, bundle.data)
        except FileExistsError:
            pass
        try:
            data = _read_regular_file(path, max_bytes=max(1, len(bundle.data)))
        except FileNotFoundError as exc:
            raise _TargetHistoryError(
                "Structured replication bundle disappeared after publication."
            ) from exc
        if data != bundle.data:
            raise _TargetHistoryError(
                "Existing structured replication bundle bytes do not match staged history."
            )
        try:
            verified = verify_canonical_commit_bundle(data)
        except CanonicalCommitBundleError as exc:
            raise _TargetHistoryError(
                "Published structured replication bundle failed read-back verification."
            ) from exc
        if verified.bundle_hash != bundle.bundle_hash:
            raise _TargetHistoryError(
                "Published structured replication bundle hash changed on read-back."
            )

    @staticmethod
    def _publish_or_verify_exact(path: Path, expected: bytes) -> None:
        try:
            durable_publish_new_bytes(path, expected)
        except FileExistsError:
            pass
        try:
            actual = _read_regular_file(path, max_bytes=max(1, len(expected)))
        except FileNotFoundError as exc:
            raise _TargetHistoryError(
                "Structured replication manifest disappeared after publication."
            ) from exc
        if actual != expected:
            raise _TargetHistoryError(
                "Existing structured replication manifest does not match staged history."
            )

    @staticmethod
    def _verify_committed_entry(
        *,
        entries: tuple[_ManifestEntry, ...],
        commits_dir: Path,
        commit_seq: int,
        bundle: CanonicalCommitBundle,
    ) -> None:
        entry = next(
            (candidate for candidate in entries if candidate.commit_seq == commit_seq),
            None,
        )
        if entry is None or entry.head_hash != bundle.bundle_hash:
            raise _TargetHistoryError(
                "Structured replication target is missing the expected committed entry."
            )
        expected_manifest = _canonical_manifest_bytes(
            commit_seq=commit_seq,
            head_hash=bundle.bundle_hash,
            previous_head_hash=entry.previous_head_hash,
            bundle_file=entry.bundle_file,
        )
        if entry.data != expected_manifest:
            raise _TargetHistoryError(
                "Structured replication committed manifest is not canonical."
            )
        StructuredReplicationPublisher._publish_or_verify_bundle(
            commits_dir / entry.bundle_file,
            bundle,
        )
