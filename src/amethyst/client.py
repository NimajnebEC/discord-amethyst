from amethyst import moduleutils
from types import ModuleType
from amethyst import errors
from typing import Any
import discord
import logging

__all__ = ("AmethystClient",)

_log = logging.getLogger(__name__)


class AmethystClient(discord.Client):
    def __init__(
        self,
        intents: discord.Intents,
        **options: Any,
    ) -> None:
        self._home_package = self._get_home_package()

        super().__init__(intents=intents, **options)

    @property
    def home_package(self) -> ModuleType | None:
        """The parent package of the module where this client was instantiated. Is `None` if it was a top-level module."""
        return self._home_package

    def _locate_module(self, path: str) -> ModuleType:
        if self.home_package is None and path.startswith("."):
            path = path[1:]

        try:
            return moduleutils.get_module(path, self.home_package)
        except ImportError:
            raise errors.ModuleLocateError("Could locate module '%s'", path)

    def _get_home_package(self) -> ModuleType | None:
        try:
            module = moduleutils.get_caller_module()

            if moduleutils.is_package(module):
                package = module
            else:
                package = moduleutils.get_parent(module)

            _log.debug("Home package located as '%s'", package.__name__)
            return package
        except moduleutils.NoParentError:
            _log.debug("Instantiating module is top-level.")
            return None
        except (ImportError, moduleutils.ModuleUtilsError) as e:
            _log.error("Error locating home package: %s", e)
            raise errors.ModuleLocateError("Error locating home package") from e
