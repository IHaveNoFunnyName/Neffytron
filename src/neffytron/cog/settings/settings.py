from __future__ import annotations
import asyncio
import json
from typing import Optional, cast, TypeVar
from pymongo import MongoClient
from pymongo.database import Database
from discord.ext import commands
import discord
import os

from .nodes import DB_Node, view_builder, Node


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
        return cast(schema, ModuleSettings(self._schema, self._db))

    @commands.group(invoke_without_command=True)
    async def n_s(self, ctx):
        # TODO: Add some way of exploring the db here
        # In progress :confetti_ball:
        view = view_builder(self._schema)
        await ctx.send(view.content, view=view)


class ModuleSettings():
    def __init__(self, schema: Node, db: Database, path: Optional[str] = ''):
        self.db = db
        self.schema = schema
        self.path = path

    def __getattr__(self, key):
        if hasattr(self.schema, key):
            attr = getattr(self.schema, key)
            # Add ifs here for other data stores/node types
            if (issubclass(attr, DB_Node)):
                return attr(self.db, self.path, key).__get__(self, self)
            return ModuleSettings(attr, self.db, self.path + key)
