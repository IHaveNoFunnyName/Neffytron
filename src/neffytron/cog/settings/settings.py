from __future__ import annotations
import asyncio
import json
from typing import Optional, cast, TypeVar
from pymongo import MongoClient
from pymongo.database import Database
from discord.ext import commands
import discord
import os

from neffytron.cog.settings.context import N_Context

from .node import Branch


class Settings(commands.Cog):

    schema: Branch

    def __init__(self, bot):
        # Is there a value to pass to get a function to use its default value? I'm pretty sure if I did
        # MongoClient(os.getenv('MONGOURI') or None) or whatever, it'd actually use the None and fail
        # Not worth the effort to actually test it though :jamroll:, just enough to write this comment
        client = (
            MongoClient(os.getenv("MONGOURI"))
            if os.getenv("MONGOURI") != ""
            else MongoClient()
        )
        self.schema = Branch(N_Context([], client.neffytron), False)

    # class Branch:
    #   class x:
    #       class i(Value, Interface, DataSource): ...
    #   class y:
    #       class z(Array, DataSource):
    #           class j(Interface): ...
    #           class k(Interface): ...

    T = TypeVar("T")

    def get_settings(self, name, schema: T) -> T:
        setattr(self.schema, name, schema)
        return getattr(self.schema, name)

    @commands.group(invoke_without_command=True)
    async def n_s(self, ctx):
        self.schema._n_context.new(ctx)
        # TODO: Add some way of exploring the db here
        # In progress :confetti_ball:
        await ctx.send(**self.schema._n_admin_message())
