from abc import ABC
from copy import copy as shallowcopy
from typing import Any, Callable, Concatenate, Generic, ParamSpec, Self, TypeVar, Union

from dynamicpy import DynamicLoader

__all__ = ("AmethystPlugin", "CallbackWidget")

T = TypeVar("T")
P = ParamSpec("P")
PluginT = TypeVar("PluginT", bound="AmethystPlugin")
Callback = Union[Callable[Concatenate[PluginT, P], T], Callable[P, T]]


class AmethystPlugin(ABC):
    """The base class for all Amethyst plugins to inherit from"""

    def __new__(cls) -> Self:
        self = super().__new__(cls)

        # Bind all CallbackWidgets to self
        loader = DynamicLoader()
        loader.register_type_handler(
            lambda n, v: setattr(self, n, v._bound_copy(self)),
            CallbackWidget[Self, Any, Any],
        )

        loader.load_object(self)

        return self


class CallbackWidget(ABC, Generic[PluginT, P, T]):
    """The base class for all callback based widgets."""

    def __init__(self, callback: Callback[PluginT, P, T]) -> None:
        self._callback: Callback[PluginT, P, T] = callback
        self._binding: PluginT | None = None

    def _bound_copy(self, binding: PluginT) -> Self:
        copy = shallowcopy(self)
        copy._binding = binding
        return copy

    @property
    def callback(self) -> Callback[PluginT, P, T]:
        """The callback function of this widget."""
        return self._callback
