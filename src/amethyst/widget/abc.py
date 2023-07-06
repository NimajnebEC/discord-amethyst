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


class CallbackWidget(ABC, Generic[PluginT, P, T]):
    """The base class for all callback based widgets."""

    def __init__(self, callback: Callback[PluginT, P, T]) -> None:
        self._callback: Callback[PluginT, P, T] = callback
        self._binding: PluginT | None = None

    def _bound_copy(self, binding: PluginT) -> Self:
        copy = shallowcopy(self)
        copy._binding = binding
        return copy

    def invoke(self, *args, **kwargs) -> T:
        """Invokes the callback with the provided parameters and returns its result.

        Returns
        -------
        T
            The returned result from the callback function.
        """
        if self._binding is not None:
            return self._callback(self._binding, *args, **kwargs)  # type: ignore
        return self._callback(*args, **kwargs)  # type: ignore

    @property
    def callback(self) -> Callback[PluginT, P, T]:
        """The callback function of this widget."""
        return self._callback
