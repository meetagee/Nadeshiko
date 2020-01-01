import discord
from discord.ext import commands
import time
import asyncio
from music import Music
from RNG import RNG
from meme import Meme
from wolfram import Wolfram
from fun import Fun
from steam import Steam
import globals

# Bot tokens 
token = "NjU3NTAwMzQ4NzIxOTIyMDQ5.XgP_jg.AU1-D7XY1tO8TG2SF9FUCDyqgdc"

# Bot initialization
bot = commands.Bot(command_prefix=commands.when_mentioned_or("n!"),
                   description="Ohaiyooooo! Need my help? (๑˃ᴗ˂)ﻭ")
@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

# Add Cog for bot's commands here
bot.add_cog(Music(bot))
bot.add_cog(RNG(bot))
bot.add_cog(Meme(bot))
bot.add_cog(Wolfram(bot))
bot.add_cog(Fun(bot))
bot.add_cog(Steam(bot))

# Helper function for logging
async def update_stats():
    globals.initialize()
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            if globals.err:
                with open("log/stats.txt", "a") as f:
                    f.write(
                        f"Time: {int(time.time())}, Command: {globals.last_cmd}, Error message: {globals.err_msg}\n")
                globals.err = False
            await asyncio.sleep(5)

        except Exception as e:
            print(e)
            await asyncio.sleep(5)

# Welcoming message
@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        welcome = 'Welcome {0.mention} to {1.name}'.format(member, guild)
        await guild.system_channel.send(welcome)

# Farewell message
@bot.event
async def on_member_remove(member):
    guild = member.guild
    if guild.system_channel is not None:
        farewell = '{0.mention} has left/ been removed from {1.name}. We wish you the very best.'.format(member, guild)
        await guild.system_channel.send(farewell)

# Run the Bot
bot.loop.create_task(update_stats())
bot.run(token)