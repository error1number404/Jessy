import random

import discord
from discord import Interaction, SelectOption
from discord.ext.commands import RoleConverter, RoleNotFound, MemberConverter, \
    MemberNotFound, BadArgument, VoiceChannelConverter, StageChannelConverter
from discord.ui import View

from utils.get_higher_role import get_higher_role


class AdditionalSelectMenu(discord.ui.Select):
    def __init__(self, main_view: View, author: discord.Member, action: str):
        self.author = author
        self.action = action
        self.main_view = main_view
        row = 4
        options = self.get_options()
        if self.action in ['members_with_role', 'member', 'add_role', 'remove_role']:
            max_values = 5 if len(options) > 5 else len(options)
        else:
            max_values = 1
        context = {'role': ['members_with_role'], 'member': ['member', 'add_role', 'remove_role'],
                   'voice channel': ['move']}
        super().__init__(placeholder=f'Choose {[x for x in context if self.action in context[x]][0]}', options=options,
                         custom_id=f'additional.{random.randint(0, 9999999)}', row=row, max_values=max_values)

    async def callback(self, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)

    def get_options(self):
        if self.action == 'members_with_role' and len(self.author.guild.roles) < 25:
            options = [SelectOption(label=x.name, value=str(x.id)) for x in
                       list(filter(lambda x: x < get_higher_role(self.author) and not x.is_default(),
                                   self.author.guild.roles))]
        elif self.action in ['member', 'add_role', 'remove_role'] and self.author.guild.member_count < 25:
            options = [SelectOption(label=x.name, value=str(x.id)) for x in
                       list(filter(lambda x: get_higher_role(x) < get_higher_role(self.author),
                                   self.author.guild.members))]
        else:
            options = [SelectOption(label='There is too many objects, please add manually', value='overload')]
            self.main_view.overload = True
        if len(options) >= 25:
            options = [SelectOption(label='There is too many objects, please add manually', value='overload')]
            self.main_view.overload = True
        if not options:
            options = [SelectOption(label='There is no object', value='none')]
        return options

    async def get_needed_option(self, message: discord.Message):
        if self.action == 'members_with_role':
            try:
                result = await RoleConverter().convert(ctx=self.main_view.ctx, argument=message.content)
                if result > get_higher_role(self.author):
                    return "You can not manage that role"
                if result.is_default():
                    return "Everyone is untoucheable :)"
            except RoleNotFound:
                return 'Role not found'
            if self.max_values < 5 and len(self.options) > 1:
                self.max_values += 1
        elif self.action in ['add_role', 'remove_role', 'member']:
            try:
                result = await MemberConverter().convert(ctx=self.main_view.ctx, argument=message.content)
                if get_higher_role(result) >= get_higher_role(self.author):
                    return 'You can not manage this person'
            except MemberNotFound:
                return 'Member not found'
            if self.max_values < 5 and len(self.options) > 1:
                self.max_values += 1
        elif self.action in ['move']:
            try:
                result = await VoiceChannelConverter().convert(ctx=self.main_view.ctx, argument=message.content)
            except BadArgument:
                try:
                    result = await StageChannelConverter().convert(ctx=self.main_view.ctx, argument=message.content)
                except BadArgument:
                    return 'Channel not found'

        return SelectOption(label=result.name, value=str(result.id))


    def get_result(self):
        return self.values

    async def end(self):
        await self.message.delete()
        del self
