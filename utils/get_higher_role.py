from functools import reduce

import discord


def get_higher_role(member: discord.Member) -> discord.Role:
    return max(member.roles)
