import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

# Do I have to do this? Is there a way to like have python default import a .py? maybe that's what __init__.py is for?
# I don't understand how this wasn't immediately answered via google.
from settings.settings import Settings
from lobby.lobby import Lobby

def run(token):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}\nSetting up cogs")
        await bot.add_cog(Settings(bot))
        await bot.add_cog(Lobby(bot))
        print('Set up cogs')
    bot.run(token)

if __name__ == "__main__":
    load_dotenv()
    run(os.getenv('TOKEN'))