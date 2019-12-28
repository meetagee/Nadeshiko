import discord
import asyncio
from discord.ext import commands
import globals

bot = commands.Bot(command_prefix='$')

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ava(self, ctx):
        """Get the mentioned user's avatar"""

        globals.messages += 1
        if ctx.message.mentions.__len__() > 0:
            for user in ctx.message.mentions:
                await ctx.send(user.avatar_url)
        else:
            await ctx.send('{} That is not a valid user senpai !'.format(ctx.message.author.mention))

    @bot.command()
    async def fake(self, ctx):
        """Change the bot's name and avatar to the same as the one mentioned"""

        globals.messages += 1
        if ctx.message.mentions.__len__() > 0:
            for user in ctx.message.mentions:
                await ctx.message.guild.me.edit(nick=user.name)
        else:
            await ctx.send('{} That is not a valid user senpai !'.format(ctx.message.author.mention))
