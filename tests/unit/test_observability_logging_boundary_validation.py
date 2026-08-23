from __future__ import annotations

import logging

import pytest

from athena.observability.logging import _validated_log_level


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        "",
        "   ",
        "not-a-level",
        -1,
        1.5,
        None,
        object(),
    ],
)
def test_logging_level_boundary_rejects_malformed_values(value: object) -> None:
    with pytest.raises(ValueError):
        _validated_log_level(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("info", logging.INFO),
        (" WARNING ", logging.WARNING),
        (logging.DEBUG, logging.DEBUG),
        (logging.NOTSET, logging.NOTSET),
        (37, 37),
    ],
)
def test_logging_level_boundary_accepts_supported_values(
    value: object,
    expected: int,
) -> None:
    assert _validated_log_level(value) == expected
