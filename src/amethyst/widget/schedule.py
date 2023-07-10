from datetime import datetime
from typing import Any, Callable, Coroutine, TypeVar

from croniter import CroniterBadCronError, croniter

from amethyst.widget.abc import AmethystPlugin, Callback, CallbackWidget

__all__ = ("AmethystSchedule", "schedule")

PluginT = TypeVar("PluginT", bound=AmethystPlugin)

ScheduleCallback = Callback[PluginT, [], Coroutine[Any, Any, None]]


class AmethystSchedule(CallbackWidget[PluginT, [], Coroutine[Any, Any, None]]):
    """Represents an asynchronous function that should be called on a schedule."""

    def __init__(
        self,
        callback: ScheduleCallback[PluginT],
        cron: str,
    ) -> None:
        super().__init__(callback)
        # validate cron expression
        try:
            croniter(cron)
        except CroniterBadCronError as e:
            raise TypeError(f"Bad Cron Expression '{cron}'") from e
        self._cron = cron

    @property
    def cron(self) -> str:
        """The cron expression for this schedule."""
        return self._cron

    def next_occurrence(self) -> datetime:
        """Gets the next occurrence of this schedule.

        Returns
        -------
        datetime
            The datetime representing when this schedule should next be called.
        """
        iter = croniter(self.cron, datetime.now())
        return iter.get_next(datetime)


def schedule(cron: str) -> Callable[[ScheduleCallback[PluginT]], AmethystSchedule[PluginT]]:
    """Decorator to create an `AmethystSchedule` from a regular function.

    Parameters
    ----------
    cron: str
        The cron expression to run the schedule on.
    """

    def decorator(func: ScheduleCallback[PluginT]) -> AmethystSchedule[PluginT]:
        return AmethystSchedule(func, cron)

    return decorator
