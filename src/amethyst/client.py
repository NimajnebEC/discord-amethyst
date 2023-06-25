import logging
from typing import Any, Self

import discord
import dynamicpy
from discord import app_commands
from discord.abc import Snowflake

from amethyst import errors
from amethyst.utils import is_dict_subset
from amethyst.widget import AmethystCommand

__all__ = ("AmethystClient",)

_default_modules = [".commands"]

_log = logging.getLogger(__name__)


class AmethystClient(discord.Client):
    def __init__(
        self,
        intents: discord.Intents,
        *,
        search_modules: list[str] | None = None,
        **options: Any,
    ) -> None:
        super().__init__(intents=intents, **options)
        self._home_package: str | None = self._get_home_package()
        self._tree: app_commands.CommandTree[Self] = app_commands.CommandTree(self)
        self._loader: dynamicpy.DynamicLoader = self._build_loader()

        self._load_modules(search_modules or _default_modules)

    @property
    def home_package(self) -> str | None:
        """The parent package of the module where this client was instantiated. Is `None` if it was a top-level module."""
        return self._home_package

    @property
    def tree(self) -> app_commands.CommandTree:
        """The command tree responsible for handling the application commands in this bot."""
        return self._tree

    def register_command(self, command: AmethystCommand) -> None:
        """Register an instance of `AmethystCommand` to the client.

        Parameters
        ----------
        command : AmethystCommand
            The command to register.
        """
        _log.debug("Registering command '%s'", command.name)
        self._tree.add_command(command)

    async def commands_in_sync(self, guild: Snowflake | None = None) -> bool:
        """Checks if the the commands locally registered to this client are in sync with the commands on discord.

        Parameters
        ----------
        guild : Snowflake, optional
            The guild to check commands from. If left blank, checks global commands.

        Returns
        -------
        bool
            Returns true if the local commands match the remote commands.
        """
        local = {c.name: c.to_dict() for c in self.tree.get_commands(guild=guild)}
        remote = {
            c.name: {
                "nsfw": c.nsfw,
                "dm_permission": c.dm_permission,
                "default_member_permissions": c.default_member_permissions,
                **c.to_dict(),
            }
            for c in await self.tree.fetch_commands(guild=guild)
        }

        # Check for commands that only appear in one location
        if len(set(local.keys()).symmetric_difference(remote.keys())) > 0:
            return False

        # Check for changes to existing commands
        return is_dict_subset(remote, local)

    def _build_loader(self) -> dynamicpy.DynamicLoader:
        """Builds a DynamicLoader for registering widgets to the client."""
        loader = dynamicpy.DynamicLoader()

        loader.register_type_handler(lambda _, v: self.register_command(v), AmethystCommand)

        return loader

    def _load_modules(self, search_modules: list[str]) -> None:
        """Loads the modules specified in `search_modules` using the client's DynamicLoader."""
        for module in search_modules:
            if self.home_package is None and module.startswith("."):
                module = module[1:]
            self._loader.load_module(module, self.home_package)

    def _get_home_package(self) -> str | None:
        """Return the home package of the application."""
        try:
            module = dynamicpy.get_foreign_module()

            if dynamicpy.is_package(module):
                package = module
            else:
                package = dynamicpy.get_module_parent(module)

            _log.debug("Home package located as '%s'", package)
            return package
        except dynamicpy.NoParentError:
            _log.debug("Instantiating module is top-level.")
            return None
        except ImportError as e:
            _log.error("Error locating home package: %s", e)
            raise errors.ModuleLocateError("Error locating home package") from e
