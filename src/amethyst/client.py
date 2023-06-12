from amethyst import errors
from typing import Any
import dynamicpy
import discord
import logging

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
        self._home_package = self._get_home_package()
        self._load_modules(search_modules or _default_modules)

        super().__init__(intents=intents, **options)

    @property
    def home_package(self) -> str | None:
        """The parent package of the module where this client was instantiated. Is `None` if it was a top-level module."""
        return self._home_package

    def _load_modules(self, search_modules: list[str]) -> None:
        loader = dynamicpy.DynamicLoader()
        loader.register_handler(lambda n, v: print(n))

        for module in search_modules:
            if self.home_package is None and module.startswith("."):
                module = module[1:]
            loader.load_module(module, self.home_package)

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
