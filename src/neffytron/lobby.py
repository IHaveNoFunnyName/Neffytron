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


class Lobby(Cog):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    @Cog.listener("on_message")
    async def lobby_link(self, message: Message):
        match = re.search(r"(steam:\/\/[^\s]*)", message.content)
        if match:
            await message.channel.send("", view=SimpleView(match.group(0)))
