from __future__ import annotations

import argparse
import inspect
import uuid

import pytest

from athena import __main__ as launcher
from athena.cli import parser as parser_module


def test_launcher_reexports_dedicated_parser_boundary() -> None:
    assert launcher.build_parser is parser_module.build_parser
    assert launcher.build_parser.__module__ == "athena.cli.parser"

    launcher_source = inspect.getsource(launcher)
    parser_source = inspect.getsource(parser_module)

    assert "def build_parser(" not in launcher_source
    assert "def build_parser(" in parser_source
    assert "AthenaApplication" not in parser_source


def test_extracted_parser_preserves_typed_core_commands() -> None:
    parser = launcher.build_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.prog == "athena"

    chat = parser.parse_args(["chat", "new"])
    assert chat.command == "chat"
    assert chat.chat_command == "new"

    job_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    job = parser.parse_args(["job", "show", str(job_id)])
    assert job.command == "job"
    assert job.job_command == "show"
    assert job.job_id == job_id


@pytest.mark.parametrize(
    "payload",
    [
        '{"value": NaN}',
        '{"value": Infinity}',
        '{"value": -Infinity}',
        '{"value": 1e309}',
        '{"nested": [{"value": -1e309}]}',
    ],
)
def test_json_object_argument_rejects_non_finite_numbers(payload: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="finite"):
        parser_module._json_object_argument(payload)


def test_json_object_argument_preserves_finite_nested_payload() -> None:
    payload = '{"value": 1.25, "nested": [0, -2.5, {"enabled": true}]}'

    assert parser_module._json_object_argument(payload) == {
        "value": 1.25,
        "nested": [0, -2.5, {"enabled": True}],
    }


@pytest.mark.parametrize("value", ["nan", "NaN", "inf", "+inf", "-inf", "1e309"])
def test_finite_float_argument_rejects_non_finite_values(value: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="finite"):
        parser_module._finite_float_argument(value)


def test_review_accept_all_uses_finite_confidence_boundary() -> None:
    parser = launcher.build_parser()

    args = parser.parse_args(["review", "accept-all", "--min-confidence", "0.75"])

    assert args.min_confidence == 0.75
    with pytest.raises(SystemExit):
        parser.parse_args(["review", "accept-all", "--min-confidence", "nan"])
