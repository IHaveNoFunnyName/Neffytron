import asyncio


async def confirm(message, success, fail, ctx):
    msg = await message()
    await msg.add_reaction("<:GreenTick:751664729449300081>")
    await msg.add_reaction("<:RedCross:751664777821945966>")

    def check(reaction, user):
        return (
            user == ctx.author
            and str(reaction.emoji)
            in ["<:GreenTick:751664729449300081>", "<:RedCross:751664777821945966>"]
            and reaction.message == msg
        )

    try:
        reaction, user = await ctx.bot.wait_for(
            "reaction_add", timeout=60.0, check=check
        )
    except asyncio.TimeoutError:
        await fail()
    else:
        if str(reaction.emoji) == "<:GreenTick:751664729449300081>":
            await success(msg)
        else:
            await fail(msg)
    await msg.clear_reactions()
