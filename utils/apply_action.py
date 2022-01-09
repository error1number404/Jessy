from typing import Union

import discord


async def apply_action(action: Union[str, None], data: Union[list, None], guild: discord.guild):
    if action is None:
        return True
    elif action == 'add_role':
        for member in data[1]:
            try:
                await member.add_roles(*data[0])
            except BaseException as ex:
                print(ex)
        return True
    elif action == 'remove_role':
        for member in data[1]:
            try:
                await member.remove_roles(*data[0])
            except BaseException:
                pass
        return True
    elif action == 'move':
        for member in data[1]:
            try:
                await member.move_to(data[0])
            except BaseException:
                pass
        return True
    elif action == 'kick':
        for member in data:
            try:
                await member.kick(reason='Result of poll')
            except BaseException:
                pass
        return True
    elif action == 'ban':
        for member in data:
            try:
                await member.ban(reason='Result of poll')
            except BaseException:
                pass
        return True
    elif action == 'unban':
        for user in data:
            try:
                await guild.unban(user, reason='Result of poll')
            except BaseException:
                pass
        return True
    elif 'deafen' in action:
        deafen_status = 'un' not in action
        for member in data:
            try:
                await member.edit(deaf=deafen_status)
            except BaseException:
                pass
        return True
    elif 'mute' in action:
        mute_status = 'un' not in action
        for member in data:
            try:
                await member.edit(mute=mute_status)
            except BaseException:
                pass
        return True
    elif action == 'change_nickname':
        for member in data[1]:
            try:
                await member.edit(nick=data[0])
            except BaseException:
                pass
        return True
