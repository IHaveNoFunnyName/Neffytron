from typing import cast
from discord.ext.commands import Cog, Bot
# Complains about a circular import if I use neffytron.cogs.Settings
from .settings.settings import Settings


class BaseCog(Cog):

    name = None
    schema = None

    def __init__(self, bot):
        self.settings = cast(Settings, bot.get_cog(
            'Settings')).get_settings(self.name, self.schema).__getattr__(self.name)
