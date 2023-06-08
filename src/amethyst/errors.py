__all__ = ("AmethystError", "ModuleLocateError")


class AmethystError(Exception):
    """Base exception class for the amethyst module."""


class ModuleLocateError(AmethystError):
    """Exception raised when there is an error locating a module."""
