import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio

from bot import VERSION

class Misc:
    '''Miscellaneous commands anyone can use.'''
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(pass_context=True)
    async def help(self, ctx, *args: str):
        """Shows this message."""
        return await commands.bot._default_help_command(ctx, *args)
    
    @commands.command(pass_context=False)
    async def version(self):
        '''Prints ScottBot Version.'''
        await self.bot.say('ScottBot is running Version: ' + VERSION)

    @commands.command(pass_context=True)
    async def hello(self, ctx):
        '''ScottBot greets you.'''
        name = ctx.message.author.mention
        await self.bot.say("Hello {}!".format(name))

    @commands.command(pass_context=False)
    async def nanoDankster(self):
        '''A sad story.'''
        scott = '<@170388931949494272>'
        msg = 'On 7/28/18, ' + scott + ' accidentally erased his work on ScottBot. At approximately 5AM he restored his work and uploaded the new version to GitHub. '
        msg += 'Unfortunately, ' + scott + ' is stupid and forgot to hide ScottBot\'s token in the source code. '
        msg += 'This allowed mallicious bot NanoDankster to take control of the ScottBot, erasing everything from the server. Don\'t be like ' + scott + '.'
        await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def clear(self, ctx):
        '''Deletes all commands and messages from ScottBot.'''
        messages = []
        async for message in self.bot.logs_from(ctx.message.channel):
            if (message.author == self.bot.user or message.content[0] == '!'):
                messages.append(message)
                print(message.content)
        if len(messages) > 1:
            await self.bot.delete_messages(messages)

        # For messages older than 14 days
        async for message in messages:
            await self.bot.delete_message(message)

    @commands.command(pass_context=True)
    async def poll(self, ctx):
        '''Creates a poll: !poll "Question" Choices'''
        # Check for valid input and parse
        try:
            msg = ctx.message.content.split('"')
        except: 
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): !poll "Question" Choice Choice')
            return
        question = msg[1]
        choices = msg[-1].split()
        if (len(choices) < 2):
            await self.bot.say('Error! Too few choices (Min 2).')
            return
        if (len(choices) > 9):
            await self.bot.say('Error! Too many choices (Max 9).')
            return
        poll = await self.bot.say(pollPrint(question, choices))
        emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣'] # unicode for emoji's 1-9
        for i in range(len(choices)):
            await self.bot.add_reaction(poll, emoji[i])

# Helper function to print message for !poll
def pollPrint(question: str, choices: list):
    emoji = [':one:',':two:',':three:',':four:',':five:',':six:',':seven:',':eight:',':nine:',':ten:']
    rtn = 'Poll:\n'
    rtn += question + ' (React to vote)\n'
    for i in range(len(choices)):
        rtn += emoji[i] + ' ' + choices[i] + '\n'
    return rtn

def setup(bot):
    bot.add_cog(Misc(bot))