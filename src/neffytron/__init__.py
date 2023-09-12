# Import some classes and functions to the neffytron namespace
import neffytron.cog.settings
import neffytron.cog.lobby
import neffytron.utils
from neffytron.cog.lobby import Lobby
from neffytron.cog.settings.settings import Settings
from neffytron.utils import confirm

# This is in load order
cogs = [Settings, Lobby]

from neffytron.main import run
