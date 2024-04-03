from __future__ import annotations

import asyncio
import itertools
import logging
from datetime import datetime
from typing import Any, Callable, Coroutine, Iterator

from croniter import CroniterBadCronError, croniter

from amethyst.amethyst import BaseWidget, Client, Plugin, PluginSelf

Callback = Callable[[PluginSelf], Coroutine[Any, Any, None]]

_min_step = 30

_log = logging.getLogger(__name__)


async def wait_until(when: datetime):
    """Wait until the specified datetime by waiting exponentially smaller intervals.

    This protects the function from un-expected clock changes.

    Parameters
    ----------
    when : datetime
        The datetime to wait until.
    """
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

    def get_iter(self) -> Iterator[datetime]:
        """Gets an iterable of datetimes this schedule should be invoked at starting from now.

        Returns
        -------
        `Iterator[datetime]`
            And iterable of when this schedule should be invoked.
        """
        iter = croniter(self.cron, datetime.now())
        return (iter.get_next(datetime) for _ in itertools.count())

    def register(self, plugin: Plugin, client: Client) -> None:
        _log.debug("Registering schedule '%s' with '%s'", self.name, self.cron)

        async def loop():
            iter = self.get_iter()
            while not client.is_closed():
                await wait_until(next(iter))
                if client.is_ready():
                    _log.debug("Invoking schedule '%s'", self.name)
                    client.create_task(self.callback(plugin))
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
