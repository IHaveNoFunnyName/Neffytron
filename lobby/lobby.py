import urllib
import requests
from discord.ext.commands import Cog
import discord
import re

class SimpleView(discord.ui.View):
    def __init__(self, link):
        super().__init__()
        button = discord.ui.Button(label='Working lobby link because discord sucks', style=discord.ButtonStyle.url, url=link.replace("steam://joinlobby/", "https://neffytron.com/lobby/"))
        self.add_item(button)

class Lobby(Cog):
    def __init__(self, bot):
        self._bot = bot

    @Cog.listener("on_message")
    async def lobby_link(self, message):
        match = re.search('(steam:\/\/joinlobby\/[^\s]*)', message.content)
        if match:
            await message.channel.send('', view=SimpleView(match.group(0)))
    