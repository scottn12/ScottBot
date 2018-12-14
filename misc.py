import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
from bot import VERSION, ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME, REGION_NAME, s3
from boto3.session import Session
import json
import smtplib 
import os
import random

class Misc:
    '''Miscellaneous commands anyone can use.'''
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')
        self.bot.remove_command('clear') # remove?
 
    @commands.command(pass_context=True)
    async def help(self, ctx, *args: str):
        '''Shows this message.'''
        return await commands.bot._default_help_command(ctx, *args)

    @commands.command(pass_context=True)
    async def role(self, ctx):
        '''Adds/Removes user to an allowed role.'''
        if len(ctx.message.content) < 7:
            await self.bot.say('No role(s) given! Use the following format: !role @role/"role"')
            return
        else:
            roles = ctx.message.role_mentions # Get mentioned roles
            roleStr = []
            s = ctx.message.content[6:]
            roleStr = s.split('"')

        allowedRoles = []
        serverID = ctx.message.server.id
        
        # Get allowed roles (JSON)
        with open('data/serverData.json','r') as f:
            data = json.load(f)
        
        if serverID in data and 'allowedRoles' in data[serverID] and data[serverID]['allowedRoles']: # Check if server is registered / role data exists / role data not empty
            allowedRoles = data[serverID]['allowedRoles']
        else: # No server/role data registered yet
            await self.bot.say('No roles have been enabled to be used with !role. Use !allowRole to enable roles.')
            return

        user = ctx.message.author

        for role in roles: # Evaluate mentioned roles
            if role.id in allowedRoles:
                if role in (user.roles):
                    await self.bot.say('You have been removed from role "' + role.name + '"!')
                    try:
                        await self.bot.remove_roles(user, role)
                    except:
                        await self.bot.say('Error! Permission denied. Try checking ScottBot\'s permissions')
                        return
                else:
                    await self.bot.say('You have been added to role "' + role.name + '"!')
                    try:
                        await self.bot.add_roles(user, role)
                    except:
                        await self.bot.say('Error! Permission denied. Try checking ScottBot\'s permissions')
                        return
            else: 
                await self.bot.say('Error! Role: "' + role.name + '" is not enabled to be used with !role.')
        
        serverRoles = ctx.message.server.roles
        
        for role in roleStr: # Evaluate quoted roles
            found = False
            if role == '' or role == ' ' or role[0] == '<':
                continue
            for serverRole in serverRoles:
                if (role == serverRole.name):
                    found = True
                    if (serverRole.id in allowedRoles):
                        if (serverRole in user.roles):
                            await self.bot.say('You have been removed from role: "' + serverRole.name + '"!')
                            await self.bot.remove_roles(user, serverRole)
                        else:
                            await self.bot.say('You have been added to role: "' + serverRole.name + '"!')
                            await self.bot.add_roles(user, serverRole)
                    else:
                        await self.bot.say('Error! Role: "' + serverRole.name + '" is not enabled to be used with !role.')
            if not found:
                await self.bot.say('Error! Role: "' + role + '" not found!')

    @commands.command(pass_context=True)
    async def request(self, ctx):
        '''Request a feature you would like added to ScottBot.'''
        msg = ctx.message.content[9:]
        if len(msg) == 0:
            await self.bot.say('Error! No request provided.')
            return

        # Append to file
        req = '\"{}\" - {}\n'.format(msg, ctx.message.author.name)
        with open('data/requests.txt', 'a') as f:
            f.write(req)
        s3.upload_file('data/requests.txt', BUCKET_NAME, 'requests.txt')

        emailContent = 'Subject: New Feature Request for ScottBot\n\nUser: {}\nServer: {}\n\n{}'.format(str(ctx.message.author), str(ctx.message.server), msg)

        # GMail
        FROM_EMAIL = os.environ.get('FROM_EMAIL', None)
        FROM_PSWD = os.environ.get('FROM_PSWD', None)
        TO_EMAIL = os.environ.get('TO_EMAIL', None)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(FROM_EMAIL, FROM_PSWD)
        s.sendmail(FROM_EMAIL, TO_EMAIL, emailContent)
        s.quit()
        
        await self.bot.say('Request sent!')
    
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
    async def addQuote(self, ctx):
        '''Adds a quote to the list of quotes.'''
        quote = ctx.message.content[10:]
        if len(quote) == 0:
            await self.bot.say('Error! No quote was provided.')
            return
        
        mentions = ctx.message.mentions
        if mentions:
            await self.bot.say('Error! You cannot mention someone in a quote.')
            return

        # Update JSON
        with open('data/serverData.json','r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id

        if serverID in data: # Check if server is registered yet 
            if 'quotes' in data[serverID]: # Check if quotes are registered yet
                data[serverID]['quotes'].append(quote)
            else: # add quote field
                data[serverID]['quotes'] = [quote]
        else: # new server
            data[serverID] = {
                "quotes" : [quote]
            } 

        with open('data/serverData.json', 'w') as f: # Update JSON
            json.dump(data, f, indent=2)
        
        s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')

        await self.bot.say('Quote added!')

    @commands.command(pass_context=True)
    async def quote(self, ctx, arg='1'):
        '''ScottBot says a random quote.'''
        MAX_QUOTES = 5
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)
        
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']: # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:  
            await self.bot.say('Error! No quotes have been added! Use !addQuote to add quotes.')
            return

        # Check if int was passed & num of quotes is not greater than max allowed
        try:
            arg = int(arg)
        except:
            arg = 1
        if arg > MAX_QUOTES:
            await self.bot.say('**Up to ' + str(MAX_QUOTES) + ' quotes are allowed at once.**')
            arg = MAX_QUOTES

        for _ in range(arg):
            rng = random.randint(0, len(quotes)-1)
            await self.bot.say(quotes[rng])

    @commands.command(pass_context=True)
    async def poll(self, ctx):
        '''Creates a poll: !poll "Question" "Choice" "Choice"'''
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
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): !poll "Question" "Choice" "Choice"')
            return
        if (len(choices) > 9):
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): !poll "Question" "Choice" "Choice"')
            return
        #Print and React
        author = ctx.message.author
        poll = await self.bot.say(pollPrint(question, choices, author))
        emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣'] # unicode for emoji's 1-9
        for i in range(len(choices)):
            await self.bot.add_reaction(poll, emoji[i])
        try:
            await self.bot.delete_message(ctx.message)
        except:
            print('need admin D:')  

# Helper function to print message for !poll
def pollPrint(question: str, choices: list, author: discord.User):
    emoji = [':one:',':two:',':three:',':four:',':five:',':six:',':seven:',':eight:',':nine:',':ten:']
    rtn = 'Poll by ' + author.mention + ':\n'
    rtn += question + '\n'
    for i in range(len(choices)):
        rtn += emoji[i] + ' ' + choices[i] + '\n'
    return rtn    

def setup(bot):
    bot.add_cog(Misc(bot))
