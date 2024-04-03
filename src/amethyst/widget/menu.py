import inspect
import logging
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union

from discord import Interaction, Member, Message, User, app_commands

from amethyst.amethyst import BaseWidget, Client, Plugin, PluginSelf

SubjectT = TypeVar("SubjectT", Message, User, Member, Union[User, Member])
Callback = Callable[[PluginSelf, Interaction, SubjectT], Coroutine[Any, Any, None]]

_log = logging.getLogger(__name__)


class ContextMenuWidget(BaseWidget[Callback[SubjectT]]):
    """Represents a context menu.

    These are not usually created manually, instead they are created using the `amethyst.context_menu` decorator.
    """

    def __init__(
        self,
        callback: Callback,
        name: Optional[str] = None,
        nsfw: bool = False,
    ) -> None:
        super().__init__(callback)
        self._name = name
        self.nsfw = nsfw

    def wrap(
        self,
        plugin: Plugin,
    ) -> Callable[[Interaction[Client], SubjectT], Coroutine[Any, Any, None]]:
        async def wrapped(interaction: Interaction, subject) -> None:
            await self.callback(plugin, interaction, subject)

        # Copy subject type annotation
        params = inspect.signature(self.callback).parameters
        if len(params) != 3:
            raise ValueError("Context menus require exactly 3 parameters")

        *_, subject = params.values()
        if subject.annotation is subject.empty:
            raise ValueError("Third parameter of context menus must be explicitly typed.")

        wrapped.__annotations__["subject"] = subject.annotation

        return wrapped

    def register(self, plugin: Plugin, client: Client) -> None:
        _log.debug("Registering context menu '%s'", self.name)

        menu = app_commands.ContextMenu(
            name=self._name or self.callback.__name__.title(),
            callback=self.wrap(plugin),
            nsfw=self.nsfw,
        )

        menu.add_check(lambda i: plugin.client.guild_allowed(i.guild))
        client.tree.add_command(menu)


context_menu = ContextMenuWidget.decorate
"""Creates an application command context menu from a regular function.

Parameters
    ------------
    name: `str`, optional
        The name of the context menu command. If not given, it defaults to a title-case
        version of the callback name. Note that unlike regular slash commands this can
        have spaces and upper case characters in the name.
    nsfw: `bool`, optional
        Whether the command is NSFW and should only work in NSFW channels. Defaults to ``False``.

        Due to a Discord limitation, this does not work on subcommands.
"""
