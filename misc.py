import discord
from discord.ext import commands
from discord.utils import get
from bot import VERSION, BUCKET_NAME, s3
import json
import smtplib 
import os
import time
import random

class Misc:
    '''Miscellaneous commands anyone can use.'''
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')
 
    @commands.command(pass_context=True)
    async def help(self, ctx, *args: str):
        '''Shows this message.'''
        return await commands.bot._default_help_command(ctx, *args)

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
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id

        if serverID in data:  # Check if server is registered yet
            if 'quotes' in data[serverID]:  # Check if quotes are registered yet
                data[serverID]['quotes'].append(quote)
            else:  # add quote field
                data[serverID]['quotes'] = [quote]
        else:  # new server
            data[serverID] = {
                "quotes": [quote]
            }

        with open('data/serverData.json', 'w') as f:  # Update JSON
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
        if serverID in data and 'quotes' in data[serverID] and data[serverID][
            'quotes']:  # Check if server/quotes are registered
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
            rng = random.randint(0, len(quotes) - 1)
            await self.bot.say(quotes[rng])

    @commands.command(pass_context=True)
    async def role(self, ctx):
        '''Join/leave a role using !role @role/"role"'''
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
        
        if serverID in data and 'allowedRoles' in data[serverID] and data[serverID]['allowedRoles']:  # Check if server is registered / role data exists / role data not empty
            allowedRoles = data[serverID]['allowedRoles']
        else:  # No server/role data registered yet
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
        
        for role in roleStr:  # Evaluate quoted roles
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
    async def roles(self, ctx):
        '''Shows roles available to join/leave.'''
        # Get allowed roles (JSON)
        serverID = ctx.message.server.id
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)
        if serverID in data and 'allowedRoles' in data[serverID] and data[serverID]['allowedRoles']:  # Check if server is registered / role data exists / role data not empty
            allowedRoles = data[serverID]['allowedRoles']
        else:  # No server/role data registered yet
            await self.bot.say('No roles have been enabled to be used with !role. Use !allowRole to enable roles.')
            return

        for id in allowedRoles:
            role = get(ctx.message.server.roles, id=id)
            if not role:  # Role has been removed since last use
                allowedRoles.remove(id)
                data[serverID]['allowedRoles'] = allowedRoles
                with open('data/serverData.json', 'w') as f:
                    json.dump(data, f, indent=2)
                s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')

        user = ctx.message.author
        user_roles = user.roles
        emoji = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']
        react = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣'] # unicode for emoji's 1-9
        total_roles = len(allowedRoles)
        # Allowed roles can fit in one message
        TIMEOUT = 30
        if total_roles <= 9:
            content = f'Choose the role(s) you would like to join/leave (Active for {TIMEOUT} seconds):\n'
            for i in range(total_roles):
                role = get(ctx.message.server.roles, id=allowedRoles[i])
                content += f'{emoji[i]} '
                if role in user_roles:
                    content += 'Leave'
                else:
                    content += 'Join'
                content += f' `{role}`\n'
            msg = await self.bot.say(content)
            for i in range(total_roles):
                await self.bot.add_reaction(msg, react[i])
            start = time.time()
            while time.time() < start + TIMEOUT:
                reaction = await self.bot.wait_for_reaction(react[:total_roles], message=msg, timeout=TIMEOUT)
                if not reaction or reaction.user != user:
                    continue
                e = reaction.reaction.emoji
                role = get(ctx.message.server.roles, id=allowedRoles[react.index(e)])
                if role in user.roles:
                    await self.bot.remove_roles(user, role)
                    await self.bot.say(f'You have left `{role}`!')
                    content = content.replace(f'Leave `{role}`', f'Join `{role}`')
                    await self.bot.edit_message(msg, new_content=content)
                else:
                    await self.bot.add_roles(user, role)
                    await self.bot.say(f'You have joined `{role}`!')
                    content = content.replace(f'Join `{role}`', f'Leave `{role}`')
                    await self.bot.edit_message(msg, new_content=content)
            return

        # Over 9 Allowed Roles
        TIMEOUT = 90
        content = f'Choose the role(s) you would like to join/leave (Active for {TIMEOUT} seconds):\n'
        for i in range(9):
            role = get(ctx.message.server.roles, id=allowedRoles[i])
            content += f'{emoji[i]} '
            if role in user_roles:
                content += 'Leave'
            else:
                content += 'Join'
            content += f' `{role}`\n'
        msg = await self.bot.say(content)
        await self.bot.add_reaction(msg, u"\u25C0")
        for i in range(9):
            await self.bot.add_reaction(msg, react[i])
        await self.bot.add_reaction(msg, u"\u25B6")
        start = time.time()
        page = 0
        while time.time() < start + TIMEOUT:
            if page*9 + 8 >= total_roles:
                on_page = total_roles % 9
            else:
                on_page = 9
            all_emoji = react[:on_page] + [u"\u25C0", u"\u25B6"]
            reaction = await self.bot.wait_for_reaction(all_emoji, message=msg, timeout=TIMEOUT)
            if not reaction or reaction.user != user:
                continue
            e = reaction.reaction.emoji
            # Back
            if e == u"\u25C0":
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                count = 0
                content = f'Choose the role(s) you would like to join/leave (Active for {TIMEOUT} seconds):\n'
                for i in range(page*9, page*9+9):
                    role = get(ctx.message.server.roles, id=allowedRoles[i])
                    content += f'{emoji[count]} '
                    if role in user_roles:
                        content += 'Leave'
                    else:
                        content += 'Join'
                    content += f' `{role}`\n'
                    count += 1
                await self.bot.edit_message(msg, new_content=content)
                continue
            # Forward
            if e == u"\u25B6":
                if page*9 + 8 >= total_roles - 1:  # Already on the last page
                    continue
                page += 1
                count = 0
                if page * 9 + 8 >= total_roles:  # Already on the last page
                    end = page*9 + total_roles % 9
                else:
                    end = page*9 + 9
                content = 'Choose the role(s) you would like to join/leave (Active for {TIMEOUT} seconds):\n'
                for i in range(page*9, end):
                    role = get(ctx.message.server.roles, id=allowedRoles[i])
                    content += f'{emoji[count]} '
                    if role in user_roles:
                        content += 'Leave'
                    else:
                        content += 'Join'
                    content += f' `{role}`\n'
                    count += 1
                await self.bot.edit_message(msg, new_content=content)
                continue
            # Role Change
            role = get(ctx.message.server.roles, id=allowedRoles[react.index(e) + page*9])
            if role in user.roles:
                await self.bot.remove_roles(user, role)
                await self.bot.say(f'You have left `{role}`!')
                content = content.replace(f'Leave `{role}`', f'Join `{role}`')
                await self.bot.edit_message(msg, new_content=content)
            else:
                await self.bot.add_roles(user, role)
                await self.bot.say(f'You have joined `{role}`!')
                content = content.replace(f'Join `{role}`', f'Leave `{role}`')
                await self.bot.edit_message(msg, new_content=content)

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

    @commands.command(pass_context=True)
    async def poll(self, ctx):
        '''Creates a poll: !poll Question | Choice | Choice'''
        # Check for valid input and parse
        try:
            msg = ctx.message.content[6:]
            msg = msg.split('|')  # Split questions and choices\
            question = msg[0]
            choices = msg[1:]
        except:
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): !poll Question | Choice | Choice')
            return
        #Check if number of choices is valid
        if (len(choices) < 2):
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): !poll Question | Choice | Choice')
            return
        if (len(choices) > 9):
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): !poll Question | Choice | Choice')
            return

        # Try to delete original message
        try:
            await self.bot.delete_message(ctx.message)
        except:
            print('need admin D:')

        # Print and React
        author = ctx.message.author
        poll = await self.bot.say(pollPrint(question, choices, author))
        emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣'] # unicode for emoji's 1-9 
        for i in range(len(choices)):
            await self.bot.add_reaction(poll, emoji[i])

# Helper function to print message for !poll
def pollPrint(question: str, choices: list, author: discord.User):
    emoji = [':one:',':two:',':three:',':four:',':five:',':six:',':seven:',':eight:',':nine:',':ten:']
    rtn = 'Poll by ' + author.mention + ':\n'
    rtn += question + '\n'
    for i in range(len(choices)):
        rtn += emoji[i] + ' ' + choices[i].lstrip(' ') + '\n'  # strip to remove extra spaces at front/back
    return rtn    

def setup(bot):
    bot.add_cog(Misc(bot))
