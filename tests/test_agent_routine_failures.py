"""Focused regression tests for routine failure reporting.

Extracts the actual exception-handler body without importing Home Assistant.
"""
import ast
import logging
from pathlib import Path
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / "custom_components/jarvis_local/agent.py"


class HomeAssistantError(Exception):
    pass


def _run_handler(error):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    handlers = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler)
        and any(
            isinstance(child, ast.Constant)
            and child.value == "Declan routine failed"
            for child in ast.walk(node)
        )
    ]
    # The current handler no longer has the old literal. Identify by its
    # user-facing generic failure response instead.
    if not handlers:
        handlers = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ExceptHandler)
            and "Earlier actions may already have run" in ast.unparse(node)
        ]
    assert len(handlers) == 1
    logger = Mock()
    replies = []
    scope = {
        "HomeAssistantError": HomeAssistantError,
        "ValueError": ValueError,
        "err": error,
        "step": {"name": "jarvis_local_good_morning"},
        "_LOGGER": logger,
        "replies": replies,
    }
    code = compile(ast.fix_missing_locations(ast.Module(body=handlers[0].body, type_ignores=[])), str(SOURCE), "exec")
    exec(code, scope)
    return scope, logger, replies


def test_tuya_rejection_is_warning_without_replay():
    scope, logger, replies = _run_handler(HomeAssistantError("The Tuya cloud rejected the command"))
    assert scope["outcome"] == "failed"
    assert scope["failure"] == "The Tuya cloud rejected the command"
    logger.warning.assert_called_once()
    logger.exception.assert_not_called()
    assert "jarvis_local_good_morning" in str(logger.warning.call_args)
    assert "Check the devices before trying again" in replies[0]


def test_other_home_assistant_error_keeps_diagnostic_traceback():
    scope, logger, replies = _run_handler(HomeAssistantError("Service unavailable"))
    assert scope["outcome"] == "failed"
    logger.exception.assert_called_once()
    logger.warning.assert_not_called()
    assert "Earlier actions may already have run" in replies[0]


def test_value_error_is_not_misclassified_as_tuya():
    scope, logger, replies = _run_handler(ValueError("Invalid routine configuration"))
    assert scope["outcome"] == "failed"
    logger.exception.assert_called_once()
    logger.warning.assert_not_called()
