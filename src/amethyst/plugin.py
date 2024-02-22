import contextlib
import logging
from typing import Any

import dynamicpy

from amethyst import error

_default_modules = [".command", ".commands", ".plugins", ".plugin"]

_log = logging.getLogger(__name__)


class Plugin:
    """The base class for all Amethyst plugins to inherit from."""

    def __init__(self) -> None:
        """The client will attempt to bind constructor parameters to dependencies when registered."""


class PluginManager:
    def __init__(self) -> None:
        self._instantiating_package = self._get_instantiating_package()
        self._module_loader = self._build_module_loader()
        self._plugin_loader = self._build_plugin_loader()

    def load_modules(self, search_modules: list[str]) -> None:
        _log.debug("Loading modules %s", search_modules)
        for module in search_modules:
            if self._instantiating_package is None and module.startswith("."):
                module = module[1:]
            with contextlib.suppress(ImportError):
                self._module_loader.load_module(module, self._instantiating_package)

    def _build_module_loader(self) -> dynamicpy.DynamicLoader:
        loader = dynamicpy.DynamicLoader()

        @loader.handler()
        def _(key: str, value: Any):
            if (
                isinstance(value, type)
                and value is not Plugin
                and issubclass(value, Plugin)
            ):
                with contextlib.suppress(error.DuplicatePluginError):
                    print(value.__module__)

        return loader

    def _build_plugin_loader(self) -> dynamicpy.DynamicLoader:
        return dynamicpy.DynamicLoader()

    def _get_instantiating_package(self) -> str | None:
        """Return the package the application was instantiated from."""
        try:
            module = dynamicpy.get_foreign_module()

            if dynamicpy.is_package(module):
                package = module
            else:
                package = dynamicpy.get_module_parent(module)

            _log.debug("Instantiating package located as '%s'", package)
            return package
        except dynamicpy.NoParentError:
            _log.debug("Instantiating module is top-level.")
            return None
        except ImportError as e:
            _log.error("Error locating instantiating package: %s", e)
            raise error.ModuleLocateError("Error locating instantiating package") from e
