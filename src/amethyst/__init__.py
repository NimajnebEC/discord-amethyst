from amethyst.amethyst import BaseWidget, Client, Plugin, WidgetPlugin
from amethyst.widget.command import command
from amethyst.widget.event import Event, event
from amethyst.widget.event.library import *  # noqa: F403

__version__ = "${pyproject.tool.poetry.version}"
__author__ = "${pyproject.tool.poetry.authors.0}"

__all__ = (  # noqa: F405
    "WidgetPlugin",
    "BaseWidget",
    "command",
    "Client",
    "Plugin",
    "Event",
    "event",
)
