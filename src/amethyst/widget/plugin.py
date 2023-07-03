from abc import ABC
from copy import copy as shallowcopy
from typing import Self

from dynamicpy import DynamicLoader

__all__ = ("AmethystPlugin", "BindableWidget")


class AmethystPlugin(ABC):
    """The base class for all Amethyst plugins to inherit from"""

    def __new__(cls) -> Self:
        self = super().__new__(cls)

        loader = DynamicLoader()

        loader.register_type_handler(
            lambda n, v: setattr(self, n, v._bound_copy(self)),
            BindableWidget,
        )

        loader.load_object(self)

        return self


class BindableWidget(ABC):
    """The base class for all callback based widgets that can be used in an `AmethystPlugin`."""

    def __init__(self) -> None:
        self.binding = AmethystPlugin | None

    def _bound_copy(self, binding: AmethystPlugin) -> Self:
        copy = shallowcopy(self)
        copy.binding = binding
        return copy
