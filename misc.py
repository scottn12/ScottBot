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

    @commands.command(pass_context=True)
    async def clear(self, ctx):
        '''Deletes all commands and messages sent from ScottBot.'''

        messages = []
        async for message in self.bot.logs_from(ctx.message.channel):
            if (ctx.message.author == self.bot.user or ctx.message.content[0]=='!'):
                messages.append(message)
        if len(messages) > 1:
            await self.bot.delete_messages(messages)

        # For messages older than 14 days
        async for message in messages:
            await self.bot.delete_message(message)

def setup(bot):
    bot.add_cog(Misc(bot))