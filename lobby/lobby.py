from discord import app_commands
from discord.ext.commands import Cog
import discord
import re

class SimpleView(discord.ui.View):
    def __init__(self, link, label):
        super().__init__()
        button = discord.ui.Button(label=label, style=discord.ButtonStyle.url, url=link.replace("steam://joinlobby/", "https://neffytron.com/lobby/"))
        self.add_item(button)

class PinView(discord.ui.View):
    def __init__(self, callback):
        super().__init__()
        button = discord.ui.Button(label="pin", style=discord.ButtonStyle.success)
        button.callback = callback
        self.add_item(button)

pinners = set((202732983910793217, 191186486886924291, 96184605073235968, 186142996574633985, 96564257583304704 )) # hard code for now

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

    @app_commands.command(name="lobby")
    async def lobby_command(self, interaction: discord.Interaction, link: str, label: str=None):
        match = re.search('(steam:\/\/joinlobby\/[^\s]*)', link)

        if not match:
            await interaction.response.send_message('Invalid lobby link.', ephemeral=True)
            return

        response = await interaction.response.send_message('', view = SimpleView(match.group(0), label or f"{interaction.user.display_name}'s Lobby"))
        if interaction.user.id in pinners:
            async def pin_callback(interaction: discord.Interaction):
                for p in await interaction.channel.pins():
                    if p.content == '' or p.content.startswith("steam://joinlobby/"):
                        await p.unpin()
                await response.resource.pin()
                return await interaction.response.edit_message(content="pinned", view=None)
            await interaction.followup.send("you're a TO wanna pin it?", ephemeral=True, view = PinView(pin_callback))
            return

        
                
