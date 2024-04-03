from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    Coroutine,
    ParamSpec,
    Self,
    Type,
    TypeAlias,
    TypeVar,
)

import discord
import dynamicpy
import environ
import envnull
import lavender

from amethyst import error
from amethyst.util import classproperty, is_dict_subset, safesubclass

if TYPE_CHECKING:
    from amethyst.widget.event import Event

__all__ = ("Client", "Plugin", "BaseWidget", "WidgetPlugin")

WidgetT = TypeVar("WidgetT", bound="BaseWidget[Any]")
PluginT = TypeVar("PluginT", bound="Plugin")
P = ParamSpec("P")
T = TypeVar("T")

PluginSelf: TypeAlias = "Self@Plugin"  # type: ignore
CallbackT = TypeVar("CallbackT", bound=Callable[Concatenate[PluginSelf, ...], Any])
Coro = Coroutine[Any, Any, T]

_default_modules = [".command", ".commands", ".plugins", ".plugin"]
_log = logging.getLogger(__name__)


class Client(discord.Client):
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

    ##region Public Methods

    def __init__(
        self,
        intents: discord.Intents,
        **options: Any,
    ) -> None:
        super().__init__(intents=intents, **options)
        self._instantiating_package = self._get_instantiating_package()
        self._setup_hooks: list[Callable[..., Coro[None]]] = []
        self._auto_sync = envnull.AMETHYST_AUTO_SYNC is not None
        self._tree = discord.app_commands.CommandTree(self)
        self._dependencies = dynamicpy.DependencyLibrary()
        self._module_loader = self._build_module_loader()
        self._plugins: dict[Type[Plugin], Plugin] = {}
        self._tasks: list[Coro[Any]] | None = []
        self._widgets: list[BaseWidget] = []

        self._guild = None
        if envnull.AMETHYST_GUILD is not None:
            self._guild = int(envnull.AMETHYST_GUILD)

    @property
    def allowed_guild(self) -> int | None:
        """If present, the bot will ignore all events from guilds with a different id."""
        return self._guild

    @property
    def tree(self) -> discord.app_commands.CommandTree:
        """The command tree responsible for handling the application commands in this bot."""
        return self._tree

    def has_plugin(self, plugin: Type[Plugin]) -> bool:
        """Checks if the specified plugin has been registered with this client.

        Parameters
        ----------
        plugin : `Type[Plugin]`
            The plugin to check if its been registered.

        Returns
        -------
        bool
            `True` if the plugin has been registered.
        """
        return plugin in self._plugins

    def get_plugin(self, plugin: Type[PluginT]) -> PluginT:
        """Gets the registered instance of the specified plugin.

        Parameters
        ----------
        plugin : `Type[PluginT]`
            The plugin to get an instance of.

        Returns
        -------
        `PluginT`
            The registered instance of the specified plugin.

        Raises
        ------
        `KeyError`
            Raised if no such plugin has been registered.
        """
        if plugin in self._plugins:
            return self._plugins[plugin]  # type: ignore
        raise KeyError(f"Plugin {plugin.name} not registered.")

    def load_plugins(self, modules: list[str] = _default_modules) -> None:
        """Load all plugins found in the specified modules and their submodules.

        Parameters
        ----------
        modules : `list[str]`, optional
            The list of modules to recursively search.
        """
        _log.debug("Loading modules %s", modules)
        for module in modules:
            if self._instantiating_package is None and module.startswith("."):
                module = module[1:]
            with contextlib.suppress(ImportError):
                self._module_loader.load_module(module, self._instantiating_package)

    def register_plugin(self, plugin: Type[Plugin]) -> None:
        """Register the specified plugin and all its widgets.

        Parameters
        ----------
        plugin : `Type[Plugin]`
            The plugin to register.

        Raises
        ------
        `DuplicatePluginError`
            Raised if the plugin has already been registered.
        `PluginDependencyError`
            Raised if there was an error while injecting dependencies.
        """
        if plugin in self._plugins:
            raise error.DuplicatePluginError(f"{plugin.name} has already been registered.")
        _log.debug("Registering plugin '%s'", plugin.name)

        # * Instantiate Plugin
        try:
            instance = plugin.__new__(plugin)
            setattr(instance, "_client", self)
            self._dependencies.inject(instance.__init__)
        except (dynamicpy.DependencyNotFoundError, dynamicpy.InjectDependenciesError) as e:
            raise error.PluginDependencyError(
                f"Error injecting dependencies into '{plugin.name}'"
            ) from e

        # * Load widgets
        loader = dynamicpy.DynamicLoader()

        @loader.widget_handler(BaseWidget)
        def _(widget: BaseWidget):
            if widget not in self._widgets:
                widget.register(instance, self)
                self._widgets.append(widget)

        loader.load_object(instance)

        # * Add to plugins list
        self._plugins[plugin] = instance

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

    async def wait_for(
        self,
        event: "Event[P]",
        /,
        *,
        check: Callable[P, bool] | None = None,
        timeout: float | None = None,
    ) -> None:
        """
        Waits for a WebSocket event to be dispatched.

        This could be used to wait for a user to reply to a message,
        or to react to a message, or to edit a message in a self-contained
        way.

        The ``timeout`` parameter is passed onto :func:`asyncio.wait_for`. By default,
        it does not timeout. Note that this does propagate the
        :exc:`asyncio.TimeoutError` for you in case of timeout and is provided for
        ease of use.

        In case the event returns multiple arguments, a :class:`tuple` containing those
        arguments is returned instead. Please check the
        documentation for a list of events and their
        parameters.

        This function returns the **first event that meets the requirements**.


        Parameters
        ----------
        event : `Event[P]`
            The event to wait for.
        check : `Callable[P, bool] | None`, optional
            A predicate to check what to wait for. The arguments must meet the
            parameters of the event being waited for.
        timeout : `float | None`, optional
            The number of seconds to wait before timing out and raising `asyncio.TimeoutError`.
        """
        await super().wait_for(event.name, check=check, timeout=timeout)

    def event(
        self, event: "Event[P]"
    ) -> Callable[[Callable[P, Coro[None]]], Callable[P, Coro[None]]]:
        """A decorator that registers an event to listen to.

        Parameters
        ----------
        event : `Event`
            The event to listen to.
        """

        def decorator(func: Callable[P, Coro[None]]) -> Callable[P, Coro[None]]:
            from amethyst.widget.event import EventWidget

            EventWidget(func, event).register(None, self)  # type: ignore
            return func

        return decorator

    def create_task(self, task: Coro[Any]) -> None:
        """Creates an asynchronous task to be started once the event loop is set-up.

        Parameters
        ----------
        task : `Coro[Any]`
            The coroutine to start.
        """
        if self._tasks is None:
            self.loop.create_task(task)
        else:
            self._tasks.append(task)

    async def tree_changed(self, guild: discord.abc.Snowflake | None = None) -> bool:
        """Checks if the local application command tree is different from the remote.

        Parameters
        ----------
        guild : `discord.abc.Snowflake | None`, optional
            The guild to check the commands against. If not passed then global commands are checked instead.

        Returns
        -------
        `bool`
            `True` if the application commands do not match.
        """
        remotes = await self.tree.fetch_commands(guild=guild)
        locals = self.tree.get_commands(guild=guild)

        if len(remotes) != len(locals):
            return True

        for local in locals:
            subset = local.to_dict()
            remote = discord.utils.get(
                remotes,
                name=local.name,
                type=discord.AppCommandType(subset["type"]),
            )

            if remote is None:
                return True

            superset = {
                "default_member_permissions": None
                if remote.default_member_permissions is None
                else remote.default_member_permissions.value,
                "dm_permission": remote.dm_permission,
                "nsfw": remote.nsfw,
                **remote.to_dict(),
            }

            # USER and MESSAGE commands have an empty string for their description
            # https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-structure
            if subset["type"] in (
                discord.AppCommandType.message,
                discord.AppCommandType.user,
            ):
                subset["description"] = ""

            if not is_dict_subset(superset, subset):
                return True

        return False

    async def refresh_tree(self, guild: discord.abc.Snowflake | None = None) -> None:
        """Synchronises the application command tree if it has changed.

        Parameters
        ----------
        guild : `discord.abc.Snowflake | None`, optional
            The guild to refresh the commands to. If not passed then global commands are refreshed instead.
        """
        if await self.tree_changed(guild):
            _log.info("Synchronising application tree...")
            await self.tree.sync(guild=guild)
        else:
            _log.debug("Skipping tree synchronisation - already up to date.")

    def guild_allowed(self, check: discord.Guild | int | None) -> bool:
        """Checks if the specified guild is allowed based on the `AMETHYST_GUILD` environment variable.

        Parameters
        ----------
        check : `discord.Guild | int | None`
            The guild to check.

        Returns
        -------
        bool
            `True` if guild is allowed.
        """
        if self.allowed_guild is None:
            return True

        if isinstance(check, discord.Guild):
            return check.id == self.allowed_guild
        if isinstance(check, int):
            return check == self.allowed_guild
        return False

    def run(
        self,
        *,
        reconnect: bool = True,
        guild: int | None = -1,
        token: str | None = None,
        log_level: int = logging.INFO,
        auto_sync: bool | None = None,
        log_filters: dict[str, int] = {},
        plugin_modules: list[str] = _default_modules,
    ) -> None:
        """A blocking call that abstracts away the event loop
        initialisation from you.

        This function also sets up [Lavender Logging](https://github.com/NimajnebEC/lavender-logging).

        Parameters
        ----------
        token : `str | None`, optional
            The authentication token. If not specified it will be taken from the `AMETHYST_TOKEN` environment variable.
        reconnect : `bool`, optional
           If we should attempt reconnecting, either due to internet failure or a specific failure on Discord's part. Certain
           disconnects that lead to bad state will not be handled (such as invalid sharding payloads or bad tokens).
        guild : `int | None`, optional
            Overrides the `AMETHYST_GUILD` environment variable. If not `None` then the bot will only handle events from the specified guild.
        guild : `bool | None`, optional
            Overrides the `AMETHYST_AUTO_SYNC` environment variable. If `True` then the application command tree will be refreshed automatically.
        log_level : `int`, optional
            The default log level for Lavender's logger.
        log_filters : `dict[str, int]`, optional
            Initial logging filter patterns, by default no specific filters are specified.
        plugin_modules : `list[str]`, optional
            A list of modules to recursively search of plugins.
        """
        if guild != -1:
            self._guild = guild
        if auto_sync is not None:
            self._auto_sync = auto_sync

        lavender.setup(level=log_level, filter_config=log_filters)
        self.load_plugins(plugin_modules)
        return super().run(
            token or environ.AMETHYST_TOKEN,
            reconnect=reconnect,
            log_handler=None,
        )

    ##endregion

    ##region Events

    async def setup_hook(self) -> None:
        # ensure that all hooks are run before continuing
        await asyncio.gather(*(h() for h in self._setup_hooks))

        if self._auto_sync:
            guild = None
            if self._guild is not None:
                guild = discord.Object(self._guild)
                self.tree.copy_global_to(guild=guild)
            await self.refresh_tree(guild)

        # Run pending tasks
        if self._tasks is not None:
            for task in self._tasks:
                self.loop.create_task(task)
            self._tasks = None

    async def on_ready(self) -> None:
        if self.user is None:
            raise AttributeError("Expected client to be logged in.")
        name = self.user.global_name or f"{self.user.name}#{self.user.discriminator}"
        _log.info(
            "Client connected as '%s' with %sms ping.",
            name,
            round(self.latency * 1000),
        )

    ##endregion

    ##region Private Methods

    def _build_module_loader(self) -> dynamicpy.DynamicLoader:
        """Build the `DynamicLoader` used for finding plugins in modules."""
        loader = dynamicpy.DynamicLoader()

        @loader.handler()
        def _(_, value: Any):
            if (
                value is not Plugin
                and safesubclass(value, Plugin)
                and not issubclass(value, WidgetPlugin)
            ):
                with contextlib.suppress(error.DuplicatePluginError):
                    self.register_plugin(value)

        return loader

    def _get_instantiating_package(self) -> str | None:
        """Return the package the application was instantiated from."""

        try:
            module = dynamicpy.get_foreign_module()

            if dynamicpy.is_package(module):
                package = module
            else:
                package = dynamicpy.get_module_parent(module)

            _log.debug("Instantiating package located as '%s'", package)
            return package
        except dynamicpy.NoParentError:
            _log.debug("Instantiating module is top-level.")
            return None
        except ImportError as e:
            raise error.ModuleLocateError("Error locating instantiating package") from e

    ##endregion


class Plugin:
    """The base class for all Amethyst plugins to inherit from."""

    def __init__(self) -> None:
        """The client will attempt to bind constructor parameters to dependencies when registered."""

    @property
    def client(self) -> Client:
        """The instance of `Client` this plugin has been registered to."""
        return getattr(self, "_client") if hasattr(self, "_client") else None  # type: ignore

    @classproperty
    def name(cls):
        """The name of this plugin."""
        return cls.__qualname__


class BaseWidget(dynamicpy.BaseWidget[CallbackT]):
    """The base class for all Amethyst widgets to inherit from."""

    def __init__(self, callback: CallbackT) -> None:
        super().__init__(callback)

    def register(self, plugin: Plugin, client: Client) -> None:
        """Register the widget with the provided `Client`.

        Parameters
        ----------
        plugin: `Plugin`
            The plugin this widget belongs to.
        client : `Client`
            The client to register the widget with.
        """
        raise NotImplementedError(f"{self.type} must implement 'register'")

    @classproperty
    def type(cls) -> str:
        """The name of the type of widget."""
        return cls.__qualname__

    @property
    def name(self) -> str:
        """The name of this widget instance."""
        return self.callback.__qualname__


class _WidgetPluginMeta(type):
    """Metaclass for injecting plugin registration into widgets."""

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        loader = dynamicpy.DynamicLoader()
        loader.register_handler(cls._inject, lambda _, v: safesubclass(v, BaseWidget))
        loader.load_object(cls)
        return cls

    def _inject(cls, _, widget) -> None:
        """Inject the plugin's registration method into the widget's registration method."""

        def proxy(widget, plugin: Plugin, client: Client) -> None:
            if not client.has_plugin(cls):
                # todo: protect against circular widget dependencies
                client.register_plugin(cls)
            widget_plugin = client.get_plugin(cls)  # type: ignore
            cls.register(widget_plugin, widget, plugin)  # type: ignore

        setattr(widget, "register", proxy)


class WidgetPlugin(Plugin, metaclass=_WidgetPluginMeta):
    """Base class for wiget plugins, allowing for the creation of more complex widgets."""

    def register(self, widget: BaseWidget, plugin: Plugin):
        """Register the provided widget with the client.

        Parameters
        ----------
        widget : `BaseWidget`
            The widget to be registered.
        plugin : `Plugin`
            The plugin this widget belongs to.
        """
        raise NotImplementedError(f"{self.name} must implement 'register'")
