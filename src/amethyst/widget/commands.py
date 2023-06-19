import inspect
from typing import Any, Callable, Concatenate, Coroutine, ParamSpec, TypeVar

from discord import Interaction
from discord.app_commands import Command, describe, locale_str
from discord.app_commands.commands import Group
from discord.utils import MISSING, _shorten

__all__ = ("AmethystCommand", "command", "describe")

T = TypeVar("T")
P = ParamSpec("P")

Coro = Coroutine[Any, Any, T]
CommandCallback = Callable[Concatenate[Interaction[Any], P], Coro[T]]


class AmethystCommand(Command[Any, P, T]):
    """Represents an Amethyst command.

    These are usually not created manually, instead they are created using the `amethyst.command` decorator.
    """

    def __init__(
        self,
        *,
        name: str | locale_str,
        description: str | locale_str,
        callback: CommandCallback[P, T],
        hybrid: bool = False,
        nsfw: bool = False,
        parent: Group | None = None,
        guild_ids: list[int] | None = None,
        auto_locale_strings: bool = True,
        extras: dict[Any, Any] = MISSING
    ):
        self._hybrid: bool = hybrid
        super().__init__(
            name=name,
            description=description,
            callback=callback,
            nsfw=nsfw,
            parent=parent,
            guild_ids=guild_ids,
            auto_locale_strings=auto_locale_strings,
            extras=extras,
        )


def command(
    name: str | locale_str | None = None,
    description: str | locale_str | None = None,
    hybrid: bool = False,
    nsfw: bool = False,
) -> Callable[[CommandCallback[P, T]], AmethystCommand[P, T]]:
    """Creates an `AmethystCommand` from a regular function.

    Parameters
    ------------
    name : str, optional
        The name of the application command. If not given, it defaults to a lower-case
        version of the callback name.
    description : str, optional
        The description of the application command. This shows up in the UI to describe
        the application command. If not given, it defaults to the first line of the docstring
        of the callback shortened to 100 characters.
    hybrid : bool, optional
        Wether the command should also be usable as a message command. Defaults to `False`.
    nsfw : bool, optional
        Whether the command is NSFW and should only work in NSFW channels. Defaults to `False`.

        Due to a Discord limitation, this does not work on subcommands.
    """

    def decorator(func: CommandCallback[P, T]) -> AmethystCommand[P, T]:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Command function must be a coroutine function")

        if description is None:
            if func.__doc__ is None:
                desc = "..."
            else:
                desc = _shorten(func.__doc__)
        else:
            desc = description

        return AmethystCommand(
            name=name if name is not None else func.__name__,
            description=desc,
            callback=func,
            parent=None,
            hybrid=hybrid,
            nsfw=nsfw,
        )

    return decorator
