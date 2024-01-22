import inspect
from typing import Any, Callable, Concatenate, Coroutine, ParamSpec, Self, TypeVar

from discord import Interaction
from discord.app_commands import Command, describe, locale_str
from discord.app_commands.commands import Group
from discord.utils import MISSING, _shorten

from amethyst.widget.abc import AmethystPlugin, Callback, CallbackWidget

__all__ = ("AmethystCommand", "command", "describe")

PluginT = TypeVar("PluginT", bound=AmethystPlugin)
Coro = Coroutine[Any, Any, None]
P = ParamSpec("P")

CommandCallback = Callback[PluginT, Concatenate[Interaction[Any], P], Coro]


class AmethystCommand(
    CallbackWidget[PluginT, Concatenate[Interaction[Any], P], Coro],
    Command[PluginT, P, None],  # type: ignore
):
    """Represents an Amethyst command.

    These are not usually created manually, instead they are created using the `amethyst.command` decorator.
    """

    def __init__(
        self,
        *,
        name: str | locale_str,
        description: str | locale_str,
        callback: CommandCallback[PluginT, P],
        nsfw: bool = False,
        parent: Group | None = None,
        guild_ids: list[int] | None = None,
        auto_locale_strings: bool = True,
        extras: dict[Any, Any] = MISSING,
    ):
        """Represents an Amethyst command.

        These are not usually created manually, instead they are created using the `amethyst.command` decorator.

        Parameters
        -----------
        name: `str | locale_str`
            The name of the application command.
        description: `str | locale_str`
            The description of the application command. This shows up in the UI to describe the application command.
        callback: `Callable[Concatenate[PluginT, P], Coroutine[Any, Any, T]] | Callable[P, Coroutine[Any, Any, T]]`
            The coroutine that is executed when the command is called.
        auto_locale_strings: `bool`
            If this is set to ``True``, then all translatable strings will implicitly
            be wrapped into `locale_str` rather than `str`. This could
            avoid some repetition and be more ergonomic for certain defaults such
            as default command names, command descriptions, and parameter names.
            Defaults to ``True``.
        nsfw: `bool`
            Whether the command is NSFW and should only work in NSFW channels.
            Defaults to ``False``.

            Due to a Discord limitation, this does not work on subcommands.
        parent: `Group`, optional
            The parent application command. ``None`` if there isn't one.
        extras: `dict`
            A dictionary that can be used to store extraneous data.
            The library will not touch any values or keys within this dictionary.
        """
        CallbackWidget.__init__(self, callback, name)  # type: ignore
        Command.__init__(
            self,
            name=name,
            description=description,
            callback=callback,
            nsfw=nsfw,
            parent=parent,
            guild_ids=guild_ids,
            auto_locale_strings=auto_locale_strings,
            extras=extras,
        )

    def _bound_copy(self, binding: AmethystPlugin) -> Self:
        return self._copy_with(parent=self.parent, binding=binding)  # type: ignore


def command(
    name: str | locale_str | None = None,
    description: str | locale_str | None = None,
    nsfw: bool = False,
) -> Callable[[CommandCallback[PluginT, P]], AmethystCommand[PluginT, P]]:
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

    def decorator(func: CommandCallback[PluginT, P]) -> AmethystCommand[PluginT, P]:
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
            nsfw=nsfw,
        )

    return decorator
