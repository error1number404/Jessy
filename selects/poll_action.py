import asyncio
import random

import discord
from discord import Interaction, SelectOption
from discord.ui import View

from buttons.add_select_option import AddSelectOptionButton
from selects.action_object import ActionObjectSelectMenu
from utils.check_author import check
from views.select import SelectView


class PollActionSelectMenu(discord.ui.Select):
    def __init__(self, author: discord.Member, main_view: View, position: str, bot: discord.AutoShardedBot):
        self.author = author
        self.main_view = main_view
        self.position = position
        self.message: discord.Message
        me = bot.me(author.guild)
        purpose = 'сhosen object(s)' if position == 'poll' else 'person who pressed it'
        options = []
        if author.guild_permissions.manage_roles and me.guild_permissions.manage_roles:
            options.append(SelectOption(label='Add role',
                                        description=f'Сhosen role will be added to {purpose}', value='add_role'))
            options.append(SelectOption(label='Remove role',
                                        description=f'Сhosen role will be removed from {purpose}', value='remove_role'))
        if author.guild_permissions.ban_members and me.guild_permissions.ban_members:
            options.append(SelectOption(label='Ban',
                                        description=f'{purpose.capitalize()} will be banned', value='ban'))
            if self.position == 'poll':
                options.append(SelectOption(label='Unban',
                                            description=f'{purpose.capitalize()} will be unbanned', value='unban'))
        if author.guild_permissions.kick_members and me.guild_permissions.kick_members:
            options.append(SelectOption(label='Kick',
                                        description=f'{purpose.capitalize()} will be kicked', value='kick'))
        if author.guild_permissions.manage_nicknames and me.guild_permissions.manage_nicknames:
            options.append(SelectOption(label='Change nickname',
                                        description=f'{purpose.capitalize()} will have chosen nickname',
                                        value='change_nickname'))
            self.nickname = 'Kenny'
        if author.guild_permissions.deafen_members and me.guild_permissions.deafen_members:
            options.append(SelectOption(label='Deafen',
                                        description=f'{purpose.capitalize()} will be deafened', value='deafen'))
            options.append(SelectOption(label='Undeafen',
                                        description=f'{purpose.capitalize()} will be undeafened', value='undeafen'))
        if author.guild_permissions.mute_members and me.guild_permissions.mute_members:
            options.append(SelectOption(label='Mute',
                                        description=f'{purpose.capitalize()} will be muted', value='mute'))
            options.append(SelectOption(label='Unmute',
                                        description=f'{purpose.capitalize()} will be unmuted', value='unmute'))
        if author.guild_permissions.move_members and me.guild_permissions.move_members:
            options.append(SelectOption(label='Move',
                                        description=f'{purpose.capitalize()} will be moved to the chosen channel',
                                        value='move'))

        self.select = None
        super().__init__(placeholder='Choose action on the end of the poll', options=options,
                         custom_id=f'{position}_action.{random.randint(0, 9999999)}', row=2)

    async def callback(self, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        if self.select:
            if self.select.additional_select:
                await self.select.additional_select.end()
            await self.select.end()
            self.main_view.overload = False
        if self.values[0] in ['add_role', 'remove_role'] and self.position == 'button':
            self.select = ActionObjectSelectMenu(author=self.author, main_view=self.main_view,
                                                 action=self.values[0])
            await interaction.response.send_message('Choose role', view=SelectView(self.select))
            self.select.message = await interaction.original_message()
        elif self.values[0] in ['move'] and self.position == 'button':
            self.select = ActionObjectSelectMenu(author=self.author, main_view=self.main_view,
                                                 action=self.values[0])
            await interaction.response.send_message('Choose voice channel', view=SelectView(self.select))
            self.select.message = await interaction.original_message()
        elif self.position == 'poll':
            self.select = ActionObjectSelectMenu(author=self.author, main_view=self.main_view,
                                                 action=self.values[0])
            if self.values[0] == 'change_nickname':
                await interaction.response.send_message('Send new nickname')
                self.select.message = await interaction.original_message()
                try:
                    mes = await self.main_view.bot.wait_for('message', check=check(interaction.user), timeout=30)
                    self.nickname = mes.content
                    await interaction.followup.send('Okay, look up')
                except asyncio.exceptions.TimeoutError:
                    self.nickname = 'Kenny'
                    await interaction.followup.send('Okay, it will be Kenny')
                await self.select.message.edit('Choose action object', view=SelectView(self.select))
            else:
                await interaction.response.send_message('Choose action object', view=SelectView(self.select))
                self.select.message = await interaction.original_message()
        elif self.position == 'button' and self.values[0] == 'change_nickname':
            await interaction.response.send_message('Send new nickname')
            try:
                mes = await self.main_view.bot.wait_for('message', check=check(interaction.user), timeout=30)
                self.nickname = mes.content
            except asyncio.exceptions.TimeoutError:
                self.nickname = 'Kenny'
                await interaction.followup.send('Okay, it will be Kenny')
        if self.main_view.overload and self.values[0] in ['unban', 'add_role', 'remove_role', 'move']:
            add_button = AddSelectOptionButton(author=self.author, main_view=self.main_view)
            message = add_button.work_object.message
            await message.edit(view=SelectView(add_button, add_button.work_object))

    def __bool__(self):
        return bool(self.options)

    def get_result(self):
        result = {'action': self.values[0] if self.values else None,
                  'action_object': self.select.get_result() if self.values and self.select else None}
        if result['action'] == 'change_nickname':
            result['action_object']['nickname'] = self.nickname
        if len(self.values) > 1:
            result['action'] = ' '.join(self.values)
        return result

    async def end(self):
        result = self.get_result()
        await asyncio.sleep(1)
        if self.select:
            if self.select.additional_select:
                await self.select.additional_select.end()
            await self.select.end()
        del self
        return result
