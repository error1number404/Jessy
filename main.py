import logging
from abc import ABC
from glob import glob

import discord
from discord.ui import View
from discord.utils import get

from data import db_session
from data.config import TOKEN
from data.discord_server import DiscordServer

logging.basicConfig(level=logging.ERROR, filename='log/jessy_logs.txt', format='%(asctime)s - %(message)s\n')
db_session.global_init("db/jessy.db")
db_sess = db_session.create_session()
COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")]


class Jessy(discord.AutoShardedBot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self.id = 927550578345795664

    def setup(self):
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")

    def run(self):
        self.setup()
        super().run(TOKEN, reconnect=True)

    def me(self, guild):
        return get(guild.members, id=self.id)

    async def on_guild_join(self, guild):
        new_guild = DiscordServer(id=guild.id)
        db_sess.add(new_guild)
        db_sess.commit()

    async def on_guild_remove(self, guild):
        db_sess.query(DiscordServer).filter(DiscordServer.id == guild.id).delete()
        db_sess.commit()

    async def on_reaction_add(self, reaction, user):
        if reaction.message.author.id == self.id and reaction.message.components is not None:
            if [x for x in reaction.message.components[0].children if x.custom_id == 'answer_button']:
                if len(reaction.message.reactions) > 1:
                    [await reaction.message.clear_reaction(x) for x in reaction.message.reactions[1:]]
                    return


intents = discord.Intents().all()
# intents.members = True
# intents.presences = True
bot = Jessy(intents=intents, help_command=None)
bot.run()
