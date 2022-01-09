import discord
from discord import Option
from discord.ext import commands


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[457159286158655498, 922801946484674601])
    async def hello(self, ctx):
        return await ctx.respond(f'{self.bot.cogs}', ephemeral=True)

    @commands.slash_command(guild_ids=[457159286158655498, 922801946484674601],
                            description='Clear text channel history.')
    @commands.has_permissions(manage_messages=True)
    async def clear_history(self, ctx,
                            limit: Option(int, 'Number of messages to delete', required=False, default=None)):
        await ctx.channel.purge(limit=limit)
        return await ctx.respond('Done', ephemeral=True)

    @commands.slash_command(guild_ids=[457159286158655498, 922801946484674601],
                            description='Set role tag')
    async def set_role_tag(self, ctx,
                           role: Option(discord.Role, 'Role tag to set',
                                        required=True, default=None)):
        if role in ctx.author.roles:
            await ctx.author.edit(nick=f'[{role}] {ctx.author.name}')
            return await ctx.respond('Done', ephemeral=True)
        else:
            return await ctx.respond('You dont have that role', ephemeral=True)


def setup(bot):
    bot.add_cog(MainCog(bot))
