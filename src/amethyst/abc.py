from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    ParamSpec,
    Self,
    TypeAlias,
    TypeVar,
)

import dynamicpy

from amethyst.util import classproperty, safesubclass

if TYPE_CHECKING:
    from amethyst.client import Client

PluginSelf: TypeAlias = "Self@Plugin"  # type: ignore

WidgetT = TypeVar("WidgetT", bound="BaseWidget[..., Any]")
P = ParamSpec("P")
T = TypeVar("T")


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
