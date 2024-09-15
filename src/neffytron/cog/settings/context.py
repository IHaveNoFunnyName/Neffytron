from typing import List
from discord.ext.commands import Context as DiscordContext
from pymongo.database import Database

# Everything needed to create a setting, both static and dynamic.
# Add additions both here, and where relevant in file://../baseCog.py and file://./settings.py

# It should be a dataclass, i just don't know if they can have functions and i'm not going to look it up


class N_Context:
    path: List[str]
    discord: DiscordContext
    db: Database

    # Static (the dynamic ones will be None to start but will always be set before use)
    def __init__(self, path: List[str], db: Database, discord: DiscordContext = None):
        self.path = path
        self.db = db
        self.discord = discord

    # Dynamic / New class per invocation
    def new(self, discord: DiscordContext):
        return N_Context(self.path, self.db, discord)

    def add_path(self, path: str):
        return N_Context(self.path + [path], self.db, self.discord)
