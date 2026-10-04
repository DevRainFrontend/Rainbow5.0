import discord


def can_moderate(author: discord.Member, target: discord.Member) -> bool:
    if author.id == author.guild.owner_id:
        return True
    if target.id == author.guild.owner_id:
        return False
    if target.id == author.id:
        return False
    return target.top_role < author.top_role


def bot_can_act(guild: discord.Guild, target: discord.Member) -> bool:
    me = guild.me
    if not me:
        return False
    return target.top_role < me.top_role


def can_manage_role(author: discord.Member, role: discord.Role) -> bool:
    if author.id == author.guild.owner_id:
        return True
    return role < author.top_role
