from typing import Self

from dynamicpy import DynamicLoader

from amethyst import widget

__all__ = ("AmethystPlugin",)


class AmethystPlugin:
    """The base class for all Amethyst plugins to inherit from"""

    def __new__(cls) -> Self:
        self = super().__new__(cls)

        loader = DynamicLoader()

        @loader.type_handler(widget.AmethystCommand)
        def bind_command(name: str, command: widget.AmethystCommand):
            cmd = command._copy_with(parent=command.parent, binding=self)
            setattr(self, name, cmd)

        loader.load_object(self)

        return self
