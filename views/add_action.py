import logging
import random

import discord
from discord import Interaction
from discord.ext.commands import AutoShardedBot, Context
from discord.ui import View

from selects.poll_action import PollActionSelectMenu


class AddActionView(View):
    def __init__(self, bot: AutoShardedBot, author: discord.Member, position: str, ctx: Context):
        super().__init__(timeout=None)
        self.author = author
        self.ctx = ctx
        self.bot = bot
        self.position = position
        self.bans: list
        self.overload = False
        self.message: discord.Message
        self.add_item(PollActionSelectMenu(author=author, position=position, main_view=self, bot=bot))
        self.in_process = True
        self.custom_id = f'add_action_view.{random.randint(0, 9999999)}'

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
        pool = self['poll_action'] or self['button_action']
        await self.message.delete()
        del self
        return await pool.end()

    @discord.ui.button(label='Back to managing', style=discord.ButtonStyle.secondary, custom_id='end_adding')
    async def end_adding_callback(self, button, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        try:
            self.in_process = False
        except BaseException as e:
            logging.error("Exception occurred", exc_info=True)
