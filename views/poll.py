import asyncio
import logging
from typing import Union

import discord
from discord.ui import View
from buttons.poll_answer import PollAnswerButton
from pycord.discord.utils import get
from utils.apply_action import apply_action
from utils.get_action_object import get_action_object
import random


class PollView(View):
    def __init__(self, bot, buttons, lifetime: int, question: str, author: discord.Member,
                 result_channel: Union[discord.TextChannel, None], anonymous: bool, **kwargs):
        super().__init__(timeout=None)
        [setattr(self, key, kwargs[key]) for key in kwargs]
        self.question = question
        self.author = author
        self.lifetime = lifetime
        self.bot = bot
        self.k = 0
        self.users_in_poll = set()
        self.answers = [set() for _ in range(len(buttons))]
        self.custom_id = f'poll_view.{random.randint(0, 9999999)}'
        self.result_channel = result_channel
        self.anonymous = anonymous
        [self.add_item(PollAnswerButton(
            **(item | {'index': index, 'view': self, 'custom_id': f"{item['label']}.{random.randint(0, 9999999)}"})))
            for
            index, item in
            enumerate(buttons)]

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

    # @discord.ui.button(label='End now', style=discord.ButtonStyle.danger, custom_id='end_now', row=2)
    # async def end_now_callback(self, button, interaction):
    #     if interaction.user == self.author:
    #         self.lifetime = 10
    #         return await interaction.response.send_message('Now it will be ended', ephemeral=True)
    #     else:
    #         return await interaction.response.send_message('You are not a author of poll', ephemeral=True)

    async def initialize_poll(self, poll_message):
        self.poll_message = poll_message
        self.poll_message_channel = poll_message.channel
        self.bot.polls.add(self)

    async def proceed_poll(self):
        if self.lifetime:
            edit = {}
            # if self.k % 15 == 0:
            #     for child in self.children:
            #         child.label = f'{child.label.split("|")[0]} | {round((len(self.answers[child.index]) / len(self.users_in_poll)) * 100) if self.answers[child.index] else 0}%'
            #     edit['view'] = self
            if self.k % 5 == 0:
                edit['embed'] = await self.get_poll_embed()
                await self.poll_message.edit(**edit)
            self.k += 5 if self.lifetime >= 5 else self.lifetime
            self.lifetime -= 5 if self.lifetime >= 5 else self.lifetime
        else:
            for child in self.children:
                child.disabled = True
                child.label = f'{child.label.split("|")[0]} | {round((len(self.answers[child.index]) / len(self.users_in_poll)) * 100) if self.answers[child.index] else 0}%'
            await self.poll_message.edit(embed=await self.get_poll_embed(), view=self)
            self.lifetime = self.k
            if not self.result_channel:
                await self.poll_message_channel.send(embed=await self.get_poll_embed_result())
            else:
                await self.result_channel.send(embed=await self.get_poll_embed_result())
            return await self.kill()

    async def get_poll_embed(self):
        embed = discord.Embed(
            title=self.question,
            description=f'Lifetime : {self.lifetime} seconds' if self.lifetime else 'Poll is ended',
            colour=discord.Colour.from_rgb(106, 192, 245)
        )
        if not self.anonymous:
            embed.set_author(name=self.author.name, icon_url=self.author.avatar.url)
        return embed

    async def get_digit_emoji(self, digit):
        words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        return f":{words[digit]}:"

    async def get_poll_embed_result(self):
        await self.do_actions()
        embed = discord.Embed(
            title=f"Here is a result of poll '{self.question}'",
            description=f'Poll lasted for {self.lifetime} seconds' + '\n\n',
            colour=discord.Colour.from_rgb(106, 192, 245)
        )
        embed.description += f'At the end was  **{len(self.users_in_poll)}**  members that actually vote in poll' + '\n\n'
        embed.description += '\n'.join([
            f'Here is **{len(self.answers[item.index])}** votes for {item.emoji if item.emoji else ""}**{item.label.split(" | ")[0]}**. It is {round((len(self.answers[item.index]) / len(self.users_in_poll)) * 100) if self.answers[item.index] else 0}% of all votes'
            for item in self.children])
        if not self.anonymous:
            embed.set_author(name=self.author.name, icon_url=self.author.avatar.url)
        return embed

    async def do_actions(self):
        keys = None
        if type(self.action_object) is dict:
            keys = [key for key in self.action_object]
        if self.action is None:
            pass
        elif keys and (keys[0].isnumeric() or keys[0].split()[0].isnumeric()):
            action_objects = await get_action_object(
                objects=[keys[0], self.action_object[keys[0]]],
                scope=self.action, guild=self.author.guild)
        elif keys:
            action_objects = await get_action_object(
                objects=self.action_object[keys[0]],
                scope=keys[0], guild=self.author.guild)
        else:
            action_objects = await get_action_object(objects=self.action_object,
                                                     scope=self.action, guild=self.author.guild, bot=self.bot)
        if (self.condition == '-1' or self.answers[int(self.condition)] == max(self.answers, key=len)) and self.action:
            if self.action == 'change_nickname':
                await apply_action(action=self.action, data=[self.action_object['nickname'], action_objects],
                                   guild=self.author.guild)
            else:
                await apply_action(action=self.action, data=action_objects, guild=self.author.guild)
        for item in self.children:
            await item.do_action()

    async def kill(self):
        self.bot.polls.remove(self)
        del self
