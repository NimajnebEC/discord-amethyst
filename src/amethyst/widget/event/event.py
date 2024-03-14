from __future__ import annotations

import logging
from typing import (
    Any,
    Callable,
    Concatenate,
    Coroutine,
    Generic,
    ParamSpec,
    TypeVar,
)

from amethyst.amethyst import BaseWidget, Client, Plugin

__all__ = ("Event", "EventWidget", "event")

Coro = Coroutine[Any, Any, None]
P = ParamSpec("P")
T = TypeVar("T")

_log = logging.getLogger(__name__)


class Event(Generic[P]):
    """Represents a subscribable event and the callback signature.

    Events can be defined by simply making an instance of this class and typing it with the callback parameters.

    Example:
    ```
    on_message: AmethystEvent[[discord.Message], Coroutine] = AmethystEvent("on_message")
    ```
    """

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._name


class EventWidget(BaseWidget[P, Coro]):
    """Represents a event widget, consisting of a callback function and the `AmethystEvent` that its subscribed to.

    These are not usually created manually, instead they are created using the `amethyst.event` decorator.
    """

    def __init__(
        self,
        callback: Callable[Concatenate[Plugin, P], Coro],
        event: Event[P],
    ) -> None:
        super().__init__(callback)
        self._event = event

    @property
    def event(self) -> Event[P]:
        """The event this handler is subscribed to."""
        return self._event

    def register(self, plugin: Plugin | None, client: Client) -> None:
        _log.debug(
            "Registering event handler '%s' for '%s'",
            self.name,
            self.event.name,
        )

        async def wrapper(*args) -> None:
            try:
                await self.callback(*args)  # type: ignore
            except Exception:
                _log.error("Error handling '%s': ", self.name, exc_info=True)

        def handler(*args) -> bool:
            if plugin is not None:  # To support anonymous events using Client.event
                args = (plugin, *args)

            client.create_task(wrapper(*args))
            return False

        client.create_task(client.wait_for(self.event, check=handler))  # type: ignore


event = EventWidget.decorate
"""Decorator to designate a regular function to be called when the specified event is invoked.

Parameters
----------
event: `Event`
    The event to subscribe to.
"""
