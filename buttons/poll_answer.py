import discord.ui
from discord import Interaction

from utils.apply_action import apply_action
from utils.get_action_object import get_action_object
from utils.get_higher_role import get_higher_role


class PollAnswerButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        print(kwargs)
        self.main_view = kwargs.pop('view')
        self.index = kwargs.pop('index')
        self.action = kwargs.pop('action')
        self.action_object = kwargs.pop('action_object')
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: Interaction):
        if interaction.user.id not in self.main_view.users_in_poll:
            self.main_view.users_in_poll.add(interaction.user.id)
            self.main_view.answers[self.index].add(interaction.user.id)
            return await interaction.response.send_message('Your vote has been counted!', ephemeral=True)
        return await interaction.response.send_message('You have already vote', ephemeral=True)

    async def do_action(self):
        if self.action is None:
            return None
        if self.action == 'move':
            action_objects = await get_action_object(
                objects=[self.main_view.answers[self.index], self.action_object],
                scope='button_move', guild=self.main_view.author.guild)
        elif self.action in ['add_role', 'remove_role']:
            action_objects = await get_action_object(
                objects=[' '.join(list(map(str, self.action_object))), self.main_view.answers[self.index]],
                scope=self.action, guild=self.main_view.author.guild)
        else:
            action_objects = await get_action_object(
                objects=self.main_view.answers[self.index],
                scope=self.action, guild=self.main_view.author.guild)
        if self.action in ['kick', 'ban']:
            author_higher_role = get_higher_role(self.main_view.author)
            action_objects = list(filter(lambda x: get_higher_role(x) < author_higher_role, action_objects))
        if self.action == 'change_nickname':
            await apply_action(action=self.action, data=[self.action_object['nickname'], action_objects],
                               guild=self.main_view.author.guild)
        else:
            await apply_action(action=self.action, data=action_objects, guild=self.main_view.author.guild)
