import os
from typing import Any, Optional

import discord
import neffytron
from discord.abc import Messageable
from discord.ext import commands
from discord.ext.commands.bot import Bot
from pymongo import MongoClient
from pymongo.database import Database


# Type hinting is getting completely lost, presumably because it goes through get_cog and turned into Any
# Any way to fix this? Not familiar with python/pylance typing.


class Settings(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        # Is there a value to pass to get a function to use its default value? I'm pretty sure if I did
        # MongoClient(os.getenv('MONGOURI') or None) or whatever, it'd actually use the None and fail
        # Not worth the effort to actually test it though :jamroll:, just enough to write this comment
        client: MongoClient[Any] = (
            MongoClient(os.getenv("MONGOURI"))
            if os.getenv("MONGOURI") != ""
            else MongoClient()
        )
        self._bot = bot
        self._db = client.neffytron
        self._settings = self.get_settings("settings")

    def get_settings(self, name: str) -> "ModuleSettings":
        return ModuleSettings(name, self._db)

    @commands.group(invoke_without_command=True)
    async def neffytron_settings(self, ctx: Messageable):
        # TODO: Add some way of exploring the db here/in subcommands
        await ctx.send("Settings!")

    @neffytron_settings.command()
    async def add_admin(self, ctx: commands.Context[Any], displayName: str):
        if self._settings.is_admin(ctx):
            query = await ctx.guild.query_members(displayName) if ctx.guild else []
            if len(query):

                async def message() -> discord.Message:
                    return await ctx.send(
                        f"Add admin: {query[0].mention}?",
                        allowed_mentions=discord.AllowedMentions.none(),
                    )

                async def success(msg: discord.Message):
                    if ctx.guild is not None:
                        self._db[str(ctx.guild.id)].settings.admins.find_one_and_update(
                            {"id": query[0].id},
                            {
                                "$set": {
                                    "id": query[0].id,
                                    "display_name": query[0].display_name,
                                }
                            },
                            upsert=True,
                        )
                        await msg.edit(
                            content=f"Added admin {query[0].mention}.",
                            allowed_mentions=discord.AllowedMentions.none(),
                        )

                async def fail(msg: discord.Message):
                    await msg.edit(content="Cancelled")

                await neffytron.confirm(message, success, fail, ctx)
            else:
                await ctx.send(f'Could not find member: "{displayName}"')

    @neffytron_settings.command()
    async def admin_role(self, ctx: commands.Context[Any], role):
        if self._settings.is_admin(ctx):
            if (
                ctx.guild is not None
                and (fetched_role := discord.utils.get(ctx.guild.roles, name=role))
                is not None
            ):
                current_str = ""
                if (
                    current_id := self._settings.get_setting(ctx.guild, "admin_role")
                    is not None
                ):
                    current_role = ctx.guild.get_role(current_id)
                    current_str = (
                        f"\nThe current role is {current_role.mention}"
                        if current_role is not None
                        else ""
                    )

                async def message() -> discord.Message:
                    return await ctx.send(
                        f"Switch admin role to: {fetched_role.mention}?{current_str}",
                        allowed_mentions=discord.AllowedMentions.none(),
                    )

                async def success(msg: discord.Message):
                    self._settings.set_setting(ctx.guild, "admin_role", fetched_role.id)
                    await msg.edit(
                        content=f"Set admin role to: {fetched_role.mention}.",
                        allowed_mentions=discord.AllowedMentions.none(),
                    )

                async def fail(msg: discord.Message):
                    await msg.edit(content="Cancelled")

                await neffytron.confirm(message, success, fail, ctx)
            else:
                await ctx.send(f'Could not find role: "{role}"')

    @neffytron_settings.command()
    async def is_admin(self, ctx: commands.Context, displayName):
        query = await ctx.guild.query_members(displayName) if ctx.guild else []
        if len(query):
            await ctx.send(
                f'{query[0].mention} is {"" if self._settings.is_admin(guild=ctx.guild, member=query[0]) else "not "}an admin.',
                allowed_mentions=discord.AllowedMentions.none(),
            )


class ModuleSettings:
    def __init__(self, name: str, db: Database) -> None:
        self.db = db
        self.name = name

    def get_setting(self, server, key):
        entry = self.db[str(server.id)][self.name].settings.find_one({"key": key})
        return entry["value"] if entry is not None else None

    def set_setting(self, server, key, value):
        self.db[str(server.id)][self.name].settings.find_one_and_replace(
            {"key": key}, {"key": key, "value": value}, upsert=True
        )

    def find_one(self, server: discord.Guild, path, filter):
        return self.db[str(server.id)][self.name][path].find_one(filter)

    def set_one(self, server, path, filter, value):
        self.db[str(server.id)][self.name][path].find_one_and_replace(
            filter, value, upsert=True
        )

    def is_admin(
        self,
        ctx: Optional[commands.Context] = None,
        guild: Optional[discord.Guild] = None,
        member: Optional[discord.Member] = None,
    ):
        if ctx:
            server = ctx.guild
            author = ctx.author
        else:
            server = guild
            author = member

        if (
            server is not None
            and isinstance(author, discord.Member)
            and server.owner is not None
        ):
            if (role := self.get_setting(server, "admin_role")) is not None:
                role = server.get_role(role)
            admins_collection = self.db[str(server.id)].settings.admins
            if admins_collection is not None:
                return (
                    (role and role in author.roles)
                    or admins_collection.find_one({"id": author.id}) is not None
                    or author.id == server.owner.id
                )
            else:
                return False
        else:
            return False
