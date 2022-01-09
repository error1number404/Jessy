import asyncio
import random

import discord
from discord import Interaction, SelectOption
from discord.ext.commands import RoleConverter, RoleNotFound, UserNotFound, UserConverter, MemberConverter, \
    MemberNotFound, VoiceChannelConverter, BadArgument, StageChannelConverter
from discord.ui import View
from discord.utils import find, get

from buttons.add_select_option import AddSelectOptionButton
from selects.additional import AdditionalSelectMenu
from utils.get_higher_role import get_higher_role
from views.select import SelectView


class ActionObjectSelectMenu(discord.ui.Select):
    def __init__(self, author: discord.Member, main_view: View, action: str):
        self.author = author
        self.main_view = main_view
        self.message: discord.Message
        self.action = action
        self.additional_select = None
        row = 3 if action in ['ban', 'kick', 'change_nickname'] else 4
        options = self.get_options()
        max_values = 1 if action in ['ban', 'kick', 'change_nickname'] else len(options)
        super().__init__(placeholder='Choose action object', options=options,
                         custom_id=f'{action}_action_object.{random.randint(0, 9999999)}', row=row, max_values=max_values)

    async def callback(self, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        if self.additional_select and self.action not in ['add_role', 'remove_role', 'move']:
            await self.additional_select.end()
            self.additional_select = None
        if self.values[0] in ['member', 'members_with_role']:
            self.additional_select = AdditionalSelectMenu(author=self.author,
                                                          action=self.values[0],
                                                          main_view=self.main_view)
            await interaction.response.send_message(
                f'Choose {"role" if self.values[0] == "members_with_role" else "member"}',
                view=SelectView(self.additional_select))
            self.additional_select.message = await interaction.original_message()
            if self.main_view.overload:
                add_button = AddSelectOptionButton(author=self.author, main_view=self.main_view)
                message = add_button.work_object.message
                await message.edit(view=SelectView(add_button, add_button.work_object))
        elif self.action in ['add_role', 'remove_role'] and not self.additional_select and self.main_view[
            'poll_action']:
            self.additional_select = AdditionalSelectMenu(author=self.author,
                                                          action='member',
                                                          main_view=self.main_view)
            await interaction.response.send_message(
                'Choose member',
                view=SelectView(self.additional_select))
            self.additional_select.message = await interaction.original_message()
            if self.main_view.overload:
                add_button = AddSelectOptionButton(author=self.author, main_view=self.main_view)
                message = add_button.work_object.message
                await message.edit(view=SelectView(add_button, add_button.work_object))
        elif self.action in ['move'] and not self.additional_select and self.main_view[
            'poll_action']:
            self.additional_select = AdditionalSelectMenu(author=self.author,
                                                          action=self.action,
                                                          main_view=self.main_view)
            await interaction.response.send_message(
                'Choose voice channel',
                view=SelectView(self.additional_select))
            self.additional_select.message = await interaction.original_message()
            if self.main_view.overload:
                add_button = AddSelectOptionButton(author=self.author, main_view=self.main_view)
                message = add_button.work_object.message
                await message.edit(view=SelectView(add_button, add_button.work_object))

    def get_options(self):
        options = []
        if self.action in ['add_role', 'remove_role'] and len(self.author.guild.roles) < 25:
            options = [SelectOption(label=x.name, value=str(x.id)) for x in
                       list(filter(lambda x: x < get_higher_role(self.author) and not x.is_default(),
                                   self.author.guild.roles))]
        elif self.action in ['ban', 'kick', 'change_nickname']:
            options = [SelectOption(label='Member', value='member'),
                       SelectOption(label='Members with role ...', value='members_with_role')]
        elif self.action == 'unban' and len(self.main_view.bans) < 25:
            options = [SelectOption(label=x.user.name, value=str(x.user.id)) for x in
                       self.main_view.bans]
        elif self.action == 'move' and self.main_view['poll_action'] and len(
                query := list(filter(lambda x: x.voice is not None, self.author.guild.members))) < 25:
            try:
                options = [SelectOption(label=x.name, value=str(x.id)) for x in query]
            except BaseException:
                pass
        elif self.action == 'move' and self.main_view['button_action'] and len(
                query := self.author.guild.voice_channels + self.author.guild.stage_channels) < 25:
            try:
                options = [SelectOption(label=x.name, value=str(x.id)) for x in query]
            except BaseException:
                pass
        elif self.action == 'deafen' and len(
                query := list(
                    filter(lambda x: x.voice is not None and not x.voice.deaf, self.author.guild.members))) < 25:
            try:
                options = [SelectOption(label=x.name, value=str(x.id)) for x in query]
            except BaseException:
                pass
        elif self.action == 'mute' and len(
                query := list(
                    filter(lambda x: x.voice is not None and not x.voice.mute, self.author.guild.members))) < 25:
            try:
                options = [SelectOption(label=x.name, value=str(x.id)) for x in query]
            except BaseException:
                pass
        elif self.action == 'undeafen' and len(
                query := list(filter(lambda x: x.voice is not None and x.voice.deaf, self.author.guild.members))) < 25:
            try:
                options = [SelectOption(label=x.name, value=str(x.id)) for x in query]
            except BaseException:
                pass
        elif self.action == 'unmute' and len(
                list(filter(lambda x: x.voice is not None and x.voice.mute, self.author.guild.members))) < 25:
            try:
                options = [SelectOption(label=x.name, value=str(x.id)) for x in query]
            except BaseException:
                pass
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
        if self.action in ['add_role', 'remove_role']:
            try:
                result = await RoleConverter().convert(ctx=self.main_view.ctx, argument=message.content)
                if not result < get_higher_role(self.author):
                    return "You can not manage that role"
            except BaseException:
                return 'Role not found'
            if self.max_values < 5 and len(self.options) > 1:
                self.max_values += 1
        elif self.action == 'unban':
            try:
                name, discriminator = message.content.split('#')
                if not (result := get(self.main_view.bans, user__name=name, user__discriminator=discriminator).user):
                    return "That user is not banned"
            except BaseException:
                return 'User not found'
            if self.max_values < 5 and len(self.options) > 1:
                self.max_values += 1
        elif self.action == 'move' and self.main_view['button_action']:
            try:
                result = await VoiceChannelConverter().convert(ctx=self.main_view.ctx, argument=message.content)
            except BadArgument:
                try:
                    result = await StageChannelConverter().convert(ctx=self.main_view.ctx, argument=message.content)
                except BadArgument:
                    return 'Channel not found'
        else:
            try:
                result = await MemberConverter().convert(ctx=self.main_view.ctx, argument=message.content)
                if get_higher_role(result) >= get_higher_role(self.author):
                    return 'You can not manage this person'
                if not result.voice:
                    return 'That user not in any channel now'
                elif self.action == 'mute' and result.voice.mute:
                    return 'That user is already muted'
                elif self.action == 'deafen' and result.voice.deaf:
                    return 'That user is already deafened'
                elif self.action == 'unmute' and not result.voice.mute:
                    return 'That user is already unmuted'
                elif self.action == 'undeafen' and not result.voice.deaf:
                    return 'That user is already undeafened'
            except BaseException:
                return 'Member not found'
            if self.max_values < 5 and len(self.options) > 1:
                self.max_values += 1

        return SelectOption(label=result.name, value=str(result.id))

    def get_result(self) -> dict:
        values = self.additional_select.get_result() if self.additional_select else self.values
        values = list(filter(lambda x: x not in ['overload', 'none'], values))
        if len(self.values) > 1:
            self.values[0] = ' '.join(self.values)
        return {self.values[0]: values} if self.additional_select else values

    async def end(self):
        await self.message.delete()
        del self
