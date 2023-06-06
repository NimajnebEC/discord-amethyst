import amethyst.moduleutils.errors as errors
from types import ModuleType
from typing import Iterator
import importlib.util
import importlib.abc
import importlib
import inspect
import pkgutil

__all__ = ("get_caller_module", "iter_submodules")


def get_caller_module() -> ModuleType:
    """Gets the module of the first non-amethyst function in the stack.

    Returns
    -------
    ModuleType
        The first foreign module in the stack.
    """
    stack = inspect.stack(0)
    for frame in stack:
        name = frame.frame.f_globals.get("__name__", "")
        if not name.startswith("amethyst."):
            return importlib.import_module(name)
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
    errors.ExpectedPackage
        Raised when the provided module is not a package.
    """
    if not hasattr(package, "__path__"):
        raise errors.ExpectedPackage("Modules can not have submodules.")
    for finder, name, _ in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        spec = None
        if isinstance(finder, importlib.abc.MetaPathFinder):
            spec = finder.find_spec(name, package.__path__)
        elif isinstance(finder, importlib.abc.PathEntryFinder):
            spec = finder.find_spec(name, package)

        if spec is not None:
            package = importlib.util.module_from_spec(spec)
            yield package
