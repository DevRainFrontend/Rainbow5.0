import discord

BRAND_COLOR = discord.Color.from_rgb(88, 101, 242)
ERROR_COLOR = discord.Color.from_rgb(237, 66, 69)
SUCCESS_COLOR = discord.Color.from_rgb(87, 242, 135)
WARN_COLOR = discord.Color.from_rgb(254, 231, 92)

FOOTER = "Rainbow 5.0"


def base_embed(
    title: str,
    description: str = "",
    *,
    color: discord.Color = BRAND_COLOR,
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER)
    return embed


def success(title: str, description: str) -> discord.Embed:
    return base_embed(title, description, color=SUCCESS_COLOR)


def error(title: str, description: str) -> discord.Embed:
    return base_embed(title, description, color=ERROR_COLOR)


def warn(title: str, description: str) -> discord.Embed:
    return base_embed(title, description, color=WARN_COLOR)
