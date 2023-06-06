__all__ = ("ModuleUtilsError", "ExpectedPackage")


class ModuleUtilsError(Exception):
    """Base exception class for amethyst's moduleutils module."""


class ExpectedPackage(ModuleUtilsError):
    """Exception raised when function expected a package but got a module."""
