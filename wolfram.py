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
        """Wolframalpha solver, anything that normal wolframalpha can do"""

        globals.messages += 1
        result = client.query(string)
        answer = next(result.results).text
        await ctx.send('{} Result: {}' .format(ctx.message.author.mention, answer))

    @commands.command(pass_context=True)
    async def graph(self, ctx, *, string):
        """Wolframalpha graphing"""

        globals.messages += 1
        result = client.query("graph " + string)
        #answer = next(result.results).subpods
        result = list(result)
        imageURL = result[1].get('subpod').get('img').get('@src')
        embed = discord.Embed()
        embed.set_image(url=imageURL)
        await ctx.send(embed=embed)