import re
from datetime import timedelta

import discord


def parse_duration(text: str) -> timedelta | None:
    match = re.fullmatch(r"(\d+)([smhd])", text.lower())
    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    if unit == "s":
        return timedelta(seconds=amount)
    if unit == "m":
        return timedelta(minutes=amount)
    if unit == "h":
        return timedelta(hours=amount)
    if unit == "d":
        return timedelta(days=amount)
    return None


async def resolve_member(
    ctx,
    arg: str,
) -> discord.Member | None:
    if not arg:
        return None

    try:
        user_id = int(arg.strip("<@!>"))
        return ctx.guild.get_member(user_id) or await ctx.guild.fetch_member(user_id)
    except ValueError:
        pass

    return discord.utils.get(ctx.guild.members, name=arg)


async def resolve_role(ctx, arg: str) -> discord.Role | None:
    if not arg:
        return None

    if arg.startswith("<@&") and arg.endswith(">"):
        try:
            role_id = int(arg.strip("<@&>"))
            return ctx.guild.get_role(role_id)
        except ValueError:
            return None

    return discord.utils.get(ctx.guild.roles, name=arg)
