import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from neffytron import cogs as cogs


def run():
    load_dotenv()
    if os_token := os.getenv("TOKEN"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        bot = commands.Bot(command_prefix="!", intents=intents)

        @bot.event
        async def on_ready() -> None:

            print(f"Logged in as {bot.user}\nSetting up cogs")
            for cog in cogs:
                await bot.add_cog(cog(bot))
            print("Set up cogs")

        bot.run(os_token)