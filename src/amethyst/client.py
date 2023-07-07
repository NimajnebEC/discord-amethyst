import asyncio
import logging
from typing import Any, Callable, Coroutine, Self, Type, TypeVar, overload

import discord
import dynamicpy
from discord import app_commands
from discord.abc import Snowflake

from amethyst import error
from amethyst.util import is_dict_subset
from amethyst.widget import (
    AmethystCommand,
    AmethystEvent,
    AmethystEventHandler,
    AmethystPlugin,
    DiscordPyEvent,
    events,
)

__all__ = ("AmethystClient",)

_default_modules = [".commands"]

_log = logging.getLogger(__name__)

CoroT = TypeVar("CoroT", bound=Callable[..., Coroutine[Any, Any, Any]])


class AmethystClient(discord.Client):
    def __init__(
        self,
        intents: discord.Intents,
        *,
        search_modules: list[str] | None = None,
        **options: Any,
    ) -> None:
        super().__init__(intents=intents, **options)
        self._search_modules = search_modules or _default_modules
        self._home_package: str | None = self._get_home_package()
        self._loader: dynamicpy.DynamicLoader = self._build_loader()
        self._tree: app_commands.CommandTree[Self] = app_commands.CommandTree(self)
        self._dependencies: dynamicpy.DependencyLibrary = dynamicpy.DependencyLibrary()
        self._events: dict[AmethystEvent, list[AmethystEventHandler]] = {}

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
        dependency : Any
            The dependency to add the library.

        Raises
        ------
        TypeError
            Raised when attempting to add a type to the library.
        DuplicateDependencyError
            Raised when another dependency with that type already exists in the library.
        """
        self._dependencies.add(dependency)

    def register_command(self, command: AmethystCommand) -> None:
        """Register an instance of `AmethystCommand` to the client.

        Parameters
        ----------
        command : AmethystCommand
            The command to register.
        """
        _log.debug("Registering command '%s'", command.name)
        self._tree.add_command(command)

    def register_plugin(self, plugin: Type[AmethystPlugin]) -> None:
        """Register an `AmethystPlugin` to the client.

        Parameters
        ----------
        plugin : Type[AmethystPlugin]
            A type inheriting from `AmethystPlugin` to register to the client.
        """
        _log.debug("Registering plugin '%s'", plugin.__name__)

        try:
            instance = plugin.__new__(plugin)
            instance._client = self  # add client attribute
            self._dependencies.inject(instance.__init__)
        except dynamicpy.DependencyNotFoundError as e:
            raise error.RegisterPluginError(
                f"Could not find a dependency when injecting into '{plugin.__name__}'"
            ) from e
        except dynamicpy.InjectDependenciesError as e:
            raise error.RegisterPluginError(
                f"Error injecting dependencies into '{plugin.__name__}'"
            ) from e

        self._loader.load_object(instance)

    def register_event(self, handler: AmethystEventHandler) -> None:
        """Register an `AmethystEventHandler` to the client.

        Parameters
        ----------
        event : AmethystEvent
            The instance `AmethystEventHandler` to register to the client.
        """
        event = handler.event
        _log.debug(
            "Registering handler '%s' for event '%s'",
            handler.callback.__name__,
            event.name,
        )

        if event not in self._events:
            self._events[event] = []

            # Setup invoker for default events
            if isinstance(handler.event, DiscordPyEvent) and not hasattr(self, event.name):
                setattr(
                    self,
                    event.name,
                    lambda *args, **kwargs: self.invoke_event(event, *args, **kwargs),
                )

        # Add handler to event map
        self._events[event].append(handler)

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
        event : AmethystEvent
            The event to invoke the handlers of.

        Returns
        -------
        Coroutine | None
            When the event is a coroutine, a `Coroutine` will be returned. Otherwise `None`.
        """
        handlers = self._events.get(event, [])
        if event.is_coroutine:
            return asyncio.gather(*(h.invoke(*args, **kwargs) for h in handlers))  # type: ignore
        for handler in handlers:
            handler.invoke(*args, **kwargs)

    async def commands_in_sync(self, guild: Snowflake | None = None) -> bool:
        """Checks if the the commands locally registered to this client are in sync with the commands on discord.

        Parameters
        ----------
        guild : Snowflake, optional
            The guild to check commands from. If left blank, checks global commands.

        Returns
        -------
        bool
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
        search_modules : list[str], optional
            The modules to search through, will use the modules specified in the constructor by default
        """
        self._load_modules(search_modules or self._search_modules)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        """A Shorthand coroutine for `load` + `login` + `connect`.

        Parameters
        ----------
        token: str
            The authentication token. Do not prefix this token with
            anything as the library will do it for you.
        reconnect: bool
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled (such as
            invalid sharding payloads or bad tokens).
        """
        self.load()
        await super().start(token, reconnect=reconnect)

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

        handler = AmethystEventHandler(coro, event)
        self.register_event(handler)

        return coro

    async def setup_hook(self) -> None:
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

        # Invoke subscribed handlers
        await self.invoke_event(events.on_ready)

    def _build_loader(self) -> dynamicpy.DynamicLoader:
        """Builds a DynamicLoader for finding widgets to add to the client."""
        loader = dynamicpy.DynamicLoader()

        loader.register_type_handler(lambda _, v: self.register_command(v), AmethystCommand)
        loader.register_type_handler(
            lambda _, v: self.register_event(v), AmethystEventHandler
        )
        loader.register_handler(
            lambda _, v: self.register_plugin(v),
            lambda _, v: isinstance(v, type)
            and v is not AmethystPlugin
            and issubclass(v, AmethystPlugin),
        )

        return loader

    def _load_modules(self, search_modules: list[str]) -> None:
        """Loads the modules specified in `search_modules` using the client's DynamicLoader."""
        _log.debug("Loading modules %s", search_modules)
        for module in search_modules:
            if self.home_package is None and module.startswith("."):
                module = module[1:]
            self._loader.load_module(module, self.home_package)

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
