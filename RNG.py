import asyncio
import discord
import random
from discord.ext import commands

class RNG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def random(self, ctx, num):
        """Choose a random number between 1 and the input number"""

        arg = random.randint(1, int(num))
        await ctx.send('Why are you making me pick {} senpai?'.format(arg))

    @commands.command(pass_context=True)
    async def choose(self, ctx, *, string):
        """Choose one out of multiple inputs"""

        separated = string.split(", ")
        arg = random.choice(separated)
        await ctx.send('Hmmmm I think I will choose {} senpai'.format(arg))

    @commands.command()
    async def quoteNgoc(self, ctx):
        """Choose a random quote that Ngoc once said"""

        quotes = ["Wowowowowow :O", "Thế thì.. đỡ thế đéo nào được đây?", "Thôi mất hết rồi :<"]
        arg = random.randint(1, 3)
        await ctx.send('A wise man once said: {}'.format(quotes[arg-1]))
