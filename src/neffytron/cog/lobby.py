from typing import Callable, Iterator, Self
import urllib
import requests
import discord
import re
from discord.ext.commands import Cog, Bot, command, Context
from ..cog.baseCog import BaseCog
from ..cog.settings.nodes import Node, Val, Set, channel_interface, str_interface
import re
import urllib.parse

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

class Prev_Messages:
    class message(str_interface):
        pass
    class channel(channel_interface):
        pass

class Lobby(BaseCog):

    name = 'Lobby'

    class settings(Node):
        class i(str_interface):
            _default = 'Not set yet'
        class channel(channel_interface[Val]):
            _default = None
        list = Set(Prev_Messages)

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        super().__init__(bot)

    @Cog.listener("on_message")
    async def lobby_link(self, message: Message):
        match = re.search('\s(steam:\/\/[^\s]*)', message.content)
        if match:
            await message.channel.send('', view=SimpleView(match.group(0)))

    @command()
    async def test(self, ctx: Context, val: str):
        string = 'Last command was :"' + self.settings.i + '" in ' + (self.settings.channel.mention if self.settings.channel else 'None') + '\n'
        string += 'All previous commands:\n'
        for message in self.settings.list:
            string += message.message + ' in ' + message.channel.mention + '\n'
        await ctx.send(string)
        self.settings.i = val
        self.settings.channel = ctx.channel
        self.settings.list.add({'message': val, 'channel': ctx.channel})
