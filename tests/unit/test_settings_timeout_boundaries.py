from __future__ import annotations

import math
from pathlib import Path
from typing import Any, cast

import pytest

from athena.config.settings import AthenaSettings, ConfigurationError


@pytest.mark.parametrize(
    "field,value",
    [
        pytest.param("model_request_timeout_seconds", True, id="request-true"),
        pytest.param("model_request_timeout_seconds", False, id="request-false"),
        pytest.param("model_request_timeout_seconds", 0, id="request-zero"),
        pytest.param("model_request_timeout_seconds", -1, id="request-negative"),
        pytest.param("model_request_timeout_seconds", math.nan, id="request-nan"),
        pytest.param("model_request_timeout_seconds", math.inf, id="request-inf"),
        pytest.param("model_request_timeout_seconds", -math.inf, id="request-neg-inf"),
        pytest.param("model_request_timeout_seconds", "2", id="request-text"),
        pytest.param("model_generation_timeout_seconds", True, id="generation-true"),
        pytest.param("model_generation_timeout_seconds", 0, id="generation-zero"),
        pytest.param("model_generation_timeout_seconds", math.nan, id="generation-nan"),
        pytest.param("model_generation_timeout_seconds", math.inf, id="generation-inf"),
    ],
)
def test_direct_settings_reject_invalid_timeout_scalars(
    field: str,
    value: object,
    tmp_path: Path,
) -> None:
    kwargs: dict[str, Any] = {
        "local_root": tmp_path,
        field: value,
    }

    with pytest.raises(ConfigurationError, match="finite number greater than zero"):
        AthenaSettings(**kwargs)


@pytest.mark.parametrize(
    "request_timeout,generation",
    [
        pytest.param(1, 2, id="integers"),
        pytest.param(0.25, 300.5, id="floats"),
    ],
)
def test_direct_settings_canonicalize_valid_timeout_numbers(
    request_timeout: object,
    generation: object,
    tmp_path: Path,
) -> None:
    settings = AthenaSettings(
        local_root=tmp_path,
        model_request_timeout_seconds=cast(Any, request_timeout),
        model_generation_timeout_seconds=cast(Any, generation),
    )

    assert settings.model_request_timeout_seconds == float(cast(Any, request_timeout))
    assert settings.model_generation_timeout_seconds == float(cast(Any, generation))
    assert isinstance(settings.model_request_timeout_seconds, float)
    assert isinstance(settings.model_generation_timeout_seconds, float)


@pytest.mark.parametrize(
    "name,value",
    [
        pytest.param("ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS", "nan", id="request-nan"),
        pytest.param("ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS", "inf", id="request-inf"),
        pytest.param("ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS", "+inf", id="request-plus-inf"),
        pytest.param("ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS", "-inf", id="request-neg-inf"),
        pytest.param("ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS", "0", id="request-zero"),
        pytest.param("ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS", "-1", id="request-negative"),
        pytest.param("ATHENA_MODEL_GENERATION_TIMEOUT_SECONDS", "NaN", id="generation-nan"),
        pytest.param("ATHENA_MODEL_GENERATION_TIMEOUT_SECONDS", "Infinity", id="generation-inf"),
        pytest.param("ATHENA_MODEL_GENERATION_TIMEOUT_SECONDS", "0", id="generation-zero"),
    ],
)
def test_environment_rejects_invalid_timeout_numbers(
    name: str,
    value: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(tmp_path))
    monkeypatch.setenv(name, value)

    with pytest.raises(ConfigurationError, match="finite number greater than zero"):
        AthenaSettings.from_environment()


def test_environment_accepts_finite_positive_timeouts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(tmp_path))
    monkeypatch.setenv("ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS", "0.5")
    monkeypatch.setenv("ATHENA_MODEL_GENERATION_TIMEOUT_SECONDS", "600")

    settings = AthenaSettings.from_environment()

    assert settings.model_request_timeout_seconds == 0.5
    assert settings.model_generation_timeout_seconds == 600.0
