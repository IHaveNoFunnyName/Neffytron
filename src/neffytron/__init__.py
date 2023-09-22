# Import some classes and functions to the neffytron namespace
from .cog.lobby import Lobby
from .cog.settings.settings import Settings
from .utils import confirm

# This is in load order
cogs = [Settings, Lobby]

from .main import run
