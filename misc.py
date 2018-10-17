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
        self.countNum = 0                

    @commands.command(pass_context=True)
    async def role(self, ctx):
        '''Adds/Removes user to an allowed role.'''
        roles = ctx.message.role_mentions # Get mentioned roles
        roleStr = []
        try:
            s = ctx.message.content[6:]
            roleStr = s.split('"')
        except:
            await self.bot.say('Error! Use the following format: !role @role/"role"')
        if not roles and roleStr == None:
            await self.bot.say('No role(s) given! Use the following format: !role @role/"role"')
            return

        allowedRoles = []
        serverID = ctx.message.server.id

        # S3 Connection/JSON Update
        from boto3.session import Session
        import os
        ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID', None)
        ACCESS_SECRET_KEY = os.environ.get('ACCESS_SECRET_KEY', None)
        BUCKET_NAME = os.environ.get('BUCKET_NAME', None)
        REGION_NAME = os.environ.get('REGION_NAME', None)
        session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key= ACCESS_SECRET_KEY, region_name= REGION_NAME)
        s3 = session.client('s3')
        s3.download_file(BUCKET_NAME, 'serverData.json', 'data/serverData.json')

        import json
        with open('data/serverData.json','r') as f:
            data = json.load(f)
        
        noRoles = True
        for server in data['servers']:
            if serverID == server['serverID']: # Look for current server
                try:
                    allowedRoles = server['allowedRoles']
                    noRoles = False
                except:
                    await self.bot.say('No roles enabled!')
                    return
            if noRoles:
                await self.bot.say('No roles enabled!')
                return

        user = ctx.message.author

        for role in roles:
            if role.id in allowedRoles:
                if role in user.roles:
                    await self.bot.say('You have been removed from ' + role.name + '!')
                    await self.bot.remove_roles(user, role)
                else:
                    await self.bot.say('You have been added to ' + role.name + '!')
                    await self.bot.add_roles(user, role)
            else: 
                await self.bot.say('That role is not enabled to be used with !role.')
        
        serverRoles = ctx.message.server.roles
        
        for role in roleStr:
            noRole = True
            if role == '' or role == ' ' or role[0] == '<':
                continue
            for serverRole in serverRoles:
                if role == serverRole.name:
                    noRole = False
                    if serverRole.id in allowedRoles:
                        if serverRole in user.roles:
                            await self.bot.say('You have been removed from ' + serverRole.name + '!')
                            await self.bot.remove_roles(user, serverRole)
                        else:
                            await self.bot.say('You have been added to ' + serverRole.name + '!')
                            await self.bot.add_roles(user, serverRole)
                    else:
                        await self.bot.say('That role is not enabled to be used with !role.')
            if noRole:
                await self.bot.say(role + ' does not exist.')

    @commands.command(pass_context=True)
    async def help(self, ctx, *args: str):
        '''Shows this message.'''
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
        for message in messages:
            await self.bot.delete_message(message)

    @commands.command(pass_context=True)
    async def poll(self, ctx):
        '''Creates a poll: !poll "Question" Choices'''
        # Check for valid input and parse
        try:
            msg = ctx.message.content[6:]
            msg = msg.split('" "') #Split questions and choices
            msg[0] = msg[0].replace('"','') #Remove remaning quotations
            msg[-1] = msg[-1].replace('"','')
            question = msg[0]
            choices = msg[1:]
        except:
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): !poll "Question" "Choice" "Choice"')
            return
        #Check if number of choices is valid
        if (len(choices) < 2):
            await self.bot.say('Error! Too few choices (Min 2).')
            return
        if (len(choices) > 9):
            await self.bot.say('Error! Too many choices (Max 9).')
            return
        #Print and React
        poll = await self.bot.say(pollPrint(question, choices))
        emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣'] # unicode for emoji's 1-9
        for i in range(len(choices)):
            await self.bot.add_reaction(poll, emoji[i])

# Helper function to print message for !poll
def pollPrint(question: str, choices: list):
    emoji = [':one:',':two:',':three:',':four:',':five:',':six:',':seven:',':eight:',':nine:',':ten:']
    rtn = 'Poll:\n'
    rtn += question + '\n'
    for i in range(len(choices)):
        rtn += emoji[i] + ' ' + choices[i] + '\n'
    return rtn    

def setup(bot):
    bot.add_cog(Misc(bot))