import urllib
import requests
import discord
import re
from discord.ext.commands import Cog, Bot, command, Context

from neffytron.cog.settings.datasource import DS_mongo, DS_wau
from neffytron.cog.settings.interface import Interface_str
from neffytron.cog.settings.node import Value
from ..cog.baseCog import BaseCog
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


class Lobby(BaseCog):

    name = "Lobby"

    class settings:
        class i(Value, Interface_str, DS_mongo): ...

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        super().__init__(bot)

    @Cog.listener("on_message")
    async def lobby_link(self, message: Message):
        match = re.search("\s(steam:\/\/[^\s]*)", message.content)
        if match:
            await message.channel.send("", view=SimpleView(match.group(0)))

    @command()
    async def test(self, ctx: Context):
        self.settings.i = "wau"
        await ctx.send(self.settings.i.capitalize())
