__all__ = (
    "PluginDependencyError",
    "DuplicatePluginError",
    "RegisterPluginError",
    "ModuleLocateError",
    "AmethystError",
)


class AmethystError(Exception):
    """Base exception class for the amethyst module."""


class ModuleLocateError(AmethystError):
    """Exception raised when there is an error locating a module."""


class RegisterPluginError(AmethystError):
    """Exceptions raised when registering a plugin fails."""


class DuplicatePluginError(RegisterPluginError):
    """Exception raised when attempting to register a plugin that is already registered."""


class PluginDependencyError(RegisterPluginError):
    """Exception raised when binding dependencies fails."""
