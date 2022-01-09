import asyncio
import random

import discord.ui
from discord import Interaction
from utils.check_author import check
from views.select import SelectView


class AddSelectOptionButton(discord.ui.Button):
    def __init__(self, author, main_view):
        self.main_view = main_view
        self.author = author
        self.message: discord.Message
        self.work_object = [self.main_view[x] for x in ['poll_action', 'button_action'] if self.main_view[x]][
            0].select
        if self.work_object.additional_select is not None:
            self.work_object = self.work_object.additional_select
        super().__init__(label='Add to select', style=discord.ButtonStyle.success, custom_id=f'add.{random.randint(0, 9999999)}')

    async def callback(self, interaction: Interaction):
        if not interaction.user == self.author:
            return await interaction.response.send_message('Please do not interrupt other people',
                                                           ephemeral=True)
        await interaction.response.send_message(
            f'Okay, send me {self.work_object.action.split("_")[-1] if not self.work_object.action == "move" else "voice channel"} {"name / mention / id or whatever" if self.work_object.action != "unban" else "send me name and user digits like that name#digits"}')
        try:
            message = await self.main_view.bot.wait_for('message', check=check(interaction.user),
                                                        timeout=30)
            option = await self.work_object.get_needed_option(message)
            if type(option) != str:
                self.work_object.append_option(option)
                try:
                    await self.work_object.message.edit(view=SelectView(self, self.work_object))
                except BaseException:
                    self.work_object.options.pop()
                    return await interaction.followup.send('Already added')
                return await interaction.followup.send('Done')
            return await interaction.followup.send(option)
        except asyncio.exceptions.TimeoutError:
            pass

    async def end(self):
        await self.message.delete()
        del self
