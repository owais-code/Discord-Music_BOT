import asyncio
import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='?')

status = ['Kaise Hoga!', 'Aise Hoga!', 'Ho Gya!']

@client.event
async def on_ready():
    change_status.start()
    print('Seby is here!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `?help` command for details!')

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Ping!** Latency: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ['***grumble*** Bol bae', 'What is it!', 'Hello, how are you?', 'Hayeeeeeeee', '**Wasssuup!**']
    await ctx.send(choice(responses))

@client.command(name='die', help='This command returns a random last words')
async def die(ctx):
    responses = ['Rehen do phir', 'Bolo Zuban Kesari', 'Hips dont lie, I do']
    await ctx.send(choice(responses))

@client.command(name='credits', help='This command returns the credits')
async def credits(ctx):
    await ctx.send('Made by `Owais (Spidey), ofcourse u know him`')
    await ctx.send('Thanks to me for coming up with the idea')
    await ctx.send('Thanks to only me for helping me making this')

@client.command(name='creditz', help='This command returns the TRUE credits')
async def creditz(ctx):
    await ctx.send('**No one but me, lozer!**')

@client.command(name='play', help='This command plays music')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("Buddy, First connect to some voice channel then call me")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))

@client.command(name='stop', help='This command stops the music and makes the bot leave the voice channel')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@tasks.loop(seconds=3)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

client.run('Your Token')
