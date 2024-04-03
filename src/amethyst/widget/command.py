import logging
from typing import Any, Callable, Concatenate, Coroutine, Optional, ParamSpec

from discord import Interaction
from discord.app_commands import Command
from discord.utils import _shorten

from amethyst.amethyst import BaseWidget, Client, Plugin, PluginSelf

P = ParamSpec("P")
Callback = Callable[Concatenate[PluginSelf, Interaction, P], Coroutine[Any, Any, None]]

_log = logging.getLogger(__name__)


class CommandWidget(BaseWidget[Callback[P]]):
    """Represents an Amethyst command.

    These are not usually created manually, instead they are created using the `amethyst.command` decorator.
    """

    def __init__(
        self,
        callback: Callback,
        name: Optional[str] = None,
        description: Optional[str] = None,
        nsfw: bool = False,
    ) -> None:
        super().__init__(callback)  # type: ignore
        self._description = description
        self._name = name
        self.nsfw = nsfw

    @property
    def description(self) -> str:
        if self._description is not None:
            return self._description

        if self.callback.__doc__ is None:
            return "..."
        else:
            return _shorten(self.callback.__doc__)

    def register(self, plugin: Plugin, client: Client) -> None:
        _log.debug("Registering command '%s'", self.name)

        command = Command(
            name=self._name or self.callback.__name__,
            description=self.description,
            callback=self.callback,
            nsfw=self.nsfw,
        )

        command.binding = plugin
        command.add_check(lambda i: plugin.client.guild_allowed(i.guild))
        client.tree.add_command(command)


command = CommandWidget.decorate
"""Decorator to turn a normal function into an application command.

Parameters
------------
name : `str`, optional
    The name of the application command. If not given, it defaults to a lower-case
    version of the callback name.
description : `str`, optional
    The description of the application command. This shows up in the UI to describe
    the application command. If not given, it defaults to the first line of the docstring
    of the callback shortened to 100 characters.
nsfw : `bool`, optional
    Whether the command is NSFW and should only work in NSFW channels. Defaults to `False`.

    Due to a Discord limitation, this does not work on subcommands.
"""
