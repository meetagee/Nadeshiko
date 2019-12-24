import discord
from discord.ext import commands
import time
import asyncio
from music import Music
from RNG import RNG

# Logging global vars
messages = joined = 0


# Bot & Server tokens initialization
# TODO: figure out how to use dotenv
token = "NjU3NTAwMzQ4NzIxOTIyMDQ5.XfyxTg.QMwxYFUt9cMrKKHf7dhziDBY_14"
ID = 657500819565838336


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

# Helper function for logging
async def update_stats():
    await bot.wait_until_ready()
    global messages, joined

    while not bot.is_closed():
        try:
            with open("stats.txt", "a") as f:
                f.write(
                    f"Time: {int(time.time())}, Messages: {messages}, Members Joined: {joined}\n")

            messages = 0
            joined = 0

            await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)


# Run the Bot
bot.loop.create_task(update_stats())
bot.run(token)