import urllib
import requests
import discord
import re
from discord.ext.commands import Cog, Bot, command
from neffytron.cog.baseCog import BaseCog
# Damn it this is exactly what I wanted to avoid with this, why can't you sort everything out and let me import neffytron.nodes
from neffytron.cog.settings.nodes import DB_Channel, Node, DB_Value
import re
import urllib.parse
from asyncio import Future
from typing import Iterator

import discord
import requests
from discord.ext.commands import Cog
from discord.ext.commands.bot import Bot
from discord.message import Message


def shorten(url_long: str) -> str:
    url = "http://tinyurl.com/api-create.php?" + urllib.parse.urlencode(
        {"url": url_long}
    )
    res = requests.get(url)
    return res.text


class SimpleView(discord.ui.View):
    def __init__(self, link: str) -> None:
        super().__init__()
        button = discord.ui.Button(
            label="Working lobby link because discord sucks",
            style=discord.ButtonStyle.url,
            url=shorten(link),
        )
        self.add_item(button)

class Lobby(BaseCog):

    name = 'Lobby'

    class settings(Node):
        class i(DB_Value):
            _default = 'Not set yet'
        class channel(DB_Value[DB_Channel]):
            _default = None

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        super().__init__(bot)

    @Cog.listener("on_message")
    async def lobby_link(self, message: Message):
        match = re.search('\s(steam:\/\/[^\s]*)', message.content)
        if match:
            await message.channel.send('', view=SimpleView(match.group(0)))

    @command()
    async def test(self, ctx, val: str):
        await ctx.send('Last command was :"' + self.settings.i + '" in ' + (self.settings.channel.mention if self.settings.channel else 'None'))
        self.settings.i = val
        self.settings.channel = ctx.channel
