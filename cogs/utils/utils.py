import discord
from discord import app_commands
from discord.ext.commands import Cog
import dateparser

class Utils(Cog):
    def __init__(self, bot):
        self._bot = bot

    @app_commands.command(name="time", description="Natural language to discord's timestamp format that they haven't made user friendly in years")
    @app_commands.describe(time="Time in Natural language", format="(Optional) Format")
    @app_commands.choices(format=[
        app_commands.Choice(name="12:34", value="t"),
        app_commands.Choice(name="12:34:56", value="T"),
        app_commands.Choice(name="1/2/26", value="d"),
        app_commands.Choice(name="1 Feb 2026", value="D"),
        app_commands.Choice(name="1 Feb 2026 at 12:34", value="f"),
        app_commands.Choice(name="Sunday, 1 Feb 2026 at 12:34", value="F"),
        app_commands.Choice(name="in 5 minutes", value="R"),
    ])
    @app_commands.allowed_installs(guilds=False, users=True)
    async def time_command(self, interaction: discord.Interaction, time: str, format: app_commands.Choice[str]=None):
        parsed_time = dateparser.parse(time)
        if not parsed_time:
            await interaction.response.send_message("Sorry, I couldn't understand that time.", ephemeral=True)
            return
        timestamp = int(parsed_time.timestamp())

        if format is None:
            format = app_commands.Choice(name="Relative Time", value="R")

        await interaction.response.send_message("<t:{0}:{1}>\n`<t:{0}:{1}>`".format(timestamp, format.value), ephemeral=True)