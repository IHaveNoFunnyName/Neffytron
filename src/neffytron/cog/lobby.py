import urllib
import requests
import discord
import re
from discord.ext.commands import Cog, Bot, command, Context
from ..cog.baseCog import BaseCog
from ..cog.settings.nodes import Node, Val, Binary_Relation, channel_interface, member_interface, str_interface
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


class auto_pin:
    class channel(channel_interface):
        pass

    class member(member_interface):
        pass


class Lobby(BaseCog):

    name = 'Lobby'

    class settings(Node):
        _short_desc = 'Controls auto pinning lobby links'

        auto_pin = Binary_Relation(auto_pin)

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        super().__init__(bot)

    @Cog.listener("on_message")
    async def lobby_link(self, message: Message):
        match = re.search('\s(steam:\/\/[^\s]*)', message.content)
        if match:
            await message.channel.send('', view=SimpleView(match.group(0)))
