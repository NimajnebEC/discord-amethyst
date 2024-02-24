from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Concatenate, ParamSpec, Self, TypeVar

import dynamicpy

from amethyst.util import classproperty

if TYPE_CHECKING:
    from amethyst.client import Client

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


class Widget(dynamicpy.BaseWidget[Callable[Concatenate["Self@Plugin", P], T]]):
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

    @abstractmethod
    def register(self, plugin: Plugin, client: "Client") -> None:
        """Register the widget with the provided `Client`.

        Parameters
        ----------
        plugin: `Plugin`
            The plugin this widget belongs to.
        client : `Client`
            The client to register the widget with.
        """
