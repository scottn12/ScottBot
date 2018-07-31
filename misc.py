import discord
from discord.ext import commands
from discord.ext.commands import Bot

class Misc:
    '''Miscellaneous commands anyone can use.'''
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(pass_context=True)
    async def help(self, ctx, *args: str):
        """Shows this message."""
        return await commands.bot._default_help_command(ctx, *args)

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
        '''Creates poll using reactions. !poll "Question" Choices Time'''
        try:
            msg = ctx.message.content.split('"')
        except: 
            
            return
        question = msg[1]
        msg = msg[-1].split()
        try:
            int(msg[-1])
        except:
            await self.bot.say('Error! Use the following format(Min 2, Max 10 Choices): !poll "Question" Choice Choice Time(Minutes)')
            return
        if (len(msg) < 3):
            await self.bot.say('Error! Use the following format(Min 2, Max 10 Choices): !poll "Question" Choice Choice Time(Minutes)')
            return
        if (len(msg) > 11):
            await self.bot.say('Error! Too many choices (Max 10).')
        time = int(msg[-1])
        del msg[-1] # Remove time
        choices = []
        for choice in msg:
            choices.append(choice)
        await self.bot.say(pollPrint(question, choices))
        poll = self.bot.logs_from(ctx.message.channel, 1)
        im sleepy

def pollPrint(question: str, choices: list):
    emoji = [':one:',':two:',':three:',':four:',':five:',':six:',':seven:',':eight:',':nine:',':ten:']
    rtn = question + ' (React to vote)\n'
    for i in range(len(choices)):
        rtn += emoji[i] + ' ' + choices[i] + '\n'
    return rtn




def setup(bot):
    bot.add_cog(Misc(bot))