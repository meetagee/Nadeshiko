# Nadeshiko

Nadeshiko is a cute little Discord bot written in [Python](https://www.python.org "Python homepage") 3.6.9, using the [discord.py](https://github.com/Rapptz/discord.py) library. The bot's main purposes are to stream music from Youtube videos and do Wolfram Alpha queries so that online group work can be easy, enjoyable without having to switch between tabs from Discord to Internet browsers to do such stuffs.  

fyi: Nadeshiko is based on a female anime character [Nadeshiko Kagamihara](https://yuru-camp.fandom.com/wiki/Nadeshiko_Kagamihara). She is cute and happy and she can be your perfect studying partner (aka your 2D waifu) ٩(｡•́‿•̀｡)۶.

### Commands

In general, all commands can be shown in details through 1 simple command `n!help`. 

We implemented various Entertainment-related categories of commands such as Meme, RNG, Steam along with our 2 most important categories Music and Wolfram. To use any of them, input a command in the form `n!<One of the options below>`

1. Fun:
    - ava:       Gets and displays the mentioned user's avatar
    - fake:      Changes the bot's name and avatar to the same as the one mentioned
2. Meme:
    - memedog:   Replaces the dog's face with mentioned user's avatar
    - memestep:  Replaces the * with mentioned user's face
3. Music:
    - join:      Joins a voice channel
    - leave:     Clears the queue and leaves the voice channel
    - loop:      Loops the currently playing song
    - now:       Displays the currently playing song
    - pause:     Pauses the currently playing song
    - play:      Plays a song
    - queue:     Shows the player's queue
    - resume:    Resumes a currently paused song
    - skip:      Vote to skip a song. The requester can automatically skip.
    - stop:      Stops playing song and clears the queue
    - volume:    Sets the volume of the player from 0-100%
4. RNG:
    - choose:    Chooses one out of multiple inputs in form ______, ______, ______
    - quoteNgoc: Chooses a random quote that Ngoc once said
    - random:    Chooses a random number between 1 and the input number
5. Steam:
    - stat:      Displays Steam account's summary of a specific person from their steam ID
6. Wolfram:
    - graph:     Graphs a function
    - wolf:      Wolfram Alpha solver 
