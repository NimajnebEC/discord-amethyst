import amethyst.moduleutils.errors as errors
from types import ModuleType
from typing import Iterator
import importlib.util
import importlib.abc
import importlib
import pkgutil
import sys

__all__ = (
    "get_caller_module",
    "iter_submodules",
    "get_parent",
    "is_package",
    "get_module",
)


def get_caller_module() -> ModuleType:
    """Gets the module of the first non-amethyst function in the stack.

    Returns
    -------
    ModuleType
        The first foreign module in the stack.

    Raises
    ------
    ModuleUtilsError
        Raised no foreign modules are found in the stack.
    """
    frame = sys._getframe(1)
    while True:
        name = frame.f_globals.get("__name__", "")
        if not name.startswith("amethyst."):
            return get_module(name)
        frame = frame.f_back
        if frame is None:
            raise errors.ModuleUtilsError("No foreign modules in stack.")


def iter_submodules(package: ModuleType) -> Iterator[ModuleType]:
    """Yields ModuleType for all submodules of the provided package.

    Parameters
    ----------
    module : ModuleType
        The package to iterate through.

    Yields
    ------
    ModuleType
        A submodule of the package.

    Raises
    ------
    ExpectedPackageError
        Raised when the provided module is not a package.
    """
    if not is_package(package):
        raise errors.ExpectedPackageError("Provided module is not a package.")
    for finder, name, _ in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        spec = None
        if isinstance(finder, importlib.abc.MetaPathFinder):
            spec = finder.find_spec(name, package.__path__)
        elif isinstance(finder, importlib.abc.PathEntryFinder):
            spec = finder.find_spec(name, package)

        if spec is not None:
            package = importlib.util.module_from_spec(spec)
            yield package


def is_package(module: ModuleType) -> bool:
    """Checks if the given module is a package.

    Parameters
    ----------
    module : ModuleType
        The module to check.

    Returns
    -------
    bool
        True if the provided module is a package.
    """
    return hasattr(module, "__path__")


def get_module(name: str, package: str | ModuleType | None = None) -> ModuleType:
    """Gets a module from its name.

    Parameters
    ----------
    name : str
        The absolute name of the module.
    package : str | ModuleType | None
        If present, will perform a relative import from the specified package.

    Returns
    -------
    ModuleType
        The imported module.
    """
    if isinstance(package, ModuleType):
        package = package.__name__
    return importlib.import_module(name, package)


def get_parent(module: ModuleType) -> ModuleType:
    """Gets the parent package of the specified module.

    Parameters
    ----------
    module : ModuleType
        The module to get the parent of.

    Returns
    -------
    ModuleType
        The parent package of the specified module.

    Raises
    ------
    NoParentError
        Raised when the specified module has no parent.
    """
    try:
        resolved = importlib.util.resolve_name("..", module.__name__)
    except ImportError:
        raise errors.NoParentError(f"{module.__name__} is a top level module.")
    return get_module(resolved)
