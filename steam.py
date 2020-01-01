import discord
import requests
import json
from discord.ext import commands
import globals

app_id = "FB70036E9D18F2E4BAFE570A7934EB83"

class Steam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def stat(self, ctx, *, string):
        """Displays Steam account's summary of a specific person from his/her Steam ID"""

        url = ('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' + app_id + '&steamids=' + string)
        info_string = (requests.get(url).content)
        info_dict = json.loads(info_string)

        nickname = info_dict.get("response").get("players")[0].get("personaname")
        realname = info_dict.get("response").get("players")[0].get("realname")
        profileurl = info_dict.get("response").get("players")[0].get("profileurl")
        avatar = info_dict.get("response").get("players")[0].get("avatarmedium")

        embed = discord.Embed(title="Steam Summary", description="User " + string, color=0x00ff00)
        embed.add_field(name="Nickname", value=nickname, inline=False)
        embed.add_field(name="Real name", value=realname, inline=False)
        embed.add_field(name="Profile URL", value=profileurl, inline=False)
        embed.add_field(name="Avatar", value='\0', inline=False)
        embed.set_image(url=avatar)
        await ctx.send(embed=embed)



