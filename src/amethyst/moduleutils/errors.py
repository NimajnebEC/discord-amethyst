__all__ = ("ModuleUtilsError", "ExpectedPackageError", "NoParentError")


class ModuleUtilsError(Exception):
    """Base exception class for amethyst's moduleutils module."""


class ExpectedPackageError(ModuleUtilsError):
    """Exception raised when function expected a package but got a module."""


class NoParentError(ModuleUtilsError):
    """Exception raised when trying to get the parent of a top level module."""
