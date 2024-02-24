from amethyst.abc import Plugin
from amethyst.client import Client
from amethyst.widget.event import Event, event
from amethyst.widget.event.library import *  # noqa: F403

__version__ = "${pyproject.tool.poetry.version}"
__author__ = "${pyproject.tool.poetry.authors.0}"

__all__ = (  # noqa: F405
    "Client",
    "Plugin",
    "Event",
    "event",
)
