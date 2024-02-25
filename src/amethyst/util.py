from typing import Any

__all__ = ("is_dict_subset", "classproperty")


def is_dict_subset(superset: dict[Any, Any], subset: dict[Any, Any]) -> bool:
    """Returns true if all the keys in `subset` are present and have equal values in `superset`.

    Checks dictionaries and lists recursively.

    Parameters
    ----------
    superset : `dict[Any, Any]`
        The dictionary to check contains the subset.
    subset : `dict[Any, Any]`
        The dictionary to check is contained within the superset.

    Returns
    -------
    `bool`
        True if all the keys in `subset` are present and have equal values in `superset`.
    """
    return _node_is_subset(superset, subset)


def _node_is_subset(superset: Any, subset: Any) -> bool:
    if isinstance(superset, dict) and isinstance(subset, dict):
        # Ensure that all items in the subset are present in the superset
        return all(
            (k in superset and _node_is_subset(superset[k], v) for k, v in subset.items())
        )

    if isinstance(superset, list) and isinstance(subset, list):
        # Ensure that all items in the subset are present in the superset, no matter the order
        # Explaination:
        #   For each item in the subset, check if any items in the superset match
        return all((any((_node_is_subset(x, y) for x in superset)) for y in subset))
    return superset == subset


class classproperty:
    """Decorator to turn a method into a class property."""

    def __init__(self, func):
        self.fget = func

    def __get__(self, _, owner):
        return self.fget(owner)


def safesubclass(obj: object, cls: type) -> bool:
    """Combined isinstance and issubclass check.

    Parameters
    ----------
    obj : `object`
        The object to check if is a subclass of `cls`.
    cls : `type`
        The class to check if `obj` is a subclass of.

    Returns
    -------
    bool
        `True` if `obj` is a subclass of `cls`.
    """
    return isinstance(obj, type) and issubclass(obj, cls)
