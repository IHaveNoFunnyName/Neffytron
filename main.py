import os
import urllib
import requests
from dotenv import load_dotenv

import discord
from discord.ext import commands

# Do I have to do this? Is there a way to like have python default import a .py? maybe that's what __init__.py is for?
# I don't understand how this wasn't immediately answered via google.
from settings.settings import Settings

def run(token):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}\nSetting up cogs")
        await bot.add_cog(Settings(bot))
        print('Set up cogs')

    def shorten(url_long):
            url = 'http://tinyurl.com/api-create.php?' + urllib.parse.urlencode({"url": url_long})
            res = requests.get(url)
            return res.text

    @bot.command()
    async def test(ctx):
        class SimpleView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)  # times out after 30 seconds
                button = discord.ui.Button(label='Join Lobby', style=discord.ButtonStyle.url, url=shorten('steam://joinlobby/245170/109775244914157053/76561198046191506'))
                self.add_item(button)
        await ctx.send('Working lobby link because discord sucks', view=SimpleView())

    bot.run(token)

if __name__ == "__main__":
    load_dotenv()
    run(os.getenv('TOKEN'))