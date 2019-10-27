"""
The MIT License (MIT)

Copyright (c) 2017-2018 Nariman Safiulin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import discord
import discord.utils

import hugo
from hugo.command import (
    Template,
    Group,
    command,
    group
)
from hugo import exceptions

# token = os.environ.get("DISCORD_BOT_TOKEN")

# fmt: off

def _build_connect_event():
    return stats.Connect()


def _build_message_event_stats():
    return chain_of([
        stats.Message(),
        Command("status"),
        BotFilter(authored_by_bot=False)
    ])


def _build_message_event_audio():
    return chain_of([
        collection_of(OneOfAll, [
            chain_of([
                audio.Join(),
                collection_of(OneOfAll, [Command("join"), Command("connect")])
            ]),
            chain_of([
                audio.Leave(),
                collection_of(OneOfAll, [
                    Command("leave"),
                    Command("disconnect")
                ])
            ]),
            chain_of([
                audio.Play(),
                Command(
                    "play",
                    rest_pattern="(?P<url>.+)"
                )
            ]),
            chain_of([audio.Pause(), Command("pause")]),
            chain_of([audio.Resume(), Command("resume")]),
            chain_of([audio.Stop(), Command("stop")]),
            chain_of([audio.Skip(), Command("skip")]),
            chain_of([
                audio.Volume(),
                Command(
                    "volume",
                    rest_pattern="(?P<volume>.+)"
                )
            ])
        ]),
        MiddlewareState(audio.State()),
        ChannelTypeFilter(guild=True),
        BotFilter(authored_by_bot=False)
    ])


def _build_message_event():
    return collection_of(OneOfAll, [
        _build_message_event_stats(),
        _build_message_event_audio()
    ])


def _build_root():
    return chain_of([
        collection_of(OneOfAll, [
            chain_of([
                _build_connect_event(),
                EventTypeFilter(EventType.CONNECT)
            ]),
            chain_of([
                _build_message_event(),
                Command(r"\$", prefix=True),
                EventTypeFilter(EventType.MESSAGE)
            ]),
        ]),
        MiddlewareState(stats.State()),
        EventNormalization()
    ])

# fmt: on



class Roles(Group):
    def __init__(self):
        super().__init__("Roles", "Roles management")
        self.assign_map = {}

    def get_role_assign_map(self, role):
        if role.id not in self.assign_map:
            self.assign_map[role.id] = []
        return self.assign_map[role.id]

    @command(slug="allow_role_assign_role",
             templates=[
                 Template(r"allow_role_assign_role <@&(?P<member_role_id>[0-9]+)> <@&(?P<assign_role_id>[0-9]+)>", allow_short_mention=True),
             ],
             short_description="Allow members with role assign specific role to other members",
             long_description="",
             private_messages=False,
             server_messages=True)
    async def allow_role_assign_role(self, ctx, member_role_id, assign_role_id):
        author = ctx.author
        member_role = discord.utils.find(lambda r: r.id == member_role_id, ctx.server.roles)
        assign_role = discord.utils.find(lambda r: r.id == assign_role_id, ctx.server.roles)

        if (not author.server == member_role.server == assign_role.server or
            not author.server_permissions.administrator):
            raise exceptions.CommandProcessError(
                "You do not have permissions to allow role assigning")

        assign_role_map = self.get_role_assign_map(assign_role)
        if member_role in assign_role_map:
            await ctx.send_message("This rule is added yet")
            return

        assign_role_map.append(member_role)
        await ctx.send_message("Rule added")

    @command(slug="allow_member_assign_role",
             templates=[
                 Template(r"allow_member_assign_role <@!?(?P<member_id>[0-9]+)> <@&(?P<assign_role_id>[0-9]+)>", allow_short_mention=True),
             ],
             short_description="Allow members with role assign specific role to other members",
             long_description="",
             private_messages=False,
             server_messages=True)
    async def allow_member_assign_role(self, ctx, member_id, assign_role_id):
        author = ctx.author
        member = ctx.server.get_member(member_id)
        assign_role = discord.utils.find(lambda r: r.id == assign_role_id, ctx.server.roles)

        if (not author.server == member.server == assign_role.server or
            not author.server_permissions.administrator):
            raise exceptions.CommandProcessError(
                "You do not have permissions to allow role assigning")

        assign_role_map = self.get_role_assign_map(assign_role)
        if member in assign_role_map:
            await ctx.send_message("This rule is added yet")
            return

        assign_role_map.append(member)
        await ctx.send_message("Rule added")

    @command(slug="assign_role",
             templates=[
                 Template(r"assign_role <@!?(?P<member_id>[0-9]+)> <@&(?P<role_id>[0-9]+)>", allow_short_mention=True),
             ],
             short_description="Assign role to member",
             long_description="",
             private_messages=False,
             server_messages=True)
    async def assign_role(self, ctx, member_id, role_id):
        author = ctx.author
        member = ctx.server.get_member(member_id)
        role = discord.utils.find(lambda r: r.id == role_id, ctx.server.roles)

        if not author.server == member.server == role.server:
            raise exceptions.CommandProcessError(
                "You do not have permissions to role assigning")

        role_map = self.get_role_assign_map(role)
        if (author in role_map or
            any((True for author_role in author.roles if author_role in role_map))):
            try:
                await ctx.bot.add_roles(member, role)
            except discord.Forbidden:
                raise exceptions.CommandProcessError(
                    "Sorry, but I can't assign this role")
            await ctx.send_message("Role assigned")
        else:
            raise exceptions.CommandProcessError(
                "You do not have permission to assign this role")
