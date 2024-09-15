import os
from typing import cast
from discord.ext.commands import Cog, Bot, CheckFailure
from discord.ext.commands.context import Context

from neffytron.cog.settings.node import Branch

# Complains about a circular import if I use neffytron.cogs.Settings
from .settings.settings import Settings


class BaseCog(Cog):

    name = None
    settings: Branch

    def __init__(self, bot):
        self.settings = cast(Settings, bot.get_cog("Settings")).get_settings(
            self.name, self.settings
        )

    async def cog_before_invoke(self, ctx: Context) -> None:
        self.settings._n_context.new(ctx)

    def cog_check(self, ctx: Context) -> bool:
        return (
            str(ctx.guild.id) != os.getenv("MAIN_SERVER") or os.getenv("ENV") != "dev"
        )

    async def cog_command_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, CheckFailure):
            return
        return await super().cog_command_error(ctx, error)
