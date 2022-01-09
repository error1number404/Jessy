import asyncio
import logging
import random

import discord
from discord import AutoShardedBot
from discord.ui import View

from views.add_action import AddActionView


class BeautifyAnswersView(View):
    def __init__(self, main_view: View, author: discord.Member, bot: AutoShardedBot, jump_button=None, **kwargs):
        super().__init__(timeout=300)
        self.author = author
        self.bot = bot
        self.main_view = main_view
        self.in_process = True
        self.custom_id = f'beautify_answers_view.{random.randint(0, 9999999)}'
        self.result = {'label': '', 'emoji': None,
                       'style': discord.ButtonStyle.primary, 'action': None, 'action_object': None} | kwargs
        self.jump_button = jump_button
        answer_button = self['answer_button']
        [setattr(answer_button, key, self.result[key]) for key in self.result]
        if jump_button == 'end_beauty':
            create_poll = self['next_answer']
            create_poll.label = 'End answers editing'
            create_poll.style = discord.ButtonStyle.success
        if not self.main_view['add_action']:
            self.remove_item(self['button_action_add'])

    def __iter__(self):
        class iterator(object):
            def __init__(self, obj):
                self.obj = obj
                self.keys = obj.keys()
                self.custom_id = self.keys[0]
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index != len(self.keys) - 1:
                    self.index += 1
                    for_return = self.obj[self.custom_id]
                    self.custom_id = self.keys[self.index]
                    return for_return
                else:
                    raise StopIteration

        return iterator(self)

    def __getitem__(self, key):
        result = [x for x in self.children if x.custom_id == key]
        return result[0] if result else None

    def keys(self):
        return [x.custom_id for x in self.children]

    async def style_callback(self, button, interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            main_button = [x for x in self.children if x.custom_id == 'answer_button'][0]
            main_button.style = button.style
            self.result['style'] = button.style
            return await interaction.response.edit_message(view=self)
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)

    @discord.ui.button(label='', style=discord.ButtonStyle.primary, custom_id='answer_button', row=1)
    async def answer_callback(self, button, interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        channel = interaction.message.channel
        for message in await channel.history(limit=5).flatten():
            if message.author.id == self.bot.id:
                break
        if message.reactions:
            button.emoji = message.reactions[0].emoji
            self.result['emoji'] = message.reactions[0].emoji
            return await interaction.response.edit_message(view=self)
        else:
            button.emoji = None
            self.result['emoji'] = None
            return await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Primary', style=discord.ButtonStyle.primary, custom_id='primary_check', row=2)
    async def primary_callback(self, button, interaction):
        return await self.style_callback(button, interaction)

    @discord.ui.button(label='Secondary', style=discord.ButtonStyle.secondary, custom_id='secondary_check', row=2)
    async def secondary_callback(self, button, interaction):
        return await self.style_callback(button, interaction)

    @discord.ui.button(label='Danger', style=discord.ButtonStyle.danger, custom_id='danger_check', row=2)
    async def danger_callback(self, button, interaction):
        return await self.style_callback(button, interaction)

    @discord.ui.button(label='Success', style=discord.ButtonStyle.success, custom_id='success_check', row=2)
    async def success_callback(self, button, interaction):
        return await self.style_callback(button, interaction)

    @discord.ui.button(label='Jump to next', style=discord.ButtonStyle.secondary, custom_id='next_answer', row=3)
    async def jump_to_next_callback(self, button, interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            self.in_process = False
            return None
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)

    @discord.ui.button(label='Add action', style=discord.ButtonStyle.secondary, custom_id='button_action_add', row=3)
    async def button_action_add_callback(self, button, interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            action_view = AddActionView(bot=self.bot, author=self.author, position='button', ctx=self.main_view.ctx)
            message = interaction.message
            await interaction.response.send_message(
                'Set action that will be applied to members who vote for this answer', view=action_view)
            action_view.message = await interaction.original_message()
            await message.delete()
            while action_view.in_process:
                await asyncio.sleep(1)
            result = await action_view.end()
            self.result = self.result | result
            print(self.result)
            inter = await interaction.followup.send(
                content=f'⬇️Here is an example how your answer button will looks like, you can change it by pressing style buttons\nIf you want to add emoji, react to this message and then click on answer button',
                view=self)
            self.message = inter
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)

    async def freeze(self, message):
        [setattr(self[x], 'disabled', True) for x in self.keys()]
        await message.edit(view=self)

    async def unfreeze(self, message):
        for item in self.keys():
            self[item].disabled = False
        await message.edit(view=self)

    def get_result(self):
        return self.result

    async def end(self):
        await self.message.delete()
        result = self.get_result()
        del self
        return result
