import logging
import random

import discord
from discord import Interaction
from discord.ext.commands import AutoShardedBot, Context
from discord.ui import View

from selects.poll_action import PollActionSelectMenu
from selects.poll_action_condition import PollActionConditionSelectMenu


class ActionConditionView(View):
    def __init__(self, bot: AutoShardedBot, main_view: View, author: discord.Member):
        super().__init__(timeout=None)
        self.author = author
        self.bot = bot
        self.add_item(PollActionConditionSelectMenu(author=author, main_view=main_view))
        self.in_process = True
        self.custom_id = f'action_condition_view.{random.randint(0, 9999999)}'

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

    async def end(self):
        pool_condition = self['poll_action_conidition']
        del self
        return await pool_condition.end()

    @discord.ui.button(label='Back to managing', style=discord.ButtonStyle.secondary,
                       custom_id='end_choosing_condition')
    async def end_choosing_callback(self, button, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            self.in_process = False
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)
