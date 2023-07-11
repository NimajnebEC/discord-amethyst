import asyncio
import contextlib
import logging
import os
from datetime import datetime
from typing import Any, Callable, Coroutine, Self, Type, TypeVar, overload

import discord
import dynamicpy
from discord import app_commands
from discord.abc import Snowflake
from discord.utils import MISSING
from dotenv import load_dotenv

from amethyst import error
from amethyst.util import is_dict_subset
from amethyst.widget import (
    AmethystCommand,
    AmethystEvent,
    AmethystEventHandler,
    AmethystPlugin,
    AmethystSchedule,
    DiscordPyEvent,
    events,
)

__all__ = ("AmethystClient",)

_environ_key_token = "AMETHYST-BOT-TOKEN"
_environ_key_sync_guild = "AMETHSYT-SYNC-GUILD"
_environ_key_auto_sync = "AMETHYST-AUTO-SYNC"

_schedule_delay_cutoff = 30

_default_modules = [".command", ".commands", ".plugins", ".plugin"]

_log = logging.getLogger(__name__)

CoroT = TypeVar("CoroT", bound=Callable[..., Coroutine[Any, Any, Any]])
T = TypeVar("T")


def try_register(func: Callable[[T], None], widget: T) -> None:
    """Calls the specified register method, suppressing any raised `WidgetAlreadyRegisteredError`.

    Parameters
    ----------
    func : `Callable[[T], None]`
        The register method to wrap.
    widget : `T`
        The widget to register.
    """
    with contextlib.suppress(error.WidgetAlreadyRegisteredError):
        return func(widget)


class AmethystClient(discord.Client):
    """Represents a connection to Discord. This class extends discord.Client and is the primary home of amethyt's additions."""

    def __init__(
        self,
        intents: discord.Intents,
        *,
        search_modules: list[str] | None = None,
        **options: Any,
    ) -> None:
        """Represents a connection to Discord. This class extends discord.Client and is the primary home of amethyt's additions.

        Parameters
        ----------
        intents: `Intents`
            The intents that you want to enable for the session. This is a way of
            disabling and enabling certain gateway events from triggering and being sent.
        search_modules : `list[str]`, optional
            The modules to search for widgets and plugins in
        max_messages: `int`, optional
            The maximum number of messages to store in the internal message cache.
            This defaults to ``1000``. Passing in ``None`` disables the message cache.
        proxy: `str`, optional
            Proxy URL.
        proxy_auth: `aiohttp.BasicAuth`, optional
            An object that represents proxy HTTP Basic Authorization.
        shard_id: `int`, optional
            Integer starting at ``0`` and less than `.shard_count`.
        shard_count: `int`, optional
            The total number of shards.
        application_id: `int`
            The client's application ID.
        member_cache_flags: `MemberCacheFlags`
            Allows for finer control over how the library caches members.
            If not given, defaults to cache as much as possible with the
            currently selected intents.
        chunk_guilds_at_startup: `bool`
            Indicates if `.on_ready` should be delayed to chunk all guilds
            at start-up if necessary. This operation is incredibly slow for large
            amounts of guilds. The default is ``True`` if `Intents.members`
            is ``True``.
        status: `.Status`, optional
            A status to start your presence with upon logging on to Discord.
        activity: `.BaseActivity`, optional
            An activity to start your presence with upon logging on to Discord.
        allowed_mentions: `AllowedMentions`, optional
            Control how the client handles mentions by default on every message sent.
        heartbeat_timeout: `float`
            The maximum numbers of seconds before timing out and restarting the
            WebSocket in the case of not receiving a HEARTBEAT_ACK. Useful if
            processing the initial packets take too long to the point of disconnecting
            you. The default timeout is 60 seconds.
        guild_ready_timeout: `float`
            The maximum number of seconds to wait for the GUILD_CREATE stream to end before
            preparing the member cache and firing READY. The default timeout is 2 seconds.
        assume_unsync_clock: `bool`
            Whether to assume the system clock is unsynced. This applies to the ratelimit handling
            code. If this is set to ``True``, the default, then the library uses the time to reset
            a rate limit bucket given by Discord. If this is ``False`` then your system clock is
            used to calculate how long to sleep for. If this is set to ``False`` it is recommended to
            sync your system clock to Google's NTP server.
        enable_debug_events: `bool`
            Whether to enable events that are useful only for debugging gateway related information.

            Right now this involves :func:`on_socket_raw_receive` and :func:`on_socket_raw_send`. If
            this is ``False`` then those events will not be dispatched (due to performance considerations).
            To enable these events, this must be set to ``True``. Defaults to ``False``.
        http_trace: `aiohttp.TraceConfig`
            The trace configuration to use for tracking HTTP requests the library does using ``aiohttp``.
            This allows you to check requests the library is using. For more information, check the
            [aiohttp documentation](https://docs.aiohttp.org/en/stable/client_advanced.html#client-tracing).
        max_ratelimit_timeout: `float`, optional
            The maximum number of seconds to wait when a non-global rate limit is encountered.
            If a request requires sleeping for more than the seconds passed in, then
            :exc:`~discord.RateLimited` will be raised. By default, there is no timeout limit.
            In order to prevent misuse and unnecessary bans, the minimum value this can be
            set to is ``30.0`` seconds.
        """
        super().__init__(intents=intents, **options)
        self._search_modules: list[str] | None = search_modules
        self._home_package: str | None = self._get_home_package()
        self._loader: dynamicpy.DynamicLoader = self._build_loader()
        self._tree: app_commands.CommandTree[Self] = app_commands.CommandTree(self)
        self._dependencies: dynamicpy.DependencyLibrary = dynamicpy.DependencyLibrary()
        self._schedule_sleep_task: asyncio.Task | None = None
        self._plugins: list[Type[AmethystPlugin]] = []
        self._events: list[AmethystEventHandler] = []
        self._schedules: list[AmethystSchedule] = []
        self._commands: list[AmethystCommand] = []

    @property
    def home_package(self) -> str | None:
        """The parent package of the module where this client was instantiated. Is `None` if it was a top-level module."""
        return self._home_package

    @property
    def tree(self) -> app_commands.CommandTree:
        """The command tree responsible for handling the application commands in this bot."""
        return self._tree

    def add_dependency(self, dependency: Any) -> None:
        """Add a dependency to the client's dependency library.

        These dependencies are injected into plugin constructors.

        Parameters
        ----------
        dependency : `Any`
            The dependency to add the library.

        Raises
        ------
        `TypeError`
            Raised when attempting to add a type to the library.
        `DuplicateDependencyError`
            Raised when another dependency with that type already exists in the library.
        """
        self._dependencies.add(dependency)

    def register_command(self, command: AmethystCommand) -> None:
        """Register an instance of `AmethystCommand` to the client.

        Parameters
        ----------
        `command` : `AmethystCommand`
            The command to register.
        """
        # Ensure not already registered
        if command in self._commands:
            raise error.WidgetAlreadyRegisteredError(
                f"Command {command.name} has already been registered."
            )
        _log.debug("Registering command '%s'", command.name)
        self._tree.add_command(command)
        self._commands.append(command)

    def register_plugin(self, plugin: Type[AmethystPlugin]) -> None:
        """Register an `AmethystPlugin` to the client.

        Parameters
        ----------
        plugin : `Type[AmethystPlugin]`
            A type inheriting from `AmethystPlugin` to register to the client.
        """

        # Ensure not already registered
        if plugin in self._plugins:
            raise error.WidgetAlreadyRegisteredError(
                f"Plugin {plugin.name} has already been registered."
            )
        _log.debug("Registering plugin '%s'", plugin.name)
        self._plugins.append(plugin)

        try:
            instance = plugin.__new__(plugin)
            instance._client = self  # add client attribute
            self._dependencies.inject(instance.__init__)
        except dynamicpy.DependencyNotFoundError as e:
            raise error.RegisterPluginError(
                f"Could not find a dependency when injecting into '{plugin.name}'"
            ) from e
        except dynamicpy.InjectDependenciesError as e:
            raise error.RegisterPluginError(
                f"Error injecting dependencies into '{plugin.name}'"
            ) from e

        self._loader.load_object(instance)

    def register_event(self, handler: AmethystEventHandler) -> None:
        """Register an `AmethystEventHandler` to the client.

        Parameters
        ----------
        event : `AmethystEvent`
            The instance `AmethystEventHandler` to register to the client.
        """

        # Ensure not already registered
        if handler in self._events:
            raise error.WidgetAlreadyRegisteredError(
                f"Handler {handler.name} has already been registered."
            )
        self._events.append(handler)
        event = handler.event
        _log.debug(
            "Registering handler '%s' for event '%s'",
            handler.name,
            event.name,
        )

        # Setup invoker for default events
        if isinstance(handler.event, DiscordPyEvent) and not hasattr(self, event.name):
            setattr(
                self,
                event.name,
                lambda *args, **kwargs: self.invoke_event(event, *args, **kwargs),
            )

    def register_schedule(self, schedule: AmethystSchedule) -> None:
        """Register an `AmethystSchedule` to the client.

        Parameters
        ----------
        schedule : `AmethystSchedule`
            The instance `AmethystSchedule` to register to the client.
        """

        # Ensure not already registered
        if schedule in self._schedules:
            raise error.WidgetAlreadyRegisteredError(
                f"Schedule {schedule.name} has already been registered."
            )
        _log.debug("Registering schedule '%s'", schedule.name)
        self._schedules.append(schedule)

        if self._schedule_sleep_task is None:
            if self.is_ready():
                # start loop
                self.loop.create_task(self._schedule_loop())
        elif (
            not self._schedule_sleep_task.cancelled()
            and not self._schedule_sleep_task.cancelling()
        ):
            # Cancel the sleep task to recalculate next_datetime
            self._schedule_sleep_task.cancel()

    @overload
    def invoke_event(
        self, event: AmethystEvent[Any, Coroutine], *args, **kwargs
    ) -> Coroutine[Any, Any, None]:
        ...

    @overload
    def invoke_event(self, event: AmethystEvent[Any, None], *args, **kwargs) -> None:
        ...

    def invoke_event(self, event: AmethystEvent, *args, **kwargs) -> Coroutine | None:
        """Invokes all the registered handlers of the specified event.

        Parameters
        ----------
        event : `AmethystEvent`
            The event to invoke the handlers of.

        Returns
        -------
        `Coroutine | None`
            When the event is a coroutine, a `Coroutine` will be returned. Otherwise `None`.
        """
        handlers = (e for e in self._events if e.event == event)
        if event.is_coroutine:
            return asyncio.gather(*(h.invoke(*args, **kwargs) for h in handlers))  # type: ignore
        for handler in handlers:
            handler.invoke(*args, **kwargs)

    async def commands_in_sync(self, guild: Snowflake | None = None) -> bool:
        """Checks if the the commands locally registered to this client are in sync with the commands on discord.

        Parameters
        ----------
        guild : `Snowflake`, optional
            The guild to check commands from. If left blank, checks global commands.

        Returns
        -------
        `bool`
            Returns true if the local commands match the remote commands.
        """
        local = {c.name: c.to_dict() for c in self.tree.get_commands(guild=guild)}
        remote = {
            c.name: {
                "nsfw": c.nsfw,
                "dm_permission": c.dm_permission,
                "default_member_permissions": c.default_member_permissions,
                **c.to_dict(),
            }
            for c in await self.tree.fetch_commands(guild=guild)
        }

        # Check for commands that only appear in one location
        if len(set(local.keys()).symmetric_difference(remote.keys())) > 0:
            return False

        # Check for changes to existing commands
        return is_dict_subset(remote, local)

    def load(self, search_modules: list[str] | None = None) -> None:
        """Recursively search the specified modules and register all widgets found.

        Parameters
        ----------
        search_modules : `list[str]`, optional
            The modules to search through, will use the modules specified in the constructor by default
        """
        self._load_modules(
            search_modules or self._search_modules or _default_modules,
            search_modules is None and self._search_modules is None,
        )

    async def start(self, token: str | None = None, *, reconnect: bool = True) -> None:
        """A Shorthand coroutine for `load` + `login` + `connect`.

        Also loads the .env file if it is found in the project directory.

        Parameters
        ----------
        token: `str`
            The authentication token. Do not prefix this token with
            anything as the library will do it for you.
        reconnect: `bool`
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled (such as
            invalid sharding payloads or bad tokens).
        """
        load_dotenv()
        self.load()

        if token is None and _environ_key_token not in os.environ:
            raise RuntimeError("Bot token was not supplied in parameters or eviron.")
        token = token or os.environ[_environ_key_token]

        await super().start(token, reconnect=reconnect)

    def run(
        self,
        token: str | None = None,
        *,
        reconnect: bool = True,
        log_handler: logging.Handler | None = MISSING,
        log_formatter: logging.Formatter = MISSING,
        log_level: int = MISSING,
        root_logger: bool = False,
    ) -> None:
        """A blocking call that abstracts away the event loop
        initialisation from you.

        If you want more control over the event loop then this
        function should not be used. Use `start` coroutine
        or `connect` + `login`.

        This function also sets up the logging library to make it easier
        for beginners to know what is going on with the library. For more
        advanced users, this can be disabled by passing ``None`` to
        the ``log_handler`` parameter.

        WARNING
        -------
        This function must be the last function to call due to the fact that it
        is blocking. That means that registration of events or anything being
        called after this function call will not execute until it returns.

        Parameters
        -----------
        token: `str`
            The authentication token. Do not prefix this token with
            anything as the library will do it for you.
        reconnect: `bool`
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled (such as
            invalid sharding payloads or bad tokens).
        log_handler: `logging.Handler`, optional
            The log handler to use for the library's logger. If this is ``None``
            then the library will not set up anything logging related. Logging
            will still work if ``None`` is passed, though it is your responsibility
            to set it up.

            The default log handler if not provided is `logging.StreamHandler`.

        log_formatter: `logging.Formatter`
            The formatter to use with the given log handler. If not provided then it
            defaults to a colour based logging formatter (if available).

        log_level: `int`
            The default log level for the library's logger. This is only applied if the
            ``log_handler`` parameter is not ``None``. Defaults to ``logging.INFO``.

        root_logger: `bool`
            Whether to set up the root logger rather than the library logger.
            By default, only the library logger (``'discord'``) is set up. If this
            is set to ``True`` then the root logger is set up as well.

            Defaults to ``False``.
        """
        super().run(
            token,  # type: ignore
            reconnect=reconnect,
            log_handler=log_handler,
            log_formatter=log_formatter,
            log_level=log_level,
            root_logger=root_logger,
        )

    def event(self, coro: CoroT) -> CoroT:
        # override default event decorator to use new amethyst event system
        """A decorator that registers an event handler to listen.

        It is recommended to use the `amethyst.event` decorator instead of this as it supports type hints.
        """
        name: str = coro.__name__
        if not hasattr(events, name):
            raise TypeError(f"Could not find event '{name}'")

        event = getattr(events, name)

        if not isinstance(event, AmethystEvent):
            raise TypeError(f"Could not find a valid event called '{name}'")

        handler = AmethystEventHandler(event, coro)
        self.register_event(handler)

        return coro

    async def setup_hook(self) -> None:
        # Synchronise commands if out of date
        if os.getenv(_environ_key_auto_sync) != "false":
            guild = None
            if _environ_key_sync_guild in os.environ:
                guild = discord.Object(os.environ[_environ_key_sync_guild])
                self.tree.copy_global_to(guild=guild)

            if not await self.commands_in_sync(guild):
                _log.info("Synchronising Commands...")
                await self.tree.sync(guild=guild)

        # Invoke subscribed handlers
        await self.invoke_event(events.on_setup_hook)

    async def on_ready(self):
        """override on_ready event."""
        if self.user is None:
            raise AttributeError("Expected client to be logged in.")
        name = self.user.global_name or f"{self.user.name}#{self.user.discriminator}"
        _log.info(
            "Client connected as '%s' with %sms ping.",
            name,
            round(self.latency * 1000),
        )

        # Start schedule loop
        if self._schedule_sleep_task is None and len(self._schedules) > 0:
            self.loop.create_task(self._schedule_loop())

        # Invoke subscribed handlers
        await self.invoke_event(events.on_ready)

    async def _schedule_loop(self):
        """Is responsible for calling schedules"""
        while not self.is_closed():
            schedule_map = {s: s.next_occurrence() for s in self._schedules}
            next_datetime = min(schedule_map.values())

            while True:
                delay = (next_datetime - datetime.now()).total_seconds()
                final = delay <= _schedule_delay_cutoff

                if not final:
                    delay /= 2

                # Sleep until next point
                self._schedule_sleep_task = asyncio.Task(asyncio.sleep(delay))
                try:
                    await self._schedule_sleep_task
                except asyncio.CancelledError:
                    break  # Break to recalculate next_datetime

                # Invoke schedules
                if final:
                    schedules = [s for s, d in schedule_map.items() if d == next_datetime]
                    _log.debug("Invoking schedules %s", schedules)
                    asyncio.gather(*(s.invoke() for s in schedules))
                    await asyncio.sleep(1)  # sleep until the end of the second
                    break  # Break and recalculate for next schedule

    def _build_loader(self) -> dynamicpy.DynamicLoader:
        """Builds a DynamicLoader for finding widgets to add to the client."""
        loader = dynamicpy.DynamicLoader()

        loader.register_type_handler(
            lambda _, v: try_register(self.register_command, v), AmethystCommand
        )
        loader.register_type_handler(
            lambda _, v: try_register(self.register_event, v), AmethystEventHandler
        )
        loader.register_type_handler(
            lambda _, v: try_register(self.register_schedule, v), AmethystSchedule
        )
        loader.register_handler(
            lambda _, v: try_register(self.register_plugin, v),
            lambda _, v: isinstance(v, type)
            and v is not AmethystPlugin
            and issubclass(v, AmethystPlugin),
        )

        return loader

    def _load_modules(self, search_modules: list[str], allow_missing: bool = False) -> None:
        """Loads the modules specified in `search_modules` using the client's DynamicLoader."""
        _log.debug("Loading modules %s", search_modules)
        for module in search_modules:
            if self.home_package is None and module.startswith("."):
                module = module[1:]
            try:
                self._loader.load_module(module, self.home_package)
            except ImportError:
                if not allow_missing:
                    raise

    def _get_home_package(self) -> str | None:
        """Return the home package of the application."""
        try:
            module = dynamicpy.get_foreign_module()

            if dynamicpy.is_package(module):
                package = module
            else:
                package = dynamicpy.get_module_parent(module)

            _log.debug("Home package located as '%s'", package)
            return package
        except dynamicpy.NoParentError:
            _log.debug("Instantiating module is top-level.")
            return None
        except ImportError as e:
            _log.error("Error locating home package: %s", e)
            raise error.ModuleLocateError("Error locating home package") from e
