# Discord Amethyst

An opinionated extension for [discord.py](https://github.com/Rapptz/discord.py). Amethyst adds a handful of features that I found myself re-implementing or wanting for many of my Discord bots such as automatic app command synchronisation and job scheduling.

## Widgets

### Command

The amethyst command decorator is just a wrapper around discord.py's `app_commands.command` decorator. Please refer to the [discord.py documentation](https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=app_commands%20command#discord.app_commands.command) for usage.

### Event

Amethyst's event decorator is a type hinted wrapper around [discord.py's normal event decorator](https://discordpy.readthedocs.io/en/stable/api.html?highlight=client%20event#discord.Client.event). The primary difference is that you must specify which event you wish to subscribe to. The property `amethyst.events` is a module containing all of the [default discord.py events](https://discordpy.readthedocs.io/en/stable/api.html?highlight=client%20event#event-reference).

```py
import amethyst

@amethyst.event(amethyst.events.on_ready)
async def on_ready():
    print("Bot is ready!")
```

### Schedule

Amethyst implements a [cron-like](https://en.wikipedia.org/wiki/Cron) asynchronous scheduler for calling functions on a set schedule, powered by [croniter](https://github.com/kiorky/croniter).

The following is an example of a schedule that will run every day at 8 am.

```py
import amethyst

@amethyst.schedule("0 8 * * *")
async def every_morning():
    print("Good morning!")
```

## Dynamic Module Import

Amethyst can dynamically load python modules, powered by [dynamicpy](https://github.com/NimajnebEC/dynamicpy#dynamicloader). When run, the client will automatically import and register any widgets found in the `.command`, `.commands`, `.plugin` and `.plugins` submodules. The submodules which are searched can be configured in the `AmethystClient`'s constructor.

Lets say you have the following project structure:

```
my-bot/
├── __init__.py
├── main.py
└── commands/
    ├── __init__.py
    ├── foo.py
    └── bar.py
```

If your instance of `AmethystClient` is instantiated in `main.py` then the `commands/` package will be recursively searched for widgets to register.

The searched modules can also be top-level, the only requirement is that they are at the same level as the module inside which the client was instantiated.

```
my-bot.py
plugins.py
commands/
├── __init__.py
├── foo.py
└── bar.py
```

In this example, the `commands.py` module and the `commands/` package will be searched.

## Plugin System

Amethyst has a plugin system, powered by [dynamicpy](https://github.com/NimajnebEC/dynamicpy) and inspired by [discord.py Cogs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html). You can create a plugin by simply defining a class that extends `AmethystPlugin`. If this is found by the [Dynamic Module Importer](#dynamic-module-import) then it will be automatically registered to the client, otherwise you will have to use the `AmethystClient.register_plugin` method.

An example plugin may look like the following:

```py
import amethyst

class ExamplePlugin(amethyst.AmethystPlugin):

    @amethyst.event(amethyst.events.on_ready)
    async def on_ready(self):
        channel = self.client.get_channel(000000000000000000)
        await channel.send("Bot is ready!")
```

### Plugin Dependency Injection

Amethyst plugins support [dynamicpy dependency injection](https://github.com/NimajnebEC/dynamicpy#dependencylibrary) for their constructors. You can add dependencies to the client using the `AmethystClient.add_dependency` method, which will then be injected into constructor parameters when the plugin is registered.

```py
import mysql.connector
import amethyst

client = amethyst.AmethystClient(...)
database: mysql.connector.MySQLConnection = mysql.connector.connect(...)
client.add_dependency(database)

class ExamplePlugin(amethyst.AmethystPlugin):

    def __init__(self, database: mysql.connector.MySQLConnection) -> None:
        self.database = database

```

## Evironment Variables

Amethyst uses [python-dotenv](https://pypi.org/project/python-dotenv/) to load `.env` files found at the project root. This can be used to configure certain aspects of the library.

| Name                | Default | Description                                                                                     |
| ------------------- | ------- | ----------------------------------------------------------------------------------------------- |
| AMETHYST_BOT_TOKEN  | _None_  | If present, `token` can be omitted from the `AmethystClient.run` and this will be used instead. |
| AMETHYST_AUTO_SYNC  | true    | If `true`, the client will synchronise app_commands if they are out of date with Discord.       |
| AMETHYST_SYNC_GUILD | _None_  | If present, app_commands will only be synchronised to specified guild id.                       |

## Roadmap

- [ ] Context Menus
- [ ] Hybrid Commands
- [ ] Plugins enable/disable after initialisation
- [ ] Debug mode featuring automatic reload
