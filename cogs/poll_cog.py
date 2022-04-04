import discord
from discord import Option, Embed
from discord.ext import commands, tasks

from data.config import MAIN_ROLE, WEBSITE
from selects.poll_action import PollActionSelectMenu
from views.create_poll import CreatePollView


class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.poll_loop.start()

    @commands.slash_command(guild_ids=[457159286158655498, 922801946484674601, 695277861572968488, 942313682464043048],
                            description='Create poll in this channel')
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def create_poll(self, ctx, question: Option(str, description='Question in poll', required=True, default=''),
                          number_of_answers: Option(int, description='Number of answers', required=True, min_value=2,
                                                    max_value=5),
                          lifetime: Option(int, description='Lifetime of poll in seconds(by default 180 seconds)',
                                           required=False, min_value=30,
                                           default=180),
                          text: Option(str,
                                       description='Parameter for mention or other stuff which wouldnt be in embed text',
                                       required=False, default=''),
                          channel: Option(discord.TextChannel,
                                          description='Text channel where poll should be posted(by default this channel)',
                                          required=False, default=None),
                          result_channel: Option(discord.TextChannel,
                                                 description='Text channel where result of the poll should be posted(by default channel where poll created)',
                                                 required=False, default=None),
                          anonymous: Option(bool,
                                            description='If True author of poll wouldnt be shown(by default False)',
                                            required=False, default=False)
                          ):
        view = CreatePollView(bot=self.bot, question=question,
                              number_of_answers=number_of_answers, author=ctx.author,
                              lifetime=lifetime, ctx=ctx, text=text, channel=channel if channel else ctx.channel,
                              result_channel=result_channel if result_channel else ctx.channel, anonymous=anonymous)
        return await ctx.respond("Let's manage it\n", embed=Embed(
            description=f"{f'You can do a lot more with poll actions, check out our website: [{WEBSITE}]({WEBSITE})'}",
            url=WEBSITE) if not view.action_module_bought else None,
                                 view=view)

    @create_poll.error
    async def error_handle(self, ctx, error):
        return await ctx.respond(str(error), ephemeral=True)

    @tasks.loop(seconds=5.0)
    async def poll_loop(self):
        print('loop working')
        try:
            for poll in self.bot.polls:
                print(poll)
                await poll.proceed_poll()
        except BaseException:
            pass


def setup(bot):
    bot.add_cog(PollCog(bot))