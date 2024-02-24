from __future__ import annotations

import contextlib
import logging
from typing import Any, Dict, Type, TypeVar

import discord
import dynamicpy

from amethyst import error
from amethyst.abc import Plugin, Widget

_default_modules = [".command", ".commands", ".plugins", ".plugin"]

_log = logging.getLogger(__name__)

PluginT = TypeVar("PluginT", bound=Plugin)


class Client(discord.Client):
    """Represents a connection to Discord. This class extends discord.Client and is the primary home of amethyt's additions."""

    def __init__(
        self,
        intents: discord.Intents,
        **options: Any,
    ) -> None:
        super().__init__(intents=intents, **options)
        self._instantiating_package = self._get_instantiating_package()
        self._dependencies = dynamicpy.DependencyLibrary()
        self._module_loader = self._build_module_loader()
        self._plugins: Dict[Type[Plugin], Plugin] = {}

    def get_plugin(self, plugin: Type[PluginT]) -> PluginT:
        if plugin in self._plugins:
            return self._plugins[plugin]  # type: ignore
        raise KeyError(f"Plugin {plugin.name} not registered.")

    def load_modules(self, modules: list[str] = _default_modules) -> None:
        _log.debug("Loading modules %s", modules)
        for module in modules:
            if self._instantiating_package is None and module.startswith("."):
                module = module[1:]
            with contextlib.suppress(ImportError):
                self._module_loader.load_module(module, self._instantiating_package)

    def register_plugin(self, plugin: Type[Plugin]) -> None:
        if plugin in self._plugins:
            raise error.DuplicatePluginError(f"{plugin.name} has already been registered.")
        _log.debug("Registering plugin '%s'", plugin.name)

        try:
            instance = plugin.__new__(plugin)
            setattr(instance, "_client", self)
            self._dependencies.inject(instance.__init__)
        except (dynamicpy.DependencyNotFoundError, dynamicpy.InjectDependenciesError) as e:
            raise error.RegisterPluginError(
                f"Error injecting dependencies into '{plugin.name}'"
            ) from e

        self._load_plugin(instance)
        self._plugins[plugin] = instance

    def add_dependency(self, dependency: Any) -> None:
        """Add a dependency to the client's dependency library.

        These dependencies are injected into plugin constructors.

        Parameters
        ----------
        dependency : `Any`
            The dependency to add the library.

        Raises
        ------
        `TypeError`
            Raised when attempting to add a type to the library.
        `DuplicateDependencyError`
            Raised when another dependency with that type already exists in the library.
        """
        self._dependencies.add(dependency)

    def _load_plugin(self, plugin: Plugin) -> None:
        loader = dynamicpy.DynamicLoader()

        @loader.widget_handler(Widget)
        def _(widget: Widget):
            widget.register(plugin, self)

        loader.load_object(plugin)

    def _build_module_loader(self) -> dynamicpy.DynamicLoader:
        loader = dynamicpy.DynamicLoader()

        @loader.handler()
        def _(_, value: Any):
            if (
                isinstance(value, type)
                and value is not Plugin
                and issubclass(value, Plugin)
            ):
                with contextlib.suppress(error.DuplicatePluginError):
                    self.register_plugin(value)

        return loader

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
            raise error.ModuleLocateError("Error locating instantiating package") from e
