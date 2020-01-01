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
        """Wolfram Alpha solver 
        
        Basically solves anything that normal Wolfram Alpha can do (+, -, *, /, integral, differentiation, etc.)"""

        result = client.query(string)
        answer = next(result.results).text
        await ctx.send('[{}: {}]\nResult: {}' .format(ctx.message.author.mention, string, answer))

    @commands.command(pass_context=True)
    async def graph(self, ctx, *, string):
        """Graphs a function
        
        This is basically a specific Wolfram Alpha query with different inputs (functions)
        """

        result = client.query("graph " + string)
        result = list(result)
        imageURL = result[1].get('subpod').get('img').get('@src')
        embed = discord.Embed()
        embed.set_image(url=imageURL)
        await ctx.send(embed=embed)