import discord
import wolframalpha
from discord.ext import commands
import globals

app_id = "3GR9X9-Q6VYJW327K"
client = wolframalpha.Client(app_id)

class Wolfram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def wolf(self, ctx, *, string):
        """"""

        globals.messages += 1
        result = client.query(string)
        answer = next(result.results).text
        await ctx.send('Result: {}' .format(answer))