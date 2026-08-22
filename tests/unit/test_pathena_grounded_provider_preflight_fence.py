from __future__ import annotations

import ast
import inspect
import textwrap

from athena.chat.durable_grounded_generation import DurableGroundedGenerationService


def _before_provider_function() -> ast.FunctionDef:
    source = textwrap.dedent(
        inspect.getsource(DurableGroundedGenerationService.send_context_package)
    )
    module = ast.parse(source)
    send = module.body[0]
    assert isinstance(send, ast.FunctionDef)
    before_provider = next(
        node
        for node in send.body
        if isinstance(node, ast.FunctionDef) and node.name == "before_provider"
    )
    return before_provider


def _call_lines(function: ast.FunctionDef, call_name: str) -> tuple[int, ...]:
    return tuple(
        node.lineno
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == call_name
            or isinstance(node.func, ast.Name)
            and node.func.id == call_name
        )
    )


def test_provider_attempt_is_claimed_only_after_deterministic_preflight() -> None:
    before_provider = _before_provider_function()

    callback_lines = _call_lines(before_provider, "on_before_provider_call")
    snapshot_lines = _call_lines(before_provider, "_require_current_snapshot")
    claim_lines = _call_lines(before_provider, "begin_provider_attempt")

    assert len(callback_lines) == 1
    assert len(snapshot_lines) == 2
    assert len(claim_lines) == 1

    callback_line = callback_lines[0]
    claim_line = claim_lines[0]

    assert callback_line < claim_line
    assert all(line < claim_line for line in snapshot_lines)


def test_no_fallible_caller_preflight_runs_after_provider_attempt_claim() -> None:
    before_provider = _before_provider_function()
    claim_lines = _call_lines(before_provider, "begin_provider_attempt")
    assert len(claim_lines) == 1
    claim_line = claim_lines[0]

    later_calls = tuple(
        node
        for node in ast.walk(before_provider)
        if isinstance(node, ast.Call) and node.lineno > claim_line
    )
    assert later_calls == ()
