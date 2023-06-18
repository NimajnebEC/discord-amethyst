from discord.app_commands.commands import P, T, CommandCallback, GroupT
from discord.app_commands import describe, locale_str
from typing import Callable, Generic
from discord import app_commands
from abc import ABC

__all__ = ("AmethystPlugin", "AmethystCommand", "command", "describe")


class AmethystPlugin(ABC):
    """Base class for Amethyst plugins to inhert from.

    Plugins found in a client's search modules will be instantiated with dependencies injected into constructor parameters.
    """


class AmethystCommand(app_commands.Command, Generic[GroupT, P, T]):
    """Represents an Amethyst slash command.

    These are usually not created manually, instead they are created using the `amethyst.command` decorator.
    """


def command(
    name: str | locale_str | None = None,
    description: str | locale_str | None = None,
    hybrid: bool = False,
    nsfw: bool = False,
) -> Callable[[CommandCallback[GroupT, P, T]], AmethystCommand[GroupT, P, T]]:
    def decorator(func: CommandCallback[GroupT, P, T]) -> AmethystCommand[GroupT, P, T]:
        ...

    return decorator
