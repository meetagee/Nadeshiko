import discord
import requests
import globals
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
from discord.ext import commands


class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def memedog(self, ctx):
        """Replaces the dog's face with mentioned user's avatar"""

        if ctx.message.mentions.__len__() > 0:
            for user in ctx.message.mentions:
                avatarURL = user.avatar_url
            response = requests.get(avatarURL)
            avatar = Image.open(BytesIO(response.content))
            avatar = avatar.resize((300, 300))
            size = (avatar.size[0] * 3, avatar.size[1] * 3)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            mask = mask.resize(avatar.size, Image.ANTIALIAS)
            avatar.putalpha(mask)
            meme = Image.open('media/meme_01.jpg')
            meme.paste(avatar, (215, 410), avatar)
            meme.save('media/tmp/meme_ava.png')
            with open('media/tmp/meme_ava.png', 'rb') as fp:
                await ctx.send(file=discord.File(fp, 'new_meme.png'))
            os.remove('media/tmp/meme_ava.png')
        else:
            await ctx.send('{} That is not a valid user senpai !'.format(ctx.message.author.mention))

    @commands.command()
    async def memestep(self, ctx):
        """Steps on mentioned user's face"""

        if ctx.message.mentions.__len__() == 1:
            for user in ctx.message.mentions:
                avatarURL = user.avatar_url
            response = requests.get(avatarURL)
            avatar = Image.open(BytesIO(response.content))
            avatar = avatar.resize((180, 180))
            size = (avatar.size[0] * 3, avatar.size[1] * 3)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            mask = mask.resize(avatar.size, Image.ANTIALIAS)
            avatar.putalpha(mask)
            meme = Image.open('media/meme_02.jpg')
            meme.paste(avatar, (250, 770), avatar)
            meme.save('media/tmp/meme_ava.png')
            with open('media/tmp/meme_ava.png', 'rb') as fp:
                await ctx.send(file=discord.File(fp, 'new_meme.png'))
            os.remove('media/tmp/meme_ava.png')
        else:
            await ctx.send('{} That is not a valid user senpai !'.format(ctx.message.author.mention))