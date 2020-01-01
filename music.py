import asyncio
import functools
import itertools
import math
import random
import pprint
import discord
import youtube_dl
import globals
from async_timeout import timeout
from discord.ext import commands

# Silence bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def find_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)
        
        if data is None:
            globals.err = True
            globals.err_msg = "Couldn\'t find anything that matches `{}`".format(search)
            globals.last_cmd = "n!play {}".format(search)
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))
           
        return data['entries']


    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            globals.err = True
            globals.err_msg = "Couldn\'t fetch `{}`".format(search)
            globals.last_cmd = "n!play {}".format(search)
            raise YTDLError('Couldn\'t fetch `{}`'.format(search))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    globals.err = True
                    globals.err_msg = "Couldn\'t retrieve any matches for `{}`".format(search)
                    globals.last_cmd = "n!play {}".format(search)
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(search))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Views', value=self.source.views)
                 .add_field(name='Likes', value=self.source.likes)
                 .add_field(name='Dislikes', value=self.source.dislikes)
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed

class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

    def put_left(self, item : Song):
        self._queue.appendleft(item)


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx
        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self._loop = False
        self.skip_votes = set()
        self.audio_player = bot.loop.create_task(self.audio_player_task())
        self.first_init = True

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if self.first_init:
                try:
                    async with timeout(30):
                        self.current = await self.songs.get()
                        self.first_init = False
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            else:
                if self.loop:
                    source = await YTDLSource.create_source(self._ctx, self.current.source.url, loop=self.bot.loop)
                    song = Song(source)
                    self.songs.put_left(song)
                    self.current = await self.songs.get()
                else:
                    if not self.songs.empty():
                        self.current = await self.songs.get()
                    else:
                        await self._ctx.send("End of queue.")
                        self.bot.loop.create_task(self.stop())
                        return

            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        globals.err = True
        globals.err_msg = "An error occurred: {}".format(str(error))
        globals.last_cmd = str(ctx.message)
        await ctx.send('An error occurred: {}'.format(str(error)))
        await ctx.invoke(self._stop)

    @commands.command(name='join', invoke_without_subcommand=True)
    @commands.has_permissions(manage_guild=True)
    async def _join(self, ctx: commands.Context):
        """[Admin] Joins a voice channel"""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """[Admin] Clears the queue and leaves the voice channel"""

        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player from 0-100%"""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        if volume == -1:
            return await ctx.send('Current volume is {}%'.format(int(ctx.voice_state.current.source.volume * 100)))

        if volume < 0 or volume > 100:
            return await ctx.send('Volume must be between 0 and 100')
        else:
            ctx.voice_state.current.source.volume = volume / 100
            await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song"""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause') 
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context): 
        """Pauses the currently playing song"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.send("Current song paused.")

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song"""
    
        if ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.send("Current song resumed")
    

    @commands.command(name='stop')
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue"""

        ctx.voice_state.songs.clear()
        await ctx.invoke(self._leave)

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            ctx.voice_state.skip()
            if ctx.voice_state.songs.__len__() -1 == -1:
                await ctx.invoke(self._leave)

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
                if ctx.voice_state.songs.__len__() -1 == -1:
                    await ctx.invoke(self._leave)
            else:
                await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue

        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song

        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        
        if ctx.voice_state.loop:
            return await ctx.send('Looping song ```css\n{}\n```'.format(str(ctx.voice_state.current.source.title)))
        else:
            return await ctx.send('Unlooping song ```css\n{}\n```'.format(str(ctx.voice_state.current.source.title)))


    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song
        
        Can either find a song via its Youtube URL or its keywords
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        httpFlag = False

        if(search.__contains__("https://")):
            httpFlag = True
        else:
            search = "ytsearch10:" + search

        async with ctx.typing():
            try:
                if not httpFlag:
                    searchList = await YTDLSource.find_source(ctx, search, loop=self.bot.loop)
                else:
                    source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)

            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                await ctx.voice_state.stop()
                del self.voice_states[ctx.guild.id]
            else:
                if not httpFlag:
                    embed = (discord.Embed(title='These are the results I found:',
                                           color=discord.Color.blurple()))
                    i = 0
                    for entry in searchList:
                        if i == 5:
                            break
                        else:
                            try:
                                embed.add_field(name='Song #%d'%(i+1), value=str(entry['title']), inline=False)
                                i += 1
                            except KeyError:
                                pass

                    sent = await ctx.send(embed = embed) #creates a message object called "sent"

                    i = 0
                    reactionEmotes = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '❌']
                    for i in range(0,6):
                        await sent.add_reaction(reactionEmotes[i])
                    
                    def check(reaction, user):
                        if user == ctx.author:
                            if str(reaction.emoji) == '1️⃣' or str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣' or str(reaction.emoji) == '4️⃣' or str(reaction.emoji) == '5️⃣' or str(reaction.emoji) == '❌':
                                return True
                            else:
                                return False
                        else:
                            return False
                    
                    def convertToIdx(emote):
                        if str(emote) == '1️⃣':
                            return 0 
                        elif str(emote) == '2️⃣':
                            return 1 
                        elif str(emote) == '3️⃣':
                            return 2
                        elif str(emote) == '4️⃣':
                            return 3
                        elif str(emote) == '5️⃣':
                            return 4
                        elif str(emote) == '❌':
                            return -1
                        else:
                            return -2

                    try:
                        result = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                        opt = convertToIdx(result[0])
                        if opt < 0:
                            await sent.delete()
                            if ctx.voice_state.current == None:
                                await ctx.voice_state.stop()
                                del self.voice_states[ctx.guild.id]
                            if(opt == -2):
                                raise commands.CommandError('Invalid reaction!')

                    except asyncio.TimeoutError:
                        await ctx.voice_state.stop()
                        del self.voice_states[ctx.guild.id]
                    else:
                        if(opt >= 0):
                            await sent.delete()
                            urlPost = searchList[opt]['url']
                            ytURL = "https://www.youtube.com/watch?v=" + urlPost
                            source = await YTDLSource.create_source(ctx, ytURL, loop=self.bot.loop)
                            song = Song(source)
                            await ctx.voice_state.songs.put(song)
                            await ctx.send('Enqueued {}'.format(str(source)))

                else:
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send('Enqueued {}'.format(str(source)))
                    
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

