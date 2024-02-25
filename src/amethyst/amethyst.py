from __future__ import annotations

import contextlib
import logging
from typing import (
    Any,
    Callable,
    Concatenate,
    Dict,
    List,
    ParamSpec,
    Self,
    Type,
    TypeAlias,
    TypeVar,
)

import discord
import dynamicpy

from amethyst import error
from amethyst.util import classproperty, safesubclass

_default_modules = [".command", ".commands", ".plugins", ".plugin"]

_log = logging.getLogger(__name__)

PluginSelf: TypeAlias = "Self@Plugin"  # type: ignore

WidgetT = TypeVar("WidgetT", bound="BaseWidget[..., Any]")
PluginT = TypeVar("PluginT", bound="Plugin")
P = ParamSpec("P")
T = TypeVar("T")


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
        self._widgets: List[BaseWidget] = []

    def has_plugin(self, plugin: Type[Plugin]) -> bool:
        return plugin in self._plugins

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

        # * Instantiate Plugin
        try:
            instance = plugin.__new__(plugin)
            setattr(instance, "_client", self)
            self._dependencies.inject(instance.__init__)
        except (dynamicpy.DependencyNotFoundError, dynamicpy.InjectDependenciesError) as e:
            raise error.RegisterPluginError(
                f"Error injecting dependencies into '{plugin.name}'"
            ) from e

        # * Load widgets
        loader = dynamicpy.DynamicLoader()

        @loader.widget_handler(BaseWidget)
        def _(widget: BaseWidget):
            if widget not in self._widgets:
                widget.register(instance, self)
                self._widgets.append(widget)

        loader.load_object(instance)

        # * Add to plugins list
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

    def _build_module_loader(self) -> dynamicpy.DynamicLoader:
        loader = dynamicpy.DynamicLoader()

        @loader.handler()
        def _(_, value: Any):
            if value is not Plugin and safesubclass(value, Plugin):
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


class Plugin:
    """The base class for all Amethyst plugins to inherit from."""

    def __init__(self) -> None:
        """The client will attempt to bind constructor parameters to dependencies when registered."""

    @property
    def client(self) -> "Client":
        return getattr(self, "_client") if hasattr(self, "_client") else None  # type: ignore

    @classproperty
    def name(cls):
        return cls.__name__


class BaseWidget(dynamicpy.BaseWidget[Callable[Concatenate[PluginSelf, P], T]]):
    def bound(self, plugin: Plugin) -> Callable[P, T]:
        """Return a bound copy of the callback function.

        Parameters
        ----------
        plugin : `Plugin`
            The `Plugin` to bind the function to.

        Returns
        -------
        `Callable[P, T]`
            The bound version of the callback function.
        """
        return lambda *args, **kwargs: self.callback(plugin, *args, **kwargs)  # type: ignore

    def register(self, plugin: Plugin, client: "Client") -> None:
        """Register the widget with the provided `Client`.

        Parameters
        ----------
        plugin: `Plugin`
            The plugin this widget belongs to.
        client : `Client`
            The client to register the widget with.
        """
        raise NotImplementedError(f"{type(self).__name__} must implement 'register'")

    @property
    def name(self) -> str:
        return self.callback.__name__


class _WidgetPluginMeta(type):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        loader = dynamicpy.DynamicLoader()
        loader.register_handler(cls._inject, lambda _, v: safesubclass(v, BaseWidget))
        loader.load_object(cls)
        return cls

    def _inject(cls, _, widget) -> None:
        def proxy(widget, plugin: Plugin, client: "Client") -> None:
            if not client.has_plugin(cls):
                client.register_plugin(cls)
            widget_plugin = client.get_plugin(cls)  # type: ignore
            cls.register(widget_plugin, widget, plugin)  # type: ignore

        setattr(widget, "register", proxy)


class WidgetPlugin(Plugin, metaclass=_WidgetPluginMeta):
    def register(self, widget: BaseWidget, plugin: Plugin):
        raise NotImplementedError(f"{self.name} must implement 'register'")
