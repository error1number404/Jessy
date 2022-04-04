import discord
from discord import Option
from discord.ext import commands


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[457159286158655498, 922801946484674601,931576011437531136],
                            description='Clear text channel history.')
    @commands.has_permissions(manage_messages=True)
    async def clear_history(self, ctx,
                            limit: Option(int, 'Number of messages to delete', required=False, default=None)):
        await ctx.channel.purge(limit=limit)
        return await ctx.respond('Done', ephemeral=True)

    @commands.slash_command(guild_ids=[457159286158655498, 922801946484674601, 695277861572968488],
                            description='Kill bot')
    @commands.is_owner()
    async def kill(self, ctx):
        return await self.bot.close()


def setup(bot):
    bot.add_cog(MainCog(bot))
