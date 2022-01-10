import asyncio
import logging
import random

import discord
from discord import Interaction
from discord.ext.commands import Context
from discord.ui import View

from data import db_session
from data.config import WEBSITE
from data.premium_modules import PremiumModule
from utils.check_author import check
from utils.get_action_object import get_action_object
from views.add_action import AddActionView
from views.beutify_answers import BeautifyAnswersView
from views.choose_action_condition import ActionConditionView
from views.poll import PollView

db_session.global_init("db/jessy.db")
db_sess = db_session.create_session()


class CreatePollView(View):
    def __init__(self, author: discord.Member, bot: discord.AutoShardedBot, question: str, number_of_answers: int,
                 lifetime: int, ctx: Context,
                 answers=None,
                 now_on=0):
        super().__init__(timeout=None)
        if answers is None:
            answers = []
        self.ctx = ctx
        self.author = author
        self.action_on_end = {'action': None, 'action_object': None, 'condition': '-1'}
        self.bot = bot
        me = self.bot.me(author.guild)
        self.message: discord.Message
        self.question = question
        self.number_of_answers = number_of_answers
        self.answers = answers
        self.now_on = now_on
        self.lifetime = lifetime
        self.is_button_editing = False
        self.custom_id = f'create_poll_view.{random.randint(0, 9999999)}'
        self.action_module_bought = bool(db_sess.query(PremiumModule).filter(PremiumModule.guild_id == author.guild.id,
                                                                             PremiumModule.name == 'poll_actions').first())
        if not any([getattr(author.guild_permissions, item) and getattr(me.guild_permissions, item) for item in
                    ['manage_roles', 'ban_members', 'kick_members', 'manage_nicknames', 'deafen_members',
                     'mute_members',
                     'move_members']]) or not self.action_module_bought:
            self.remove_item(self['add_action'])
            self.remove_item(self['choose_condition'])

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
        result = [x for x in self.children if x.custom_id.split('.')[0] == key]
        return result[0] if result else None

    def keys(self):
        return [x.custom_id for x in self.children]

    @discord.ui.button(label='Fill answers with text', style=discord.ButtonStyle.primary, custom_id='fill_answers')
    async def fill_answers_callback(self, button, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            inter_message = interaction.message
            await self.freeze(inter_message)
            await interaction.response.edit_message(view=self)
            while self.now_on < self.number_of_answers:
                await interaction.followup.send(content=f'Okay, write a label for answer №{self.now_on + 1}')
                answer = await self.bot.wait_for('message', check=check(interaction.user), timeout=30)
                view = BeautifyAnswersView(main_view=self, bot=self.bot,
                                           jump_button='end_beauty' if self.now_on + 1 == self.number_of_answers else '',
                                           author=self.author, label=answer.content)
                view.message = await interaction.followup.send(
                    content=f'⬇️Here is an example how your answer button will looks like, you can change it by pressing style buttons\nIf you want to add emoji, react to this message and then click on answer button',
                    view=view)
                while view.in_process:
                    await asyncio.sleep(1)
                self.now_on += 1
                self.answers.append(view.get_result())
                await view.end()
            await self.unfreeze(inter_message)
            await inter_message.delete()
            self.message = await interaction.followup.send("Let's manage it", embed=Embed(
                description=f"{f'You can do a lot more with poll actions, check out our website: [{WEBSITE}]({WEBSITE})'}",
                url=WEBSITE) if not self.action_module_bought else None, view=self)
            return
        except asyncio.exceptions.TimeoutError:
            return await interaction.followup.send(content='Ooops, looks like u didnt send anything 😭',
                                                   view=CreatePollView(bot=self.bot, question=self.question,
                                                                       number_of_answers=self.number_of_answers,
                                                                       answers=self.answers, now_on=self.now_on - 1,
                                                                       lifetime=self.lifetime, author=self.author,
                                                                       ctx=self.ctx
                                                                       ))
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)

    @discord.ui.button(label='Add action', style=discord.ButtonStyle.secondary, custom_id='add_action')
    async def add_action_callback(self, button, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            action_view = AddActionView(bot=self.bot, author=self.author, position='poll', ctx=self.ctx)
            message = interaction.message
            await self.freeze(message)
            await interaction.response.send_message('Set action', view=action_view)
            action_view.message = await interaction.original_message()
            action_view.bans = await self.author.guild.bans()
            if action_view.bans is None:
                action_view.bans = []
            while action_view.in_process:
                await asyncio.sleep(1)
            result = await action_view.end()
            self.action_on_end = self.action_on_end | result
            await self.unfreeze(message)
            await message.delete()
            await interaction.followup.send("Let's manage it", view=self)
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)

    @discord.ui.button(label='Choose condition', style=discord.ButtonStyle.secondary, custom_id='choose_condition',
                       disabled=True)
    async def choose_condition_callback(self, button, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            condition_view = ActionConditionView(bot=self.bot, author=self.author, main_view=self)
            message = interaction.message
            await self.freeze(message)
            await interaction.response.send_message('Choose condition', view=condition_view)
            condition_view['poll_action_conidition'].message = await interaction.original_message()
            while condition_view.in_process:
                await asyncio.sleep(1)
            self.action_on_end = self.action_on_end | {'condition': await condition_view.end()}
            await self.unfreeze(message)
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)

    @discord.ui.button(label='Start poll', style=discord.ButtonStyle.success, custom_id='start_poll',
                       disabled=True)
    async def start_poll_callback(self, button, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            view = PollView(bot=self.bot, buttons=self.answers, lifetime=self.lifetime, author=self.author,
                            question=self.question, **self.action_on_end)
            await interaction.response.send_message(embed=await view.get_poll_embed(), view=view)
            message = await interaction.original_message()
            await interaction.message.delete()
            await view.run_poll(message)
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)

    async def freeze(self, message):
        [setattr(self[x], 'disabled', True) for x in self.keys()]
        await message.edit(view=self)

    async def unfreeze(self, message):
        for item in self.keys():
            if item == 'fill_answers':
                self[item].disabled = False if self.now_on != self.number_of_answers else True
            elif item == 'choose_condition':
                self[item].disabled = False if self.now_on == self.number_of_answers and self.action_on_end[
                    'action'] else True
            elif item == 'start_poll':
                self[item].disabled = False if self.now_on == self.number_of_answers else True
            else:
                self[item].disabled = False
        await message.edit(view=self)
