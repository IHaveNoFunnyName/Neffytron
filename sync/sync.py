
from discord.ext import commands
class Sync(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sync(self, ctx, spec = None) -> None:
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")