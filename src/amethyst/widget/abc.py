from abc import ABC
from copy import copy as shallowcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    Generic,
    ParamSpec,
    Self,
    TypeVar,
    Union,
)

from dynamicpy import DynamicLoader

if TYPE_CHECKING:
    from amethyst.client import AmethystClient

__all__ = ("AmethystPlugin", "CallbackWidget", "Callback")

T = TypeVar("T")
P = ParamSpec("P")
PluginT = TypeVar("PluginT", bound="AmethystPlugin")
Callback = Union[Callable[Concatenate[PluginT, P], T], Callable[P, T]]


class AmethystPlugin(ABC):
    """The base class for all Amethyst plugins to inherit from."""

    def __init__(self) -> None:
        """The client will attempt to bind constructor parameters to dependencies when registered."""
        self._client: AmethystClient

    def __new__(cls, *args, **kwargs) -> Self:
        instance = super().__new__(cls)
        instance._bind_widgets()
        return instance

    def _bind_widgets(self):
        """Bind all `CallbackWidgets` to self."""
        loader = DynamicLoader()
        loader.register_type_handler(
            lambda n, v: setattr(self, n, v._bound_copy(self)),
            CallbackWidget[Self, Any, Any],
        )

        loader.load_object(self)

        return self

    @property
    def client(self) -> "AmethystClient":
        """The instance of `AmethystClient` that this plugin is registered to."""
        if not hasattr(self, "_client"):
            raise AttributeError(
                "Plugin has no attribute 'client' as it was not instantiated by an AmethystClient"
            )
        return self._client

    @property
    def name(self) -> str:
        """The name of this plugin."""
        return type(self).__name__


class CallbackWidget(ABC, Generic[PluginT, P, T]):
    """The base class for all callback based widgets."""

    def __init__(self, callback: Callback[PluginT, P, T], name: str | None = None) -> None:
        """The base class for all callback based widgets.

        Parameters
        ----------
        callback : `Callable[Concatenate[PluginT, P], T] | Callable[P, T]`
            _description_
        name : `str`, optional
            The name of this callback widget, by default None
        """
        self._callback: Callback[PluginT, P, T] = callback
        self._binding: PluginT | None = None
        self._name: str | None = name

    def _bound_copy(self, binding: PluginT) -> Self:
        copy = shallowcopy(self)
        copy._binding = binding
        return copy

    def invoke(self, *args, **kwargs) -> T:
        """Invokes the callback with the provided parameters and returns its result.

        Returns
        -------
        `T`
            The returned result from the callback function.
        """
        if self._binding is not None:
            return self._callback(self._binding, *args, **kwargs)  # type: ignore
        return self._callback(*args, **kwargs)  # type: ignore

    @property
    def callback(self) -> Callback[PluginT, P, T]:
        """The callback function of this widget."""
        return self._callback

    @property
    def name(self) -> str:
        """The name of this callback widget."""
        if self._name is not None:
            return self._name

        name = self.callback.__name__
        if self._binding is not None:
            return f"{self._binding.name}.{name}"
        return name

    @name.setter
    def name(self, name: str):
        self._name = name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"
