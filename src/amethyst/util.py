from typing import Any

__all__ = ("is_dict_subset",)


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
