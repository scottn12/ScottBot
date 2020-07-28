# ScottBot by github.com/scottn12
# wiishop.py
# Contains all commands for playing music or other sounds.
import asyncio

from discord.ext import commands
import discord
import json
import os
import datetime


class Music(commands.Cog, name='Music'):
    """Commands related to playing music and other sounds."""
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.musicCheck())
        self.queue = {}
        with open('data/audio.json', 'r') as f:
            self.cacheJSON = json.load(f)

    @commands.command(pass_context=True)
    async def play(self, ctx, src=None, loop=None):
        """Play audio with ScottBot."""
        data = self.cacheJSON
        if not src:
            if src == 'list':  # Display list of playable audio
                msg = 'No audio source specified.\n```\n'
                msg += '\n'.join(data)
                msg += '```Use `!play [source] [loop]` to play one of the above options, or use `!play list` to show this again.'
                await ctx.send(msg)
                return

            channel = ctx.message.author.voice.channel
            vc = None
            for voiceChannel in self.bot.voice_clients:
                if voiceChannel.guild == ctx.message.guild:
                    if voiceChannel.channel == channel:
                        vc = voiceChannel
                        break
            if vc and vc.is_paused():
                vc.resume()
            else:
                msg = 'No audio source specified.\n```\n'
                msg += '\n'.join(data)
                msg += '```Use `!play [source] [loop]` to play one of the above options, or use `!play list` to show this again.'
                await ctx.send(msg)

        elif src not in data:
            msg = f'Audio file `{src}` not found.\n```\n'
            msg += '\n'.join(data)
            msg += '```Use `!play [source] [loop]` to play one of the above options, or use `!play list` to show this again.'
            await ctx.send(msg)
        else:
            if not ctx.message.author.voice:
                await ctx.send('First connect to a voice channel to use `!wiiShop`.')
                return
            # Find VoiceChannel and check if its already connected
            channel = ctx.message.author.voice.channel
            vc = None
            for voiceChannel in self.bot.voice_clients:
                if voiceChannel.guild == ctx.message.guild:
                    if voiceChannel.channel == channel:
                        vc = voiceChannel
                        break
                    else:
                        await voiceChannel.disconnect()
                    break
            if not vc:
                vc = await channel.connect()
            if vc.is_playing():
                vc.stop()  # Stop current song
            vc.play(discord.FFmpegPCMAudio(f'assets/audio/{data[src]}'))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 0.07

    @commands.command(pass_context=True)
    async def stop(self, ctx):
        """Stops playing current audio."""
        if not ctx.message.author.voice:
            await ctx.send('You must be in a voice channel to use `!stop`.')
            return
        channel = ctx.message.author.voice.channel
        vc = None
        for voiceChannel in self.bot.voice_clients:
            if voiceChannel.channel == channel:
                vc = voiceChannel
                if vc.is_playing():
                    vc.stop()
                else:
                    await ctx.send('ScottBot is not currently playing.')
        if not vc:
            await ctx.send('ScottBot is not connected to any voice channel.')

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        """Pauses current audio."""
        if not ctx.message.author.voice:
            await ctx.send('You must be in a voice channel to use `!pause`.')
            return
        channel = ctx.message.author.voice.channel
        vc = None
        for voiceChannel in self.bot.voice_clients:
            if voiceChannel.channel == channel:
                vc = voiceChannel
                if vc.is_playing():
                    vc.pause()
                else:
                    await ctx.send('ScottBot is not currently playing.')
        if not vc:
            await ctx.send('ScottBot is not connected to any voice channel.')

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        """Skips to next audio source in queue."""
        if not ctx.message.author.voice:
            await ctx.send('You must be in a voice channel to use `!pause`.')
            return
        channel = ctx.message.author.voice.channel
        vc = None
        for voiceChannel in self.bot.voice_clients:
            if voiceChannel.channel == channel:
                vc = voiceChannel
                if vc.is_playing():
                    vc.pause()
                else:
                    await ctx.send('ScottBot is not currently playing.')
        if not vc:
            await ctx.send('ScottBot is not connected to any voice channel.')

    @commands.command(pass_context=True)
    async def uploadAudio(self, ctx, *names):
        """Uploads a audio file to be played."""

        attachments = ctx.message.attachments
        if not attachments:
            return await ctx.send('Error: No audio attachments.')
        if not names:
            return await ctx.send('Error: Name(s) not provided for audio file(s).')
        if len(names) != len(attachments):
            return await ctx.send(f'Error: {len(names)} name(s) provided, but {len(attachments)} file(s) provided. Please provided one name for each file.')

        for i in range(len(names)):
            name = names[i]
            attachment = attachments[i]
            if name in self.cacheJSON.keys():
                await ctx.send(f'File name `{name}` already used.')
            if not attachment.filename.endswith('.mp3'):
                await ctx.send(f'Invalid file format: `{attachment.filename}`. File must be of type `.mp3`.')
                continue
            # Make sure filename is unique
            filename = attachment.filename
            if os.path.isfile(f'./assets/audio/{attachment.filename}'):
                filename = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+ '_' + attachment.filename
            try:
                with open(f'assets/audio/{filename}', 'wb') as f:
                    content = await attachment.read()
                    f.write(content)
            except Exception as e:
                await ctx.send(f'Error saving file `{attachment.filename}`: ```{e}```')
                continue
            self.cacheJSON[name] = filename
            await ctx.send(f'{attachment.filename} has been successfully saved as `{name}`!')
        self.writeJSON()

    # Check if music is playing every minute - if not stop playing (wait 2 min if paused)
    async def musicCheck(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for vc in self.bot.voice_clients:
                if not vc.is_playing() or vc.channel.members == [self.bot.user]:  # Not playing or nobody listening
                    if vc.is_paused():
                        await asyncio.sleep(120)  # Wait another two minutes if it's paused
                        if vc.is_paused():
                            await vc.disconnect()
            await asyncio.sleep(60)

    # Update file with cached JSON
    def writeJSON(self):
        with open('data/audio.json', 'w') as f:  # Update JSON
            json.dump(self.cacheJSON, f, indent=2)


def setup(bot):
    bot.add_cog(Music(bot))
