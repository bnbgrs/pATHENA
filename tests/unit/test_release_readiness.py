import pytest

from athena.release_readiness import ReleaseReadinessEvidence, assess_release_readiness

_EXACT_SHA = "0123456789abcdef0123456789abcdef01234567"


def _evidence(**overrides: bool | None | str) -> ReleaseReadinessEvidence:
    values: dict[str, bool | None | str] = {
        "exact_sha": _EXACT_SHA,
        "canonical_quality": True,
        "windows_runtime": True,
        "packaging": True,
        "frozen_argv": True,
        "two_exe_topology": True,
        "single_desktop_bounded_workers": True,
        "adaptive_2048_context_reserve": True,
        "windows_lane_lock": True,
        "storage_regressions": True,
    }
    values.update(overrides)
    return ReleaseReadinessEvidence(**values)  # type: ignore[arg-type]


def test_ready_requires_every_release_guard_explicitly_green() -> None:
    result = assess_release_readiness(_evidence())

    assert result.ready is True
    assert result.blockers == ()
    assert result.exact_sha == _EXACT_SHA


@pytest.mark.parametrize(
    "guard",
    [
        "canonical_quality",
        "windows_runtime",
        "packaging",
        "frozen_argv",
        "two_exe_topology",
        "single_desktop_bounded_workers",
        "adaptive_2048_context_reserve",
        "windows_lane_lock",
        "storage_regressions",
    ],
)
def test_false_guard_blocks_promotion(guard: str) -> None:
    result = assess_release_readiness(_evidence(**{guard: False}))

    assert result.ready is False
    assert result.blockers == (guard,)


def test_missing_evidence_blocks_promotion_fail_closed() -> None:
    result = assess_release_readiness(
        _evidence(canonical_quality=None, packaging=None, windows_runtime=None)
    )

    assert result.ready is False
    assert result.blockers == (
        "canonical_quality",
        "windows_runtime",
        "packaging",
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "abc",
        "0123456789ABCDEF0123456789ABCDEF01234567",
        "g123456789abcdef0123456789abcdef01234567",
    ],
)
def test_invalid_exact_sha_fails_closed(value: str) -> None:
    with pytest.raises(ValueError, match="lowercase 40-character hexadecimal Git SHA"):
        assess_release_readiness(_evidence(exact_sha=value))


def test_wrong_evidence_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="evidence must be ReleaseReadinessEvidence"):
        assess_release_readiness(object())  # type: ignore[arg-type]
