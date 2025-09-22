from discord.ext.commands import Cog
import discord
import re

class SimpleView(discord.ui.View):
    def __init__(self, link, label):
        super().__init__()
        button = discord.ui.Button(label=label, style=discord.ButtonStyle.url, url=link.replace("steam://joinlobby/", "https://neffytron.com/lobby/"))
        self.add_item(button)

class Lobby(Cog):
    def __init__(self, bot):
        self._bot = bot

    @Cog.listener("on_message")
    async def lobby_link(self, message: discord.Message):
        match = re.search('(steam:\/\/joinlobby\/[^\s]*)', message.content)
        if match:
            if re.search('stream', message.content, re.IGNORECASE):
                label = 'Stream Lobby'
            elif message.author.bot:
                name_match = re.search("Join (.+?)'s", message.content, re.IGNORECASE)
                if name_match:
                    label = f"{name_match.group(1)}'s Lobby"
            else:
                label = f"{message.author.display_name}'s Lobby"

            await message.channel.send('', view=SimpleView(match.group(0), label))
