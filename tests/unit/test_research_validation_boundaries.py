from __future__ import annotations

import pytest

from athena.research.errors import ResearchStateError
from athena.research.validation import _json_string_array


@pytest.mark.parametrize(
    "raw",
    ['[""]', '["   "]', '["alpha "]', '[" alpha"]', '["alpha","alpha"]'],
)
def test_research_string_array_rejects_noncanonical_or_duplicate_values(raw: str) -> None:
    with pytest.raises(ResearchStateError):
        _json_string_array(raw, "filters")


def test_research_string_array_preserves_canonical_order() -> None:
    assert _json_string_array('["alpha","beta"]', "filters") == ("alpha", "beta")
