from __future__ import annotations

from typing import Any, Callable, Concatenate, Coroutine, Generic, ParamSpec, TypeVar

from amethyst.abc import Plugin, Widget
from amethyst.client import Client

NoneT = TypeVar("NoneT", bound=None | Coroutine[Any, Any, None])
P = ParamSpec("P")
T = TypeVar("T")


__all__ = ("Event", "DiscordEvent", "EventWidget", "event")


class Event(Generic[P, NoneT]):
    """Represents a subscribable event and the callback signature.

    Events can be defined by simply making an instance of this class and typing it with the callback parameters.

    Example:
    ```
    on_message: AmethystEvent[[discord.Message], Coroutine] = AmethystEvent("on_message")
    ```
    """

    def __init__(self, name: str) -> None:
        """Represents a subscribable event and the callback signature.

        Parameters
        ----------
        name: `str`
            The name of this event.
        """
        self._name = name

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._name


class DiscordEvent(Event[P, Coroutine[Any, Any, None]]):
    """Represents a normal discord.py event and its parameters."""

    def __init__(self, name: str) -> None:
        super().__init__(name)


class EventWidget(Widget[P, NoneT]):
    """Represents a event widget, consisting of a callback function and the `AmethystEvent` that its subscribed to.

    These are not usually created manually, instead they are created using the `amethyst.event` decorator.
    """

    def __init__(
        self,
        callback: Callable[Concatenate[Plugin, P], NoneT],
        event: Event[P, NoneT],
    ) -> None:
        super().__init__(callback)
        self._event = event

    @property
    def event(self) -> Event[P, NoneT]:
        """The event this handler is subscribed to."""
        return self._event

    def register(self, plugin: Plugin, client: Client) -> None:
        setattr(client, self.event.name, self.bound(plugin))


event = EventWidget.decorate
"""Decorator to designate a regular function to be called when the specified event is invoked.

Parameters
----------
event: `Event`
    The event to subscribe to.
"""
