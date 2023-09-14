from typing import cast
from discord.ext.commands import Cog, Bot
from discord.ext.commands.context import Context
# Complains about a circular import if I use neffytron.cogs.Settings
from .settings.settings import Settings, Node


class BaseCog(Cog):

    name = None
    settings: Node

    def __init__(self, bot):
        self.settings = cast(Settings, bot.get_cog(
            'Settings')).get_settings(self.name, self.settings).__getattr__(self.name)

    async def cog_before_invoke(self, ctx: Context) -> None:
        self.settings._context.discord = ctx
