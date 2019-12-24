import asyncio
import discord
from discord.ext import commands

class Insult(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def insult(self, ctx):
        await ctx.send('<@328195790465925121> fat fuck')

