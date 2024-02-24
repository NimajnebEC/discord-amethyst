import datetime
from typing import List, Sequence

import discord
from discord import app_commands

from amethyst.widget.event.widget import DiscordEvent

__all__ = (
    "on_app_command_completion",
    "on_audit_log_entry_create",
    "on_automod_action",
    "on_automod_rule_create",
    "on_automod_rule_delete",
    "on_automod_rule_update",
    "on_bulk_message_delete",
    "on_connect",
    "on_disconnect",
    "on_guild_available",
    "on_guild_channel_create",
    "on_guild_channel_delete",
    "on_guild_channel_pins_update",
    "on_guild_channel_update",
    "on_guild_emojis_update",
    "on_guild_integrations_update",
    "on_guild_join",
    "on_guild_remove",
    "on_guild_role_create",
    "on_guild_role_delete",
    "on_guild_role_update",
    "on_guild_stickers_update",
    "on_guild_update",
    "on_integration_create",
    "on_integration_update",
    "on_interaction",
    "on_invite_create",
    "on_invite_delete",
    "on_member_ban",
    "on_member_join",
    "on_member_remove",
    "on_member_unban",
    "on_member_update",
    "on_message",
    "on_message_delete",
    "on_message_edit",
    "on_presence_update",
    "on_private_channel_pins_update",
    "on_private_channel_update",
    "on_raw_app_command_permissions_update",
    "on_raw_bulk_message_delete",
    "on_raw_integration_delete",
    "on_raw_member_remove",
    "on_raw_message_delete",
    "on_raw_message_edit",
    "on_raw_reaction_add",
    "on_raw_reaction_clear",
    "on_raw_reaction_clear_emoji",
    "on_raw_reaction_remove",
    "on_raw_thread_delete",
    "on_raw_thread_member_remove",
    "on_raw_thread_update",
    "on_raw_typing",
    "on_reaction_add",
    "on_reaction_clear",
    "on_reaction_clear_emoji",
    "on_reaction_remove",
    "on_ready",
    "on_resumed",
    "on_scheduled_event_create",
    "on_scheduled_event_delete",
    "on_scheduled_event_update",
    "on_scheduled_event_user_add",
    "on_scheduled_event_user_remove",
    "on_socket_event_type",
    "on_socket_raw_receive",
    "on_socket_raw_send",
    "on_stage_instance_create",
    "on_stage_instance_delete",
    "on_stage_instance_update",
    "on_thread_create",
    "on_thread_delete",
    "on_thread_join",
    "on_thread_member_join",
    "on_thread_member_remove",
    "on_thread_remove",
    "on_thread_update",
    "on_user_update",
    "on_voice_state_update",
    "on_webhooks_update",
    "on_setup_hook",
)

on_raw_app_command_permissions_update: DiscordEvent[
    discord.RawAppCommandPermissionsUpdateEvent
] = DiscordEvent("on_raw_app_command_permissions_update")
"""Called when application command permissions are updated.

Parameters
----------
payload: RawAppCommandPermissionsUpdateEvent
    The raw event payload data.
"""

on_app_command_completion: DiscordEvent[
    [discord.Interaction, app_commands.Command | app_commands.ContextMenu]
] = DiscordEvent("on_app_command_completion")
"""Called when a app_commands.Command or app_commands.ContextMenu has successfully completed without error.

Parameters
----------
interaction: Interaction
    The interaction of the command.
command: Union[app_commands.Command, app_commands.ContextMenu]
    The command that completed successfully
"""

on_automod_rule_create: DiscordEvent[discord.AutoModRule] = DiscordEvent(
    "on_automod_rule_create"
)
"""Called when a AutoModRule is created. You must have manage_guild to receive this.

This requires Intents.auto_moderation_configuration to be enabled.

Parameters
----------
rule: AutoModRule
    The rule that was created.
"""

on_automod_rule_update: DiscordEvent[discord.AutoModRule] = DiscordEvent(
    "on_automod_rule_update"
)
"""Called when a AutoModRule is updated. You must have manage_guild to receive this.

This requires Intents.auto_moderation_configuration to be enabled.

Parameters
----------
rule: AutoModRule
    The rule that was updated.
"""

on_automod_rule_delete: DiscordEvent[discord.AutoModRule] = DiscordEvent(
    "on_automod_rule_delete"
)
"""Called when a AutoModRule is deleted. You must have manage_guild to receive this.

This requires Intents.auto_moderation_configuration to be enabled.

Parameters
----------
rule: AutoModRule
    The rule that was deleted.
"""

on_automod_action: DiscordEvent[discord.AutoModAction] = DiscordEvent("on_automod_action")
"""Called when a AutoModAction is created/performed. You must have manage_guild to receive this.

This requires Intents.auto_moderation_execution to be enabled.

Parameters
----------
execution: AutoModAction
    The rule execution that was performed.
"""

on_guild_channel_delete: DiscordEvent[discord.abc.GuildChannel] = DiscordEvent(
    "on_guild_channel_delete"
)
"""Called whenever a guild channel is deleted.

This requires Intents.guilds to be enabled.

Parameters
----------
channel: abc.GuildChannel
    The guild channel that got deleted.
"""

on_guild_channel_create: DiscordEvent[discord.abc.GuildChannel] = DiscordEvent(
    "on_guild_channel_create"
)
"""Called whenever a guild channel is created.

This requires Intents.guilds to be enabled.

Parameters
----------
channel: abc.GuildChannel
    The guild channel that got created.
"""

on_guild_channel_update: DiscordEvent[
    [discord.abc.GuildChannel, discord.abc.GuildChannel]
] = DiscordEvent("on_guild_channel_update")
"""Called whenever a guild channel is updated. e.g. changed name, topic, permissions.

This requires Intents.guilds to be enabled.

Parameters
----------
before: abc.GuildChannel
    The updated guild channel's old info.
after: abc.GuildChannel
    The updated guild channel's new info.
"""

on_guild_channel_pins_update: DiscordEvent[
    [discord.abc.GuildChannel | discord.Thread, datetime.datetime]
] = DiscordEvent("on_guild_channel_pins_update")
"""Called whenever a message is pinned or unpinned from a guild channel.

This requires Intents.guilds to be enabled.

Parameters
----------
channel: Union[abc.GuildChannel, Thread]
    The guild channel that had its pins updated.
last_pin: Optional[datetime.datetime]
    The latest message that was pinned as an aware datetime in UTC. Could be None.
"""

on_private_channel_update: DiscordEvent[
    discord.GroupChannel, discord.GroupChannel
] = DiscordEvent("on_private_channel_update")
"""Called whenever a private group DM is updated. e.g. changed name or topic.

This requires Intents.messages to be enabled.

Parameters
----------
before: GroupChannel
    The updated group channel's old info.
after: GroupChannel
    The updated group channel's new info.
"""

on_private_channel_pins_update: DiscordEvent[
    [discord.abc.PrivateChannel, datetime.datetime | None]
] = DiscordEvent("on_private_channel_pins_update")
"""Called whenever a message is pinned or unpinned from a private channel.

Parameters
----------
channel: abc.PrivateChannel
    The private channel that had its pins updated.
last_pin: Optional[datetime.datetime]
    The latest message that was pinned as an aware datetime in UTC. Could be None.
"""


on_raw_typing: DiscordEvent[discord.RawTypingEvent] = DiscordEvent("on_raw_typing")
"""Called when someone begins typing a message. Unlike on_typing() this is called regardless of the channel and user being in the internal cache.

This requires Intents.typing to be enabled.

Parameters
----------
payload: RawTypingEvent
    The raw event payload data.
"""

on_connect: DiscordEvent[[]] = DiscordEvent("on_connect")
"""Called when the client has successfully connected to Discord. This is not the same as the client being fully prepared, see on_ready() for that.

The warnings on on_ready() also apply.
"""

on_disconnect: DiscordEvent[[]] = DiscordEvent("on_disconnect")
"""Called when the client has disconnected from Discord, or a connection attempt to Discord has failed.
This could happen either through the internet being disconnected, explicit calls to close, or Discord terminating the connection one way or the other.

This function can be called many times without a corresponding on_connect() call.
"""

on_socket_event_type: DiscordEvent[str] = DiscordEvent("on_socket_event_type")
"""Called whenever a websocket event is received from the WebSocket.

This is mainly useful for logging how many events you are receiving from the Discord gateway.

Parameters
----------
event_type: str
    The event type from Discord that is received, e.g. 'READY'.
"""

on_socket_raw_receive: DiscordEvent[str] = DiscordEvent("on_socket_raw_receive")
"""Called whenever a message is completely received from the WebSocket, before it's processed and parsed.
This event is always dispatched when a complete message is received and the passed data is not parsed in any way.

This is only really useful for grabbing the WebSocket stream and debugging purposes.

This requires setting the enable_debug_events setting in the Client.

Parameters
----------
msg: str
    The message passed in from the WebSocket library.
"""

on_socket_raw_send: DiscordEvent[bytes | str] = DiscordEvent("on_socket_raw_send")
"""Called whenever a send operation is done on the WebSocket before the message is sent. The passed parameter is the message that is being sent to the WebSocket.

This is only really useful for grabbing the WebSocket stream and debugging purposes.

This requires setting the enable_debug_events setting in the Client.

Parameters
----------
payload: Union[bytes, str]
    The message that is about to be passed on to the WebSocket library. It can be bytes to denote a binary message or str to denote a regular text message.
"""

on_ready: DiscordEvent[[]] = DiscordEvent("on_ready")
"""Called when the client is done preparing the data received from Discord. Usually after login is successful and the Client.guilds and co. are filled up.

WARNING
-------
This function is not guaranteed to be the first event called. Likewise, this function is not guaranteed to only be called once.
This library implements reconnection logic and thus will end up calling this event whenever a RESUME request fails.
"""

on_setup_hook: DiscordEvent[[]] = DiscordEvent("on_setup_hook")
"""
Called after the bot is logged in but before it has connected to the Websocket. Can be used to perform asynchronous setup.

This is only called once, in login(), and will be called before any events are dispatched, making it a better solution than doing such setup in the on_ready() event.

WARNING
-------
Since this is called before the websocket connection is made therefore anything that waits for the websocket will deadlock,
this includes things like wait_for() and wait_until_ready().
"""

on_resumed: DiscordEvent[[]] = DiscordEvent("on_resumed")
"""Called when the client has resumed a session."""

on_guild_available: DiscordEvent[discord.Guild] = DiscordEvent("on_guild_available")
"""Called when a guild becomes available. The guild must have existed in the Client.guilds cache.

This requires Intents.guilds to be enabled.

Parameters
----------
guild: Guild
    The Guild that has changed availability.
"""

on_guild_join: DiscordEvent[discord.Guild] = DiscordEvent("on_guild_join")
"""Called when a Guild is either created by the Client or when the Client joins a guild.

This requires Intents.guilds to be enabled.

Parameters
----------
guild: Guild
    The guild that was joined.
"""

on_guild_remove: DiscordEvent[discord.Guild] = DiscordEvent("on_guild_remove")
"""Called when a Guild is removed from the Client.

This happens through, but not limited to, these circumstances:
- The client got banned.
- The client got kicked.
- The client left the guild.
- The client or the guild owner deleted the guild.

In order for this event to be invoked then the Client must have been part of the guild to begin with. (i.e. it is part of Client.guilds)

This requires Intents.guilds to be enabled.

Parameters
----------
guild: Guild
    The guild that got removed.
"""

on_guild_update: DiscordEvent[discord.Guild, discord.Guild] = DiscordEvent(
    "on_guild_update"
)
"""Called when a Guild updates, for example:
- Changed name
- Changed AFK channel
- Changed AFK timeout
- etc

This requires Intents.guilds to be enabled.

Parameters
----------
before: Guild
    The guild prior to being updated.
after: Guild
    The guild after being updated.
"""

on_guild_emojis_update: DiscordEvent[
    discord.Guild, Sequence[discord.Emoji], Sequence[discord.Emoji]
] = DiscordEvent("on_guild_emojis_update")
"""Called when a Guild adds or removes Emoji.

This requires Intents.emojis_and_stickers to be enabled.

Parameters
----------
guild: Guild
    The guild that got their emojis updated.
before: Sequence[Emoji]
    A list of emojis before the update.
after: Sequence[Emoji]
    A list of emojis after the update.
"""

on_guild_stickers_update: DiscordEvent[
    [discord.Guild, Sequence[discord.GuildSticker], Sequence[discord.GuildSticker]]
] = DiscordEvent("on_guild_stickers_update")
"""Called when a Guild updates its stickers.

This requires Intents.emojis_and_stickers to be enabled.

Parameters
----------
guild: Guild
    The guild that got their stickers updated.
before: Sequence[GuildSticker]
    A list of stickers before the update.
after: Sequence[GuildSticker]
    A list of stickers after the update.
"""

on_audit_log_entry_create: DiscordEvent[discord.AuditLogEntry] = DiscordEvent(
    "on_audit_log_entry_create"
)
"""Called when a Guild gets a new audit log entry. You must have view_audit_log to receive this.

This requires Intents.moderation to be enabled.

WARNING
-------
Audit log entries received through the gateway are subject to data retrieval from cache rather than REST.
This means that some data might not be present when you expect it to be.
For example, the AuditLogEntry.target attribute will usually be a discord.Object and the AuditLogEntry.user attribute will depend on user and member cache.

To get the user ID of entry, AuditLogEntry.user_id can be used instead.

Parameters
----------
entry: AuditLogEntry
    The audit log entry that was created.
"""

on_invite_create: DiscordEvent[discord.Invite] = DiscordEvent("on_invite_create")
"""Called when an Invite is created. You must have manage_channels to receive this.

There is a rare possibility that the Invite.guild and Invite.channel attributes will be of Object rather than the respective models.

This requires Intents.invites to be enabled.

Parameters
----------
invite: Invite
    The invite that was created.
"""

on_invite_delete: DiscordEvent[discord.Invite] = DiscordEvent("on_invite_delete")
"""Called when an Invite is deleted. You must have manage_channels to receive this.

There is a rare possibility that the Invite.guild and Invite.channel attributes will be of Object rather than the respective models.
Outside of those two attributes, the only other attribute guaranteed to be filled by the Discord gateway for this event is Invite.code.

This requires Intents.invites to be enabled.

Parameters
----------
invite: Invite
    The invite that was deleted.
"""

on_integration_create: DiscordEvent[discord.Integration] = DiscordEvent(
    "on_integration_create"
)
"""Called when an integration is created.

This requires Intents.integrations to be enabled.

Parameters
----------
integration: Integration
    The integration that was created.
"""

on_integration_update: DiscordEvent[discord.Integration] = DiscordEvent(
    "on_integration_update"
)
"""Called when an integration is updated.

This requires Intents.integrations to be enabled.

Parameters
----------
integration: Integration
    The integration that was updated.
"""

on_guild_integrations_update: DiscordEvent[discord.Guild] = DiscordEvent(
    "on_guild_integrations_update"
)
"""Called whenever an integration is created, modified, or removed from a guild.

This requires Intents.integrations to be enabled.

Parameters
----------
guild: Guild
    The guild that had its integrations updated.
"""

on_webhooks_update: DiscordEvent[discord.abc.GuildChannel] = DiscordEvent(
    "on_webhooks_update"
)
"""Called whenever a webhook is created, modified, or removed from a guild channel.

This requires Intents.webhooks to be enabled.

Parameters
----------
channel: abc.GuildChannel
    The channel that had its webhooks updated.
"""

on_raw_integration_delete: DiscordEvent[discord.RawIntegrationDeleteEvent] = DiscordEvent(
    "on_raw_integration_delete"
)
"""Called when an integration is deleted.

This requires Intents.integrations to be enabled.

Parameters
----------
payload: RawIntegrationDeleteEvent
    The raw event payload data.
"""

on_interaction: DiscordEvent[discord.Interaction] = DiscordEvent("on_interaction")
"""Called when an interaction happened.

This currently happens due to slash command invocations or components being used.

WARNING
-------
This is a low-level function that is not generally meant to be used.
If you are working with components, consider using the callbacks associated with the View instead as it provides a nicer user experience.

Parameters
----------
interaction: Interaction
    The interaction data.
"""

on_member_join: DiscordEvent[discord.Member] = DiscordEvent("on_member_join")
"""Called when a Member joins a Guild.

This requires Intents.members to be enabled.

Parameters
----------
member: Member
    The member who joined.
"""

on_member_remove: DiscordEvent[discord.Member] = DiscordEvent("on_member_remove")
"""Called when a Member leaves a Guild.

If the guild or member could not be found in the internal cache, this event will not be called. You may use on_raw_member_remove() instead.

This requires Intents.members to be enabled.

Parameters
----------
member: Member
    The member who left.
"""

on_raw_member_remove: DiscordEvent[discord.RawMemberRemoveEvent] = DiscordEvent(
    "on_raw_member_remove"
)
"""Called when a Member leaves a Guild.

Unlike on_member_remove(), this is called regardless of the guild or member being in the internal cache.

This requires Intents.members to be enabled.

Parameters
----------
payload: RawMemberRemoveEvent
    The raw event payload data.
"""

on_member_update: DiscordEvent[discord.Member, discord.Member] = DiscordEvent(
    "on_member_update"
)
"""Called when a Member updates their profile.

This is called when one or more of the following things change:

- nickname
- roles
- pending
- timeout
- guild avatar
- flags

Due to a Discord limitation, this event is not dispatched when a member’s timeout expires.

This requires Intents.members to be enabled.

Parameters
----------
before: Member
    The updated member's old info.
after: Member
    The updated member's updated info.
"""

on_user_update: DiscordEvent[discord.User, discord.User] = DiscordEvent("on_user_update")
"""Called when a User updates their profile.

This is called when one or more of the following things change:

- avatar
- username
- discriminator

This requires Intents.members to be enabled.

Parameters
----------
before: User
    The updated user's old info.
after: User
    The updated user's updated info.
"""

on_member_ban: DiscordEvent[discord.Guild, discord.User | discord.Member] = DiscordEvent(
    "on_member_ban"
)
"""Called when a user gets banned from a Guild.

This requires Intents.moderation to be enabled.

Parameters
----------
guild: Guild
    The guild the user got banned from.
user: User | Member
    The user that got banned. Can be either User or Member depending on whether the user was in the guild or not at the time of removal.
"""

on_member_unban: DiscordEvent[discord.Guild, discord.User] = DiscordEvent("on_member_unban")
"""Called when a User gets unbanned from a Guild.

This requires Intents.moderation to be enabled.

Parameters
----------
guild: Guild
    The guild the user got unbanned from.
user: User
    The user that got unbanned.
"""

on_presence_update: DiscordEvent[discord.Member, discord.Member] = DiscordEvent(
    "on_presence_update"
)
"""Called when a Member updates their presence.

This is called when one or more of the following things change:
- status
- activity

This requires Intents.presences and Intents.members to be enabled.

Parameters
----------
before: Member
    The updated member's old info.
after: Member
    The updated member's updated info.
"""

on_message: DiscordEvent[discord.Message] = DiscordEvent("on_message")
"""Called when a Message is created and sent.

This requires Intents.messages to be enabled.

WARNING
-------
Your bot's own messages and private messages are sent through this event.
This can lead to cases of 'recursion' depending on how your bot was programmed.
If you want the bot to not reply to itself, consider checking the user IDs. Note that the Bot account does not have this problem.

Parameters
----------
message: Message
    The current message.
"""

on_message_edit: DiscordEvent[discord.Message, discord.Message] = DiscordEvent(
    "on_message_edit"
)
"""Called when a Message receives an update event.
If the message is not found in the internal message cache, then these events will not be called.
Messages might not be in the cache if the message is too old or the client is participating in high traffic guilds.

If this occurs, increase the max_messages parameter or use the on_raw_message_edit() event instead.

The following non-exhaustive cases trigger this event:
- A message has been pinned or unpinned.
- The message content has been changed.
- The message has received an embed. (Note: For performance reasons, the embed server does not do this in a 'consistent' manner.)
- The message's embeds were suppressed or unsuppressed.
- A call message has received an update to its participants or ending time.

This requires Intents.messages to be enabled.

Parameters
----------
before: Message
    The previous version of the message.
after: Message
    The current version of the message.
"""

on_message_delete: DiscordEvent[discord.Message] = DiscordEvent("on_message_delete")
"""Called when a message is deleted. If the message is not found in the internal message cache, then this event will not be called.
Messages might not be in the cache if the message is too old or the client is participating in high traffic guilds.

If this occurs, increase the max_messages parameter or use the on_raw_message_delete() event instead.

This requires Intents.messages to be enabled.

Parameters
----------
message: Message
    The deleted message.
"""

on_bulk_message_delete: DiscordEvent[List[discord.Message]] = DiscordEvent(
    "on_bulk_message_delete"
)
"""Called when messages are bulk deleted.
If none of the messages deleted are found in the internal message cache, then this event will not be called.
If individual messages were not found in the internal message cache, this event will still be called, but the messages not found will not be included in the messages list.
Messages might not be in the cache if the message is too old or the client is participating in high traffic guilds.

If this occurs, increase the max_messages parameter or use the on_raw_bulk_message_delete() event instead.

This requires Intents.messages to be enabled.

Parameters
----------
messages: List[Message]
    The messages that have been deleted.
"""

on_raw_message_edit: DiscordEvent[discord.RawMessageUpdateEvent] = DiscordEvent(
    "on_raw_message_edit"
)
"""Called when a message is edited. Unlike on_message_edit(), this is called regardless of the state of the internal message cache.

If the message is found in the message cache, it can be accessed via RawMessageUpdateEvent.cached_message.
The cached message represents the message before it has been edited.
For example, if the content of a message is modified and triggers the on_raw_message_edit() coroutine,
the RawMessageUpdateEvent.cached_message will return a Message object that represents the message before the content was modified.

Due to the inherently raw nature of this event, the data parameter coincides with the raw data given by the gateway.

Since the data payload can be partial, care must be taken when accessing items in the dictionary.
One example of a common case of partial data is when the 'content' key is inaccessible.
This denotes an 'embed' only edit, which is an edit in which only the embeds are updated by the Discord embed server.

This requires Intents.messages to be enabled.

Parameters
----------
payload: RawMessageUpdateEvent
    The raw event payload data.
"""

on_raw_message_delete: DiscordEvent[discord.RawMessageDeleteEvent] = DiscordEvent(
    "on_raw_message_delete"
)
"""Called when a message is deleted. Unlike on_message_delete(), this is called regardless of the message being in the internal message cache or not.

If the message is found in the message cache, it can be accessed via RawMessageDeleteEvent.cached_message.

This requires Intents.messages to be enabled.

Parameters
----------
payload: RawMessageDeleteEvent
    The raw event payload data.
"""

on_raw_bulk_message_delete: DiscordEvent[discord.RawBulkMessageDeleteEvent] = DiscordEvent(
    "on_raw_bulk_message_delete"
)
"""Called when a bulk delete is triggered. Unlike on_bulk_message_delete(), this is called regardless of the messages being in the internal message cache or not.

If the messages are found in the message cache, they can be accessed via RawBulkMessageDeleteEvent.cached_messages.

This requires Intents.messages to be enabled.

Parameters
----------
payload: RawBulkMessageDeleteEvent
    The raw event payload data.
"""

on_reaction_add: DiscordEvent[
    discord.Reaction, discord.Member | discord.User
] = DiscordEvent("on_reaction_add")
"""Called when a message has a reaction added to it. Similar to on_message_edit(), if the message is not found in the internal message cache,
then this event will not be called. Consider using on_raw_reaction_add() instead.

To get the Message being reacted, access it via Reaction.message.

This requires Intents.reactions to be enabled.

This doesn't require Intents.members within a guild context, but due to Discord not providing updated user information in a direct message,
it's required for direct messages to receive this event. Consider using on_raw_reaction_add() if you need this and do not otherwise want to enable the members intent.

Parameters
----------
reaction: Reaction
    The current state of the reaction.
user: Member | User
    The user who added the reaction.
"""

on_reaction_remove: DiscordEvent[
    discord.Reaction, discord.Member | discord.User
] = DiscordEvent("on_reaction_remove")
"""Called when a message has a reaction removed from it. Similar to on_message_edit,
if the message is not found in the internal message cache, then this event will not be called.

To get the message being reacted, access it via Reaction.message.

This requires both Intents.reactions and Intents.members to be enabled.

Consider using on_raw_reaction_remove() if you need this and do not want to enable the members intent.

Parameters
----------
reaction: Reaction
    The current state of the reaction.
user: Member | User
    The user whose reaction was removed.
"""

on_reaction_clear: DiscordEvent[discord.Message, List[discord.Reaction]] = DiscordEvent(
    "on_reaction_clear"
)
"""Called when a message has all its reactions removed from it.
Similar to on_message_edit(), if the message is not found in the internal message cache,then this event will not be called. Consider using on_raw_reaction_clear() instead.

This requires Intents.reactions to be enabled.

Parameters
----------
message: Message
    The message that had its reactions cleared.
reactions: List[Reaction]
    The reactions that were removed.
"""

on_reaction_clear_emoji: DiscordEvent[discord.Reaction] = DiscordEvent(
    "on_reaction_clear_emoji"
)
"""Called when a message has a specific reaction removed from it.
Similar to on_message_edit(), if the message is not found in the internal message cache,then this event will not be called. Consider using on_raw_reaction_clear_emoji() instead.

This requires Intents.reactions to be enabled.

New in version 1.3.

Parameters
----------
reaction: Reaction
    The reaction that got cleared.
"""

on_raw_reaction_add: DiscordEvent[discord.RawReactionActionEvent] = DiscordEvent(
    "on_raw_reaction_add"
)
"""Called when a message has a reaction added. Unlike on_reaction_add(), this is called regardless of the state of the internal message cache.

This requires Intents.reactions to be enabled.

Parameters
----------
payload: RawReactionActionEvent
    The raw event payload data.
"""

on_raw_reaction_remove: DiscordEvent[discord.RawReactionActionEvent] = DiscordEvent(
    "on_raw_reaction_remove"
)
"""Called when a message has a reaction removed. Unlike on_reaction_remove(), this is called regardless of the state of the internal message cache.

This requires Intents.reactions to be enabled.

Parameters
----------
payload: RawReactionActionEvent
    The raw event payload data.
"""

on_raw_reaction_clear: DiscordEvent[discord.RawReactionClearEvent] = DiscordEvent(
    "on_raw_reaction_clear"
)
"""Called when a message has all its reactions removed. Unlike on_reaction_clear(), this is called regardless of the state of the internal message cache.

This requires Intents.reactions to be enabled.

Parameters
----------
payload: RawReactionClearEvent
    The raw event payload data.
"""

on_raw_reaction_clear_emoji: DiscordEvent[
    discord.RawReactionClearEmojiEvent
] = DiscordEvent("on_raw_reaction_clear_emoji")
"""Called when a message has a specific reaction removed from it. Unlike on_reaction_clear_emoji(), this is called regardless of the state of the internal message cache.

This requires Intents.reactions to be enabled.

Parameters
----------
payload: RawReactionClearEmojiEvent
    The raw event payload data.
"""

on_guild_role_create: DiscordEvent[discord.Role] = DiscordEvent("on_guild_role_create")
"""Called when a Guild creates a new Role.

To get the guild it belongs to, use Role.guild.

This requires Intents.guilds to be enabled.

Parameters
----------
role: Role
    The role that was created.
"""

on_guild_role_delete: DiscordEvent[discord.Role] = DiscordEvent("on_guild_role_delete")
"""Called when a Guild deletes a Role.

To get the guild it belongs to, use Role.guild.

This requires Intents.guilds to be enabled.

Parameters
----------
role: Role
    The role that was deleted.
"""

on_guild_role_update: DiscordEvent[discord.Role, discord.Role] = DiscordEvent(
    "on_guild_role_update"
)
"""Called when a Role is changed guild-wide.

This requires Intents.guilds to be enabled.

Parameters
----------
before: Role
    The updated role's old info.
after: Role
    The updated role's updated info.
"""

on_scheduled_event_create: DiscordEvent[discord.ScheduledEvent] = DiscordEvent(
    "on_scheduled_event_create"
)
"""Called when a ScheduledEvent is created.

This requires Intents.guild_scheduled_events to be enabled.

Parameters
----------
event: ScheduledEvent
    The scheduled event that was created.
"""

on_scheduled_event_delete: DiscordEvent[discord.ScheduledEvent] = DiscordEvent(
    "on_scheduled_event_delete"
)
"""Called when a ScheduledEvent is deleted.

This requires Intents.guild_scheduled_events to be enabled.

Parameters
----------
event: ScheduledEvent
    The scheduled event that was deleted.
"""

on_scheduled_event_update: DiscordEvent[
    discord.ScheduledEvent, discord.ScheduledEvent
] = DiscordEvent("on_scheduled_event_update")
"""Called when a ScheduledEvent is updated.

This requires Intents.guild_scheduled_events to be enabled.

The following, but not limited to, examples illustrate when this event is called:
- The scheduled start/end times are changed.
- The channel is changed.
- The description is changed.
- The status is changed.
- The image is changed.

Parameters
----------
before: ScheduledEvent
    The scheduled event before the update.
after: ScheduledEvent
    The scheduled event after the update.
"""

on_scheduled_event_user_add: DiscordEvent[
    discord.ScheduledEvent, discord.User
] = DiscordEvent("on_scheduled_event_user_add")
"""Called when a user is added to a ScheduledEvent.

This requires Intents.guild_scheduled_events to be enabled.

Parameters
----------
event: ScheduledEvent
    The scheduled event that the user was added to.
user: User
    The user that was added.
"""

on_scheduled_event_user_remove: DiscordEvent[
    discord.ScheduledEvent, discord.User
] = DiscordEvent("on_scheduled_event_user_remove")
"""Called when a user is removed from a ScheduledEvent.

This requires Intents.guild_scheduled_events to be enabled.

Parameters
----------
event: ScheduledEvent
    The scheduled event that the user was removed from.
user: User
    The user that was removed.
"""

on_stage_instance_create: DiscordEvent[discord.StageInstance] = DiscordEvent(
    "on_stage_instance_create"
)
"""Called when a StageInstance is created for a StageChannel.

Parameters
----------
stage_instance: StageInstance
    The stage instance that was created.
"""

on_stage_instance_delete: DiscordEvent[discord.StageInstance] = DiscordEvent(
    "on_stage_instance_delete"
)
"""Called when a StageInstance is deleted for a StageChannel.

Parameters
----------
stage_instance: StageInstance
    The stage instance that was deleted.
"""

on_stage_instance_update: DiscordEvent[
    discord.StageInstance, discord.StageInstance
] = DiscordEvent("on_stage_instance_update")
"""Called when a StageInstance is updated.

The following, but not limited to, examples illustrate when this event is called:
- The topic is changed.
- The privacy level is changed.

Parameters
----------
before: StageInstance
    The stage instance before the update.
after: StageInstance
    The stage instance after the update.
"""

on_thread_create: DiscordEvent[discord.Thread] = DiscordEvent("on_thread_create")
"""Called whenever a thread is created.

Note that you can get the guild from Thread.guild.

This requires Intents.guilds to be enabled.

Parameters
----------
thread: Thread
    The thread that was created.
"""

on_thread_join: DiscordEvent[discord.Thread] = DiscordEvent("on_thread_join")
"""Called whenever a thread is joined.

Note that you can get the guild from Thread.guild.

This requires Intents.guilds to be enabled.

Parameters
----------
thread: Thread
    The thread that was joined.
"""

on_thread_update: DiscordEvent[discord.Thread, discord.Thread] = DiscordEvent(
    "on_thread_update"
)
"""Called whenever a thread is updated.

If the thread could not be found in the internal cache, this event will not be called.
Threads will not be in the cache if they are archived.
If you need this information, use on_raw_thread_update() instead.

This requires Intents.guilds to be enabled.

Parameters
----------
before: Thread
    The updated thread's old info.
after: Thread
    The updated thread's new info.
"""

on_thread_remove: DiscordEvent[discord.Thread] = DiscordEvent("on_thread_remove")
"""Called whenever a thread is removed. This is different from a thread being deleted.

Note that you can get the guild from Thread.guild.

This requires Intents.guilds to be enabled.

Due to technical limitations, this event might not be called as soon as one expects.
Since the library tracks thread membership locally, the API only sends updated thread membership status upon being synced by joining a thread.

Parameters
----------
thread: Thread
    The thread that was removed.
"""

on_thread_delete: DiscordEvent[discord.Thread] = DiscordEvent("on_thread_delete")
"""Called whenever a thread is deleted. If the thread could not be found in the internal cache, this event will not be called.
Threads will not be in the cache if they are archived.
If you need this information, use on_raw_thread_delete() instead.

Note that you can get the guild from Thread.guild.

This requires Intents.guilds to be enabled.

Parameters
----------
thread: Thread
    The thread that was deleted.
"""

on_raw_thread_update: DiscordEvent[discord.RawThreadUpdateEvent] = DiscordEvent(
    "on_raw_thread_update"
)
"""Called whenever a thread is updated. Unlike on_thread_update(), this is called regardless of the thread being in the internal thread cache or not.

This requires Intents.guilds to be enabled.

Parameters
----------
payload: RawThreadUpdateEvent
    The raw event payload data.
"""

on_raw_thread_delete: DiscordEvent[discord.RawThreadDeleteEvent] = DiscordEvent(
    "on_raw_thread_delete"
)
"""Called whenever a thread is deleted. Unlike on_thread_delete(), this is called regardless of the thread being in the internal thread cache or not.

This requires Intents.guilds to be enabled.

Parameters
----------
payload: RawThreadDeleteEvent
    The raw event payload data.
"""

on_thread_member_join: DiscordEvent[discord.ThreadMember] = DiscordEvent(
    "on_thread_member_join"
)
"""Called when a ThreadMember joins a Thread.

You can get the thread a member belongs to by accessing ThreadMember.thread.

This requires Intents.members to be enabled.

Parameters
----------
member: ThreadMember
    The member who joined.
"""

on_thread_member_remove: DiscordEvent[discord.ThreadMember] = DiscordEvent(
    "on_thread_member_remove"
)
"""Called when a ThreadMember leaves a Thread.

You can get the thread a member belongs to by accessing ThreadMember.thread.

This requires Intents.members to be enabled.

Parameters
----------
member: ThreadMember
    The member who left.
"""

on_raw_thread_member_remove: DiscordEvent[discord.RawThreadMembersUpdate] = DiscordEvent(
    "on_raw_thread_member_remove"
)
"""Called when a ThreadMember leaves a Thread. Unlike on_thread_member_remove(), this is called regardless of the member being in the internal thread's members cache or not.

This requires Intents.members to be enabled.

Parameters
----------
payload: RawThreadMembersUpdate
    The raw event payload data.
"""

on_voice_state_update: DiscordEvent[
    discord.Member, discord.VoiceState, discord.VoiceState
] = DiscordEvent("on_voice_state_update")
"""Called when a Member changes their VoiceState.

The following, but not limited to, examples illustrate when this event is called:

- A member joins a voice or stage channel.
- A member leaves a voice or stage channel.
- A member is muted or deafened by their own accord.
- A member is muted or deafened by a guild administrator.

This requires Intents.voice_states to be enabled.

Parameters
----------
member: Member
    The member whose voice states changed.
before: VoiceState
    The voice state prior to the changes.
after: VoiceState
    The voice state after the changes.
"""
