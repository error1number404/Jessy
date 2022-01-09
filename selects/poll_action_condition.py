import random

import discord
from discord import Interaction, SelectOption
from discord.ui import View


class PollActionConditionSelectMenu(discord.ui.Select):
    def __init__(self, author: discord.Member, main_view: View):
        self.author = author
        self.main_view = main_view
        self.message: discord.Message
        options = [SelectOption(label='Whatever', description='Poll action will be done no matter what',
                                value='-1')] + [
                      SelectOption(label=item['label'], emoji=item['emoji'],
                                   description='Poll action will be done if this answer get max votes',
                                   value=str(index)) for index, item in enumerate(self.main_view.answers)]
        super().__init__(placeholder='Choose on what condition action will be done', options=options,
                         custom_id=f'poll_action_conidition.{random.randint(0, 9999999)}', row=2)

    async def callback(self, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)

    def __bool__(self):
        return bool(self.options)

    def get_result(self):
        result = self.values if self.values else ['-1']
        return result[0]

    async def end(self):
        result = self.get_result()
        await self.message.delete()
        del self
        return result
