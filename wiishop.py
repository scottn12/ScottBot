# ScottBot by github.com/scottn12
# wiishop.py
# Contains all commands for the WII SHOP THEME!!!


from discord.ext import commands
import discord


class WiiShop(commands.Cog, name='WiiShop'):
    """Miscellaneous commands anyone can use."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def wiiShop(self, ctx):
        """do do do do do do do do do, do do do, do do do"""
        if not ctx.message.author.voice:
            await ctx.send('First connect to a voice channel to use `!wiiShop`.')
            return
        print('here')
        channel = ctx.message.author.voice.channel
        vc = None
        for voiceChannel in self.bot.voice_clients:
            if voiceChannel.channel == channel:
                vc = voiceChannel
                break
        if not vc:
            vc = await channel.connect()
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio('assets/audio/wii_shop.mp3'), after=lambda e: print('done'))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 0.07
        else:
            vc.stop()



def setup(bot):
    bot.add_cog(WiiShop(bot))
