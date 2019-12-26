import discord
import asyncio
from discord.ext import commands
import globals

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def memedog(self, ctx):
        """Show a random meme"""

        globals.messages += 1
        with open('meme_01.jpg', 'rb') as f:
            await ctx.send(file=discord.File(f, 'new_filename.png'))