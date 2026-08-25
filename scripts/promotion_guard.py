from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


CANDIDATE_REF = "refs/heads/bot/pathena-candidate"
REQUIRED_PATHS = (Path(".github/workflows/quality.yml"),)
FORBIDDEN_PATHS = (
    Path(".github/workflows/pathena-bootstrap.yml"),
    Path(".github/workflows/pathena-slice-gate.yml"),
    Path(".pathena-bootstrap"),
)
FORBIDDEN_TREES = (Path(".pathena/bootstrap"),)


@dataclass(frozen=True)
class PromotionGuardResult:
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def inspect_promotion_tree(
    root: Path,
    *,
    actual_ref: str | None = None,
    expected_ref: str = CANDIDATE_REF,
) -> PromotionGuardResult:
    root = root.resolve()
    errors: list[str] = []

    if actual_ref is not None and actual_ref != expected_ref:
        errors.append(
            f"promotion guard expected ref {expected_ref!r}, got {actual_ref!r}"
        )

    for required in REQUIRED_PATHS:
        if not (root / required).is_file():
            errors.append(f"required promotion path is missing: {required.as_posix()}")

    for forbidden in FORBIDDEN_PATHS:
        if (root / forbidden).exists():
            errors.append(f"legacy promotion path must stay absent: {forbidden.as_posix()}")

    for forbidden_tree in FORBIDDEN_TREES:
        candidate = root / forbidden_tree
        if candidate.exists():
            errors.append(
                "legacy bootstrap payload tree must stay absent: "
                f"{forbidden_tree.as_posix()}"
            )

    return PromotionGuardResult(errors=tuple(errors))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail closed if candidate promotion could revive legacy bootstrap state."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--actual-ref")
    parser.add_argument("--expected-ref", default=CANDIDATE_REF)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = inspect_promotion_tree(
        args.root,
        actual_ref=args.actual_ref,
        expected_ref=args.expected_ref,
    )
    if result.ok:
        print("promotion guard: PASS")
        return 0
    for error in result.errors:
        print(f"promotion guard: FAIL: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
