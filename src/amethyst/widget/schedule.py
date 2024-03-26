from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Coroutine

from croniter import CroniterBadCronError, croniter

from amethyst.amethyst import BaseWidget, Client, Plugin, PluginSelf

Callback = Callable[[PluginSelf], Coroutine[Any, Any, None]]

_min_step = 30

_log = logging.getLogger(__name__)


async def wait_until(when: datetime):
    while True:
        delay = (when - datetime.now()).total_seconds()
        if delay <= _min_step:
            break
        await asyncio.sleep(delay / 2)
    await asyncio.sleep(delay)


class ScheduleWidget(BaseWidget[Callback]):
    """Represents an asynchronous function that should be called on a schedule.

    These are not usually created manually, instead they are created using the `amethyst.schedule` decorator.
    """

    def __init__(self, callback: Callback, cron: str) -> None:
        super().__init__(callback)
        try:  # validate cron expression
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
        `datetime`
            The `datetime` representing when this schedule should next be called.
        """
        iter = croniter(self.cron, datetime.now())
        return iter.get_next(datetime)

    def register(self, plugin: Plugin, client: Client) -> None:
        _log.debug("Registering schedule '%s' with '%s'", self.name, self.cron)

        async def loop():
            while not client.is_closed():
                await wait_until(self.next_occurrence())
                if client.is_ready():
                    _log.debug("Invoking schedule '%s'", self.name)
                    client.create_task(self.bound(plugin)())
                else:
                    _log.debug("Skipping schedule '%s' as client is not ready", self.name)

        client.create_task(loop())


schedule = ScheduleWidget.decorate
"""Decorator to designate a regular function to be called on a schedule.

    Parameters
    ----------
    cron: `str`
        The cron expression to run the schedule on.
    """
