__all__ = ("AmethystError", "ModuleLocateError", "DuplicatePluginError")


class AmethystError(Exception):
    """Base exception class for the amethyst module."""


class ModuleLocateError(AmethystError):
    """Exception raised when there is an error locating a module."""


class DuplicatePluginError(AmethystError):
    """Exception raised when attempting to register a plugin that is already registered."""
