from __future__ import annotations

import argparse
import dataclasses
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

_COORDINATION_METADATA = frozenset(
    {
        ".pathena/AGENT_COORDINATION.md",
        ".pathena/agent-ledger.json",
    }
)
_NON_PRODUCT_EVIDENCE = frozenset(
    {
        ".github/windows-candidate-request.txt",
    }
)
_ALLOWED_CLASSIFICATIONS = frozenset(
    {"PRODUCT", "COORDINATION_METADATA", "NON_PRODUCT_EVIDENCE"}
)


@dataclasses.dataclass(frozen=True)
class CommitDiff:
    sha: str
    paths: tuple[str, ...]
    classification: str = "PRODUCT"


@dataclasses.dataclass(frozen=True)
class CandidateDiff:
    base_sha: str
    candidate_sha: str
    commits: tuple[CommitDiff, ...]


@dataclasses.dataclass(frozen=True)
class CoordinationGuardResult:
    errors: tuple[str, ...]
    covered_paths: tuple[str, ...]
    metadata_paths: tuple[str, ...]
    evidence_paths: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _mapping_list(value: object, label: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    return tuple(_mapping(item, f"{label}[]") for item in value)


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _string_tuple(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a JSON string array")
    return tuple(value)


def load_candidate_diff(path: Path) -> CandidateDiff:
    payload = _mapping(json.loads(path.read_text(encoding="utf-8")), "diff")
    raw_commits = payload.get("commits")
    if not isinstance(raw_commits, list):
        raise ValueError("diff.commits must be a JSON array")

    commits: list[CommitDiff] = []
    for index, raw_commit in enumerate(raw_commits):
        commit = _mapping(raw_commit, f"diff.commits[{index}]")
        classification = _string(
            commit.get("classification", "PRODUCT"),
            f"diff.commits[{index}].classification",
        ).upper()
        if classification not in _ALLOWED_CLASSIFICATIONS:
            raise ValueError(
                f"diff.commits[{index}].classification is unsupported: {classification}"
            )
        commits.append(
            CommitDiff(
                sha=_string(commit.get("sha"), f"diff.commits[{index}].sha"),
                paths=_string_tuple(
                    commit.get("paths"), f"diff.commits[{index}].paths"
                ),
                classification=classification,
            )
        )

    return CandidateDiff(
        base_sha=_string(payload.get("base_sha"), "diff.base_sha"),
        candidate_sha=_string(payload.get("candidate_sha"), "diff.candidate_sha"),
        commits=tuple(commits),
    )


def _claim_paths(entry: Mapping[str, Any]) -> tuple[str, ...]:
    value = entry.get("paths")
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str) and item)


def _path_matches(path: str, claim_path: str) -> bool:
    normalized = claim_path.rstrip("/")
    return path == normalized or (claim_path.endswith("/") and path.startswith(claim_path))


def _covered_by_any(path: str, entries: Iterable[Mapping[str, Any]]) -> bool:
    return any(
        _path_matches(path, claim_path)
        for entry in entries
        for claim_path in _claim_paths(entry)
    )


def inspect_coordination_coverage(
    ledger: Mapping[str, Any], diff: CandidateDiff
) -> CoordinationGuardResult:
    errors: list[str] = []
    covered: list[str] = []
    metadata: list[str] = []
    evidence: list[str] = []

    ledger_sha = ledger.get("last_known_candidate_sha")
    if ledger_sha not in {diff.base_sha, diff.candidate_sha}:
        errors.append(
            "stale ledger candidate SHA: "
            f"ledger={ledger_sha!r}, diff-base={diff.base_sha!r}, "
            f"diff-candidate={diff.candidate_sha!r}"
        )
    if ledger_sha == diff.candidate_sha and diff.commits:
        errors.append(
            "ledger already names candidate SHA but supplied diff still contains commits"
        )

    active_claims = tuple(
        entry
        for entry in _mapping_list(ledger.get("claims", []), "ledger.claims")
        if entry.get("status") == "CLAIMED"
    )
    completed = _mapping_list(ledger.get("completed", []), "ledger.completed")

    for commit in diff.commits:
        if commit.classification == "COORDINATION_METADATA":
            for path in commit.paths:
                if path not in _COORDINATION_METADATA:
                    errors.append(
                        f"commit {commit.sha} misclassifies product path as coordination metadata: {path}"
                    )
                else:
                    metadata.append(path)
            continue

        if commit.classification == "NON_PRODUCT_EVIDENCE":
            for path in commit.paths:
                if path not in _NON_PRODUCT_EVIDENCE:
                    errors.append(
                        f"commit {commit.sha} uses unapproved non-product evidence path: {path}"
                    )
                else:
                    evidence.append(path)
            continue

        matching_completed = [
            entry
            for entry in completed
            if entry.get("status") == "COMPLETED"
            and entry.get("result_candidate_sha") == commit.sha
        ]
        for path in commit.paths:
            if _covered_by_any(path, active_claims) or _covered_by_any(
                path, matching_completed
            ):
                covered.append(path)
            else:
                errors.append(f"uncovered product mutation at {commit.sha}: {path}")

    return CoordinationGuardResult(
        errors=tuple(errors),
        covered_paths=tuple(sorted(set(covered))),
        metadata_paths=tuple(sorted(set(metadata))),
        evidence_paths=tuple(sorted(set(evidence))),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail closed when candidate mutations lack coordination-ledger coverage."
    )
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--diff", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        ledger = _mapping(
            json.loads(args.ledger.read_text(encoding="utf-8")), "ledger"
        )
        diff = load_candidate_diff(args.diff)
        result = inspect_coordination_coverage(ledger, diff)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"coordination guard: FAIL: {exc}")
        return 1

    if result.ok:
        print(
            "coordination guard: PASS: "
            f"covered={len(result.covered_paths)} "
            f"metadata={len(result.metadata_paths)} "
            f"evidence={len(result.evidence_paths)}"
        )
        return 0

    for error in result.errors:
        print(f"coordination guard: FAIL: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
