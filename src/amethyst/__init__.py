from amethyst.amethyst import BaseWidget, Client, Plugin, WidgetPlugin
from amethyst.widget.command import command
from amethyst.widget.event import Event, event
from amethyst.widget.event.library import *  # noqa: F403
from amethyst.widget.menu import context_menu
from amethyst.widget.schedule import schedule

__version__ = "${pyproject.tool.poetry.version}"
__author__ = "${pyproject.tool.poetry.authors.0}"

__all__ = (
    "WidgetPlugin",
    "BaseWidget",
    "command",
    "Client",
    "Plugin",
    "Event",
    "event",
    "schedule",
    "context_menu",
)
