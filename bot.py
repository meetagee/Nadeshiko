import discord
from discord.ext import commands
import time
import asyncio
from music import Music
from RNG import RNG
import globals

# Bot & Server tokens initialization
# TODO: figure out how to use dotenv
token = "NjU3NTAwMzQ4NzIxOTIyMDQ5.XfyxTg.QMwxYFUt9cMrKKHf7dhziDBY_14"

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
    globals.initialize()
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            with open("stats.txt", "a") as f:
                f.write(
                    f"Time: {int(time.time())}, Messages: {globals.messages}, Members Joined: {globals.joined}\n")

            globals.messages = 0
            globals.joined = 0

            await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)


# Run the Bot
bot.loop.create_task(update_stats())
bot.run(token)