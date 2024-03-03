from __future__ import annotations
import asyncio
import json
from typing import Optional, cast, TypeVar
from pymongo import MongoClient
from pymongo.database import Database
from discord.ext import commands
import discord
import os

from .nodes import Context, ModuleSettings, Node


class Settings(commands.Cog):
    def __init__(self, bot):
        # Is there a value to pass to get a function to use its default value? I'm pretty sure if I did
        # MongoClient(os.getenv('MONGOURI') or None) or whatever, it'd actually use the None and fail
        # Not worth the effort to actually test it though :jamroll:, just enough to write this comment
        client = MongoClient(os.getenv('MONGOURI')) if os.getenv(
            'MONGOURI') != '' else MongoClient()
        self.bot = bot
        self._db = client.neffytron

        class Schema(Node):
            _description = 'View & change data for the various modules of Neffytron'
            pass
        self._schema = Schema

    # Python's type hinting is a dumpster fire so I don't know how to type hint what schema should be, but basically:
    #
    # class Schema:
    #   class x:
    #       i = Something in nodes.py
    #   class y:
    #       class z:
    #           j = Something in nodes.py
    #           k = Something in nodes.py
    #
    # I really wanted to get this to be JSON but type hinting hated it, it needs to be static

    T = TypeVar('T')

    def get_settings(self, name, schema: T) -> T:
        setattr(self._schema, name, schema)
        # For Context.Discord gets set at BaseCog.cog_before_invoke
        return cast(schema, ModuleSettings(self._schema, Context(None, self._db), None))

    @commands.group(invoke_without_command=True)
    async def n_s(self, ctx):
        # TODO: Add some way of exploring the db here
        # In progress :confetti_ball:
        setting = ModuleSettings(self._schema, Context(ctx, self._db), None)
        await ctx.send(**setting._message(setting))
