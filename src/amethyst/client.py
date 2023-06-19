import logging
from typing import Any, Self

import discord
import dynamicpy
from discord import app_commands

from amethyst import errors
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

    def _build_loader(self) -> dynamicpy.DynamicLoader:
        loader = dynamicpy.DynamicLoader()

        loader.register_handler(
            lambda _, v: self.register_command(v),  # type: ignore
            lambda _, v: isinstance(v, AmethystCommand),
        )

        return loader

    def _load_modules(self, search_modules: list[str]) -> None:
        for module in search_modules:
            if self.home_package is None and module.startswith("."):
                module = module[1:]
            self._loader.load_module(module, self.home_package)

    def _get_home_package(self) -> str | None:
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
