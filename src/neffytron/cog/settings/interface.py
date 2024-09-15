from typing import TypeVar, Protocol, List
from discord import TextChannel, Member, Interaction
from discord.ui import UserSelect, ChannelSelect

from neffytron.cog.settings.context import N_Context
from neffytron.cog.settings.protocols import Interface

# Inherit from the result type to get type hinting


class Interface_str(Interface, str):
    def _i_set(self, x: str, context: N_Context) -> str:
        return x

    def _i_get(self, x: str, context: N_Context) -> str:
        return x


# class Interface_channel(Interface, TextChannel):
#     _display_name = "Channel"
#     _select_placeholder = "Select a channel"

#     def _i_set(self, x: TextChannel, context: N_Context) -> str:
#         return str(x.id)

#     def _i_get(self, x: str, context: N_Context) -> TextChannel:
#         return context.discord.guild.get_channel(int(x))

#     def list(self, context: N_Context) -> List[TextChannel]:
#         return context.discord.guild.text_channels

#     def display_value(self, x: TextChannel, context: N_Context) -> str:
#         return x.name

#     def select(self, context: N_Context, name: str, state: dict, any: bool = False):
#         class Dropdown(ChannelSelect):
#             def __init__(self):
#                 super().__init__(
#                     placeholder=self._display_name
#                     + ": "
#                     + self._select_placeholder
#                     + (" (leave empty for any)" if any else ""),
#                     min_values=0,
#                 )

#             async def callback(self, interaction: Interaction):
#                 state[name] = self.values[0] if len(self.values) else "any"
#                 await interaction.response.defer()

#         return Dropdown()


# class member_interface(Interface, Member):
#     _display_name = "Member"
#     _select_placeholder = "Select a member"

#     def _i_set(self, x: Member, context: N_Context) -> str:
#         return str(x.id)

#     def _i_get(self, x: str, context: N_Context) -> Member:
#         return context.discord.guild.get_member(int(x))

#     def list(self, context: N_Context) -> List[Member]:
#         return context.discord.guild.members

#     def display_name(self, x: Member, context: N_Context) -> str:
#         return x.display_name

#     def select(self, context: N_Context, name: str, state: dict, any: bool = False):
#         class Dropdown(UserSelect):
#             def __init__(self):
#                 super().__init__(
#                     placeholder=self._display_name
#                     + ": "
#                     + self._select_placeholder
#                     + (" (leave empty for any)" if any else ""),
#                     min_values=0,
#                 )

#             async def callback(self, interaction: Interaction):
#                 state[name] = self.values[0] if len(self.values) else "any"
#                 await interaction.response.defer()

#         return Dropdown()
