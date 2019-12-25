import discord
import time
from discord.ext import commands
import globals

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        globals.messages += 1
        channel = ctx.message.channel
        t1 = time.perf_counter()
        t2 = time.perf_counter()
        embed = discord.Embed(title="Pong!", description='It took {}ms.'.format(round((t2 - t1) * 1000)),
                              color=0xffffff)
        await ctx.send(embed=embed)