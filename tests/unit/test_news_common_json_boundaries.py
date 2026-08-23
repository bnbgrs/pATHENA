from __future__ import annotations

import pytest

from athena.news.common import _json_object
from athena.news.models import NewsError


@pytest.mark.parametrize(
    "raw",
    ['{"value":NaN}', '{"value":Infinity}', '{"value":1,"value":2}'],
)
def test_news_json_object_rejects_non_strict_json(raw: str) -> None:
    with pytest.raises(NewsError, match="strict durable JSON"):
        _json_object(raw)


def test_news_json_object_accepts_nested_strict_object() -> None:
    assert _json_object('{"nested":{"value":1}}') == {"nested": {"value": 1}}
