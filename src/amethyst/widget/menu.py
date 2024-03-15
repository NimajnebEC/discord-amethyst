import inspect
import logging
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union

from discord import Interaction, Member, Message, User, app_commands

from amethyst.amethyst import BaseWidget, Client, Plugin

SubjectT = TypeVar("SubjectT", Message, User, Member, Union[User, Member])

_log = logging.getLogger(__name__)


class ContextMenuWidget(BaseWidget[[Interaction, SubjectT], Coroutine[Any, Any, None]]):
    def __init__(
        self,
        callback: Callable[[Any, Interaction, SubjectT], Coroutine[Any, Any, None]],
        name: Optional[str] = None,
        nsfw: bool = False,
    ) -> None:
        super().__init__(callback)
        self._name = name
        self.nsfw = nsfw

    def bound(
        self, plugin: Plugin
    ) -> Callable[[Interaction[Client], SubjectT], Coroutine[Any, Any, None]]:
        async def bound(interaction: Interaction, subject) -> None:
            await self.callback(plugin, interaction, subject)

        # Copy subject type annotation
        params = inspect.signature(self.callback).parameters
        if len(params) != 3:
            raise ValueError("Context menus require exactly 3 parameters")

        *_, subject = params.values()
        if subject.annotation is subject.empty:
            raise ValueError("Third parameter of context menus must be explicityly typed.")

        bound.__annotations__["subject"] = subject.annotation

        return bound

    def register(self, plugin: Plugin, client: Client) -> None:
        _log.debug("Registering context menu '%s'", self.name)

        menu = app_commands.ContextMenu(
            name=self._name or self.callback.__name__.title(),
            callback=self.bound(plugin),
            nsfw=self.nsfw,
        )

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
