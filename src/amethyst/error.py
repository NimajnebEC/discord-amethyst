__all__ = (
    "AmethystError",
    "ModuleLocateError",
    "RegisterPluginError",
    "WidgetAlreadyRegisteredError",
)


class AmethystError(Exception):
    """Base exception class for the amethyst module."""


class ModuleLocateError(AmethystError):
    """Exception raised when there is an error locating a module."""


class RegisterPluginError(AmethystError):
    """Exception raised when there is an error registering a plugin."""


class WidgetAlreadyRegisteredError(AmethystError):
    """Exception raised when attempting to register a widget that has already been registered to this client."""
