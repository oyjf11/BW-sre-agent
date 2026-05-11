"""Graph execution context: passes runtime hooks into node wrappers via ContextVar.

ContextVar is used instead of function arguments so that node functions themselves
do not need to accept extra parameters. Values are inherited automatically by
coroutines and threads spawned within the same asyncio task context.
"""
from contextvars import ContextVar
from typing import Callable, Optional

# Callable signature: (event_type, node_name, *, message, level, data) -> None
_node_event_hook: ContextVar[Optional[Callable]] = ContextVar(
    "_node_event_hook", default=None
)


def set_node_event_hook(fn: Callable):
    """Set the event hook for the current async context. Returns a token for reset."""
    return _node_event_hook.set(fn)


def reset_node_event_hook(token) -> None:
    _node_event_hook.reset(token)


def get_node_event_hook() -> Optional[Callable]:
    return _node_event_hook.get()
