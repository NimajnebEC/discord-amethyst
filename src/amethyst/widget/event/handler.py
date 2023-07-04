from __future__ import annotations

import inspect
from typing import Any, Callable, Coroutine, Generic, ParamSpec, TypeVar

from amethyst.widget.abc import AmethystPlugin, Callback, CallbackWidget

PluginT = TypeVar("PluginT", bound=AmethystPlugin)
P = ParamSpec("P")
T = TypeVar("T")

Coro = Coroutine[Any, Any, T]
EventCallback = Callback[PluginT, P, Coro[T]]


class AmethystEventHandler(CallbackWidget[PluginT, P, Coro[T]]):
    """Represents a event handler, consisting of a callback function and the `AmethystEvent` that its subscribed to."""


class AmethystEvent(Generic[P]):
    """Represents a subscribable event and the parameters a callback should include.

    Events can be defined by simply making an instance of this class and typing it with the callback parameters.

    Example:
    ```
    on_message: AmethystEvent[discord.Message] = AmethystEvent("on_message")
    ```
    """

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._name


def event(
    event: AmethystEvent[P],
) -> Callable[[EventCallback[PluginT, P, T]], AmethystEventHandler[PluginT, P, T]]:
    """Decorator to create an `AmethystEventHandler` from a regular function.

    Parameters
    ----------
    event : AmethystEvent
        The event to subscribe to.
    """

    def decorator(
        func: EventCallback[PluginT, P, T]
    ) -> AmethystEventHandler[PluginT, P, T]:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Event function must be a coroutine function")

        return AmethystEventHandler(func)

    return decorator
