"""Scoped fixture injection for offline eval.

Mirrors the project's existing ContextVar pattern (app/graph/context.py,
app/tracing.py run_id_var): a ContextVar carries per-case tool fixtures so the
gateway can short-circuit tool calls to fixed evidence. ContextVar follows the
async task automatically, so concurrent eval cases never cross-contaminate and
the gateway stays stateless. Outside a fixture_scope the var is None and the
gateway behaves exactly as in production.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Dict, Optional

# {tool_name: result_dict}; None means "not in an eval scope".
_fixture_var: ContextVar[Optional[Dict[str, dict]]] = ContextVar(
    "eval_fixtures", default=None
)


def get_active_fixtures() -> Optional[Dict[str, dict]]:
    """Return the active fixture map, or None when not inside a fixture_scope."""
    return _fixture_var.get()


@contextmanager
def fixture_scope(fixtures: Dict[str, dict]):
    """Activate a per-case fixture map for the duration of the block.

    Args:
        fixtures: mapping of tool_name -> result dict the gateway should return.
    """
    token = _fixture_var.set(fixtures or {})
    try:
        yield
    finally:
        _fixture_var.reset(token)
