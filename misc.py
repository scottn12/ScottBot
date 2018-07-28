import discord
from discord.ext import commands

class Misc:
    '''Miscellaneous commands anyone can use.'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=False)
    async def version(self):
        '''Displays current ScottBot version.'''
        #from bot import version
        await self.bot.say('ScottBot is running Version 1.1')

    @commands.command(pass_context=True)
    async def hello(self, ctx):
        '''ScottBot greets you.'''
        name = ctx.message.author.mention
        await self.bot.say("Hello {}!".format(name))

    

def setup(bot):
    bot.add_cog(Misc(bot))