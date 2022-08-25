import discord
from discord.utils import get


def get_first_match(x, y):
    return bool(set(x).intersection(set(y)))


async def get_action_object(objects: list, scope: str, guild, bot=None) -> list:
    if scope in {'member', 'mute', 'unmute', 'ban', 'kick', 'deafen', 'undeafen'}:
        return list(map(lambda x: get(guild.members, id=int(x)), objects))
    elif scope in {'add_role', 'remove_role'}:
        return [[get(guild.roles, id=int(x)) for x in objects[0].split()], list(
            map(lambda x: get(guild.members, id=int(x)), objects[1]))]
    elif scope in {'move'}:
        return [get(guild.voice_channels, id=int(objects[1][0])) or get(guild.stage_channels, id=int(objects[1][0])),
                [get(guild.members, id=int(x)) for x in objects[0].split()]]
    elif scope in {'button_move'}:
        return [get(guild.voice_channels, id=int(objects[1][0])) or get(guild.stage_channels, id=int(objects[1][0])),
                [get(guild.members, id=int(x)) for x in objects[0]]]
    elif scope in {'members_with_role'}:
        roles = list(map(lambda x: get(guild.roles, id=int(x)), objects))
        return list(filter(lambda x: get_first_match(roles, x.roles), guild.members))
    elif scope in {'unban'}:
        return list(map(lambda x: bot.get_user(int(x)), objects))
