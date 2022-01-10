from discord import Option, Embed
from discord.ext import commands

from data.config import MAIN_ROLE, WEBSITE
from selects.poll_action import PollActionSelectMenu
from views.create_poll import CreatePollView


class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[457159286158655498, 922801946484674601, 695277861572968488],
                            description='Create poll in this channel')
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def create_poll(self, ctx, question: Option(str, 'Question in poll', required=True, default=''),
                          number_of_answers: Option(int, 'Number of answers', required=True, min_value=2, max_value=5),
                          lifetime: Option(int, 'Lifetime of poll in seconds', required=False, min_value=30,
                                           default=180)):
        view = CreatePollView(bot=self.bot, question=question,
                              number_of_answers=number_of_answers, author=ctx.author,
                              lifetime=lifetime, ctx=ctx)
        return await ctx.respond("Let's manage it\n", embed=Embed(
            description=f"{f'You can do a lot more with poll actions, check out our website: [{WEBSITE}]({WEBSITE})'}",
            url=WEBSITE) if not view.action_module_bought else None,
                                 view=view)

    @create_poll.error
    async def error_handle(self, ctx, error):
        return await ctx.respond(str(error), ephemeral=True)


def setup(bot):
    bot.add_cog(PollCog(bot))
