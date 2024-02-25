from __future__ import annotations

import asyncio
import logging
from typing import (
    Any,
    Callable,
    Concatenate,
    Coroutine,
    Dict,
    Generic,
    List,
    ParamSpec,
    TypeVar,
)

from amethyst.abc import BaseWidget, Plugin, WidgetPlugin

NoneT = TypeVar("NoneT", bound=None | Coroutine[Any, Any, None])
P = ParamSpec("P")
T = TypeVar("T")

__all__ = ("Event", "DiscordEvent", "EventWidget", "event")

_log = logging.getLogger(__name__)


class Event(Generic[P, NoneT]):
    """Represents a subscribable event and the callback signature.

    Events can be defined by simply making an instance of this class and typing it with the callback parameters.

    Example:
    ```
    on_message: AmethystEvent[[discord.Message], Coroutine] = AmethystEvent("on_message")
    ```
    """

    def __init__(self, name: str, coroutine: bool = True) -> None:
        self._coroutine = coroutine
        self._name = name

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._name

    @property
    def coroutine(self) -> bool:
        return self._coroutine


class DiscordEvent(Event[P, Coroutine[Any, Any, None]]):
    """Represents a normal discord.py event and its parameters."""

    def __init__(self, name: str) -> None:
        super().__init__(name, True)


class EventWidget(WidgetPlugin):
    def __init__(self) -> None:
        self.events: Dict[Event, List[Callable]] = {}

    def register(self, widget: Widget, plugin: Plugin):
        event = widget.event
        _log.debug(
            "Registering event handler '%s.%s' for '%s'",
            plugin.name,
            widget.name,
            event.name,
        )

        if event in self.events:
            handlers = self.events[event]
        else:
            handlers: List[Callable] = []
            self.events[event] = handlers
            setattr(
                self.client,
                event.name,
                lambda *a, **k: asyncio.gather(*(h(plugin, *a, **k) for h in handlers))
                if event.coroutine
                else lambda *a, **k: (h(plugin, *a, **k) for h in handlers),
            )

        handlers.append(widget.callback)

    class Widget(BaseWidget[P, NoneT]):
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


event = EventWidget.Widget.decorate
"""Decorator to designate a regular function to be called when the specified event is invoked.

Parameters
----------
event: `Event`
    The event to subscribe to.
"""
