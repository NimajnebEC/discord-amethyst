import logging
from typing import Any, Self, Type

import discord
import dynamicpy
from discord import app_commands
from discord.abc import Snowflake

from amethyst import error
from amethyst.util import is_dict_subset
from amethyst.widget import AmethystCommand, AmethystPlugin

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
        self._search_modules = search_modules or _default_modules
        self._home_package: str | None = self._get_home_package()
        self._loader: dynamicpy.DynamicLoader = self._build_loader()
        self._tree: app_commands.CommandTree[Self] = app_commands.CommandTree(self)
        self._dependencies: dynamicpy.DependencyLibrary = dynamicpy.DependencyLibrary()

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

    def register_plugin(self, plugin: Type[AmethystPlugin]) -> None:
        """Register an `AmethystPlugin` to the client.

        Parameters
        ----------
        plugin : Type[AmethystPlugin]
            A type inheriting from `AmethystPlugin` to register to the client.
        """
        _log.debug("Registering plugin '%s'", plugin.__name__)

        try:
            instance = plugin.__new__(plugin)
            instance._client = self  # add client attribute
            self._dependencies.inject(instance.__init__)
        except dynamicpy.InjectDependenciesError as e:
            raise error.RegisterPluginError(
                f"Error injecting dependencies into {plugin.__name__}"
            ) from e

        self._loader.load_object(instance)

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

    def load(self, search_modules: list[str] | None = None) -> None:
        """Recursively search the specified modules and register all widgets found.

        Parameters
        ----------
        search_modules : list[str], optional
            The modules to search through, will use the modules specified in the constructor by default
        """
        self._load_modules(search_modules or self._search_modules)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        """A Shorthand coroutine for `load` + `login` + `connect`.

        Parameters
        ----------
        token: str
            The authentication token. Do not prefix this token with
            anything as the library will do it for you.
        reconnect: bool
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled (such as
            invalid sharding payloads or bad tokens).
        """
        self.load()
        await super().start(token, reconnect=reconnect)

    def _build_loader(self) -> dynamicpy.DynamicLoader:
        """Builds a DynamicLoader for finding widgets to add to the client."""
        loader = dynamicpy.DynamicLoader()

        loader.register_type_handler(lambda _, v: self.register_command(v), AmethystCommand)
        loader.register_handler(
            lambda _, v: self.register_plugin(v),
            lambda _, v: isinstance(v, type)
            and v is not AmethystPlugin
            and issubclass(v, AmethystPlugin),
        )

        return loader

    def _load_modules(self, search_modules: list[str]) -> None:
        """Loads the modules specified in `search_modules` using the client's DynamicLoader."""
        _log.debug("Loading modules %s", search_modules)
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
            raise error.ModuleLocateError("Error locating home package") from e
