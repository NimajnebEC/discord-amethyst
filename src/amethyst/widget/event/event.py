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

import discord

from amethyst.amethyst import BaseWidget, Client, Plugin, PluginSelf

__all__ = ("Event", "EventWidget", "event")

P = ParamSpec("P")
T = TypeVar("T")

Coro = Coroutine[Any, Any, None]
Callback = Callable[Concatenate[PluginSelf, P], Coro]

_log = logging.getLogger(__name__)


class Event(Generic[P]):
    """Represents a subscribable event and the callback signature.

    Events can be defined by simply making an instance of this class and typing it with the callback parameters.

    Example:
    ```
    on_message: AmethystEvent[[discord.Message], Coroutine] = AmethystEvent("on_message")
    ```
    """

    def __init__(
        self,
        name: str,
        guild: Callable[P, discord.Guild | int | None] | None = None,
    ) -> None:
        self._guild = guild or (lambda *_: None)
        self._name = name

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._name

    def get_guild(self, *args) -> discord.Guild | int | None:
        return self._guild(*args)  # type: ignore


class EventWidget(BaseWidget[Callback[P]]):
    """Represents a event widget, consisting of a callback function and the `AmethystEvent` that its subscribed to.

    These are not usually created manually, instead they are created using the `amethyst.event` decorator.
    """

    def __init__(self, callback: Callback[P], event: Event[P]) -> None:
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

        if self.event.name == "setup_hook":
            if plugin is None:
                client._setup_hooks.append(self.callback)
            else:
                client._setup_hooks.append(lambda: self.callback(plugin))  # type: ignore
            return

        async def wrapper(*args) -> None:
            try:
                await self.callback(*args)  # type: ignore
            except Exception:
                _log.error("Error handling '%s': ", self.name, exc_info=True)

        def handler(*args) -> bool:
            guild = self.event.get_guild(*args)
            if guild is None or client.guild_allowed(guild):
                if plugin is not None:  # To support anonymous events using Client.event
                    args = (plugin, *args)

                client.create_task(wrapper(*args))
            else:
                _log.debug(
                    f"Skipping invokation of event '{self.name}' as guild '{guild}' is not allowed."
                )
            return False

        client.create_task(client.wait_for(self.event, check=handler))  # type: ignore


event = EventWidget.decorate
"""Decorator to designate a regular function to be called when the specified event is invoked.

Parameters
----------
event: `Event`
    The event to subscribe to.
"""
