from __future__ import annotations

import inspect
from typing import Any, Callable, Coroutine, Generic, ParamSpec, TypeVar

from amethyst.widget.abc import AmethystPlugin, Callback, CallbackWidget

PluginT = TypeVar("PluginT", bound=AmethystPlugin)
NoneT = TypeVar("NoneT", bound=None | Coroutine[Any, Any, None])
P = ParamSpec("P")
T = TypeVar("T")

HandlerCallback = Callback[PluginT, P, NoneT]

__all__ = ("AmethystEvent", "DiscordPyEvent", "AmethystEventHandler", "event")


class AmethystEvent(Generic[P, NoneT]):
    """Represents a subscribable event and the callback signature.

    Events can be defined by simply making an instance of this class and typing it with the callback parameters.

    Example:
    ```
    on_message: AmethystEvent[[discord.Message], Coroutine] = AmethystEvent("on_message")
    ```
    """

    def __init__(self, name: str, is_coroutine: bool = False) -> None:
        """Represents a subscribable event and the callback signature.

        Parameters
        ----------
        name: `str`
            The name of this event.
        is_coroutine : `bool`, optional
            Wether this event will be called asynchronously, by default False
        """
        self._is_coroutine: bool = is_coroutine
        self._name = name

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._name

    @property
    def is_coroutine(self) -> bool:
        """Wether the event is a coroutine."""
        return self._is_coroutine


class DiscordPyEvent(AmethystEvent[P, Coroutine]):
    """Represents a normal Discord.py event and its parameters."""

    def __init__(self, name: str) -> None:
        super().__init__(name, True)


class AmethystEventHandler(CallbackWidget[PluginT, P, NoneT]):
    """Represents a event handler, consisting of a callback function and the `AmethystEvent` that its subscribed to.

    These are not usually created manually, instead they are created using the `amethyst.event` decorator.
    """

    def __init__(
        self,
        event: AmethystEvent[P, NoneT],
        callback: Callback[PluginT, P, NoneT],
        name: str | None = None,
    ) -> None:
        """Represents a event handler, consisting of a callback function and the `AmethystEvent` that its subscribed to.

        These are not usually created manually, instead they are created using the `amethyst.event` decorator.

        Parameters
        ----------
        event: `AmethystEvent[P, NoneT]`
            The event to subscribe to.
        callback : `Callable[Concatenate[PluginT, P], NoneT] | Callable[P, NoneT]`
            The callback function that will be invoked for this event.
        name: `str`, optional
            The name of this event handler widget, by default None
        """
        super().__init__(callback, name)
        self._event = event

    @property
    def event(self) -> AmethystEvent[P, NoneT]:
        """The event this handler is subscribed to."""
        return self._event


def event(
    event: AmethystEvent[P, NoneT],
) -> Callable[
    [HandlerCallback[PluginT, P, NoneT]], AmethystEventHandler[PluginT, P, NoneT]
]:
    """Decorator to designate a regular function to be called when the specified event is invoked.

    Parameters
    ----------
    event: `AmethystEvent`
        The event to subscribe to.
    """

    def decorator(
        func: HandlerCallback[PluginT, P, NoneT]
    ) -> AmethystEventHandler[PluginT, P, NoneT]:
        if event._is_coroutine != inspect.iscoroutinefunction(func):
            raise TypeError(
                f"Function must {'' if event._is_coroutine else 'not '}be a coroutine."
            )

        return AmethystEventHandler(event, func)

    return decorator
