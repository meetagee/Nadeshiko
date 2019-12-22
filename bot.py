import discord
import time
import asyncio

# Logging global vars
messages = joined = 0


# Bot & Server tokens initialization
client = discord.Client()
# TODO: figure out how to use dotenv
token = "NjU3NTAwMzQ4NzIxOTIyMDQ5.XfyxTg.QMwxYFUt9cMrKKHf7dhziDBY_14"
ID = 657500819565838336


# Event that responds to a new joining user
@client.event
async def on_member_join(member):
    global joined
    joined += 1
    for channel in member.guild.channels:
        if str(channel) == "general":
            await channel.send_message(f"""Welcome to the server {member.mention}""")


# Main event that responds to users' requests
@client.event
async def on_message(message):
    global messages
    messages += 1
    id = client.get_guild(ID)
    channels = ["commands"]  # Valid channels for commands (Optional)
    valid_users = ["Garu-#8359"]  # Valid users for commands (Optional)

    if str(message.channel) in channels and str(message.author) in valid_users:
        if message.content.find("n!hello") != -1:
            await message.channel.send("Helllloooooooo " + str(message.author.nick) + "-san~ (o´▽`o)ﾉ")
        elif message.content == "n!users":
            await message.channel.send(f"""# of Members: {id.member_count}""")
        elif message.content == "n!help":
            embed = discord.Embed(title="Help on BOT",
                                  description="Some useful commands")
            embed.add_field(name="n!hello", value="Greets the user")
            embed.add_field(name="n!users", value="Prints number of users")
            await message.channel.send(content=None, embed=embed)
        # Optional
        else:
            bad_words = ["nope", "naw", "789"]
            for word in bad_words:
                if message.content.count(word) > 0:
                    print("A bad word was said")
                    await message.channel.purge(limit=1)


# This event runs whenever a user updates: status, game playing, avatar, nickname or role
@client.event
async def on_member_update(before, after):
    n = after.nick
    if n:  # Check if they updated their username
        if n.lower().count("nunk") > 0:
            last = before.nick
            if last:  # If they had a username before change it back to that
                await after.edit(nick=last)
            else:  # Otherwise set it to "NAW"
                await after.edit(nick="NAW")


# Helper function for logging
async def update_stats():
    await client.wait_until_ready()
    global messages, joined

    while not client.is_closed():
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


# Runs the Bot
client.loop.create_task(update_stats())
client.run(token)
