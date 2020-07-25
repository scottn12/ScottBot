# ScottBot by github.com/scottn12
# wiishop.py
# Contains all commands for playing music or other sounds.
import asyncio

from discord.ext import commands
import discord


class Music(commands.Cog, name='Music'):
    """Commands related to playing music and other sounds."""
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.musicCheck())

    @commands.command(pass_context=True)
    async def wiiShop(self, ctx):
        """do do do do do do do do do, do do do, do do do"""
        if not ctx.message.author.voice:
            await ctx.send('First connect to a voice channel to use `!wiiShop`.')
            return
        channel = ctx.message.author.voice.channel
        vc = None
        for voiceChannel in self.bot.voice_clients:
            if voiceChannel.channel == channel:
                vc = voiceChannel
                break
        if not vc:
            vc = await channel.connect()
        if vc.is_playing():
            vc.stop()  # Stop current song
        vc.play(discord.FFmpegPCMAudio('assets/audio/wii_shop.mp3'))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 0.07

    @commands.command(pass_context=True)
    async def mii(self, ctx):
        """miiiiiiiiiiiiiii"""
        if not ctx.message.author.voice:
            await ctx.send('First connect to a voice channel to use `!mii`.')
            return
        channel = ctx.message.author.voice.channel
        vc = None
        for voiceChannel in self.bot.voice_clients:
            if voiceChannel.channel == channel:
                vc = voiceChannel
                break
        if not vc:
            vc = await channel.connect()
        if vc.is_playing():
            vc.stop()  # Stop current song
        vc.play(discord.FFmpegPCMAudio('assets/audio/mii.mp3'))
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


    # Check if music is playing every minute - if not stop playing
    async def musicCheck(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for vc in self.bot.voice_clients:
                if not vc.is_playing() or vc.channel.members == [self.bot.user]:  # Not playing or nobody listening
                    await vc.disconnect()
            await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(Music(bot))
