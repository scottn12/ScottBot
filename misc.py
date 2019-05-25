# ScottBot by github.com/scottn12
# misc.py
# Contains all commands that work independently of other commands.

from discord.ext import commands
from discord import ServerRegion
from bot import VERSION, BUCKET_NAME, s3
from discord.utils import get
import smtplib
import os
import json
import random

class Misc:
    """Miscellaneous commands anyone can use."""
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')
 
    @commands.command(pass_context=True)
    async def help(self, ctx, *args: str):
        '''Shows this message.'''
        return await commands.bot._default_help_command(ctx, *args)

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
        FROM_EMAIL = os.environ.get('FROM_EMAIL')
        FROM_PSWD = os.environ.get('FROM_PSWD')
        TO_EMAIL = os.environ.get('TO_EMAIL')

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

    @commands.command(pass_context=False)
    async def source(self):
        """Link the source code for ScottBot."""
        await self.bot.say('https://github.com/scottn12/ScottBot')

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
            msg = msg.split('|')  # Split questions and choices
            question = msg[0]
            choices = msg[1:]
        except:
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): `!poll Question | Choice | Choice`')
            return
        #Check if number of choices is valid
        if (len(choices) < 2):
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): `!poll Question | Choice | Choice`')
            return
        if (len(choices) > 9):
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): `!poll Question | Choice | Choice`')
            return

        # Try to delete original message
        try:
            await self.bot.delete_message(ctx.message)
        except:
            print('need admin D:')

        # Print and React
        author = ctx.message.author
        emoji = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':ten:']
        content = 'Poll by ' + author.mention + ':\n'
        content += question + '\n'
        for i in range(len(choices)):
            content += emoji[i] + ' ' + choices[i].lstrip(' ') + '\n'  # strip to remove extra spaces at front/back
        poll = await self.bot.say(content)
        react = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣'] # unicode for emoji's 1-9
        for i in range(len(choices)):
            await self.bot.add_reaction(poll, react[i])

    @commands.command(pass_context=True)
    async def rng(self, ctx):
        """ScottBot randomly picks one of the arguments. Coin flip if no arguments given."""
        content = ctx.message.content[5:]
        if not content:
            num = random.randint(0,1)
            if num == 0:
                await self.bot.say('Heads!')
            else:
                await self.bot.say('Tails!')
        else:
            args = content.split()
            await self.bot.say(args[random.randint(0, len(args)-1)])

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx):
        """Clears all messages in the text channel (ADMIN)."""
        test_msg = await self.bot.say("Are you sure you want to permanently clear all the messages from this channel? Type 'Y' to confirm.")
        if not await self.confirmAction(ctx):
            await self.bot.say('Clear aborted.')
            return

        # Test for permissions
        try:
            await self.bot.delete_message(test_msg)
        except:
            await self.bot.say('Error! ScottBot needs permissions to do this!')
            return

        # Delete
        async for message in self.bot.logs_from(ctx.message.channel):
            await self.bot.delete_message(message)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def streamPing(self, ctx):
        """Allows ScottBot alerts when someone starts streaming (ADMIN)."""
        # Find role desired (if any)
        content = ctx.message.content[12:]
        role = None  # Default None if no role provided
        roleID = None
        if content == 'everyone':
            await self.bot.say('Error! `everyone` is not a valid role. To have ScottBot announce when every user goes live, simply use `!streamPing` alone.')
            return
        elif content != '':
            role = get(ctx.message.server.roles, name=content)
            if not role:  # Check mentioned roles if any
                roles = ctx.message.role_mentions
                if not roles:
                    await self.bot.say(f'Error! `{content}` is not a valid role!')
                    return
                if len(roles) > 1:
                    await self.bot.say('Error! Only one role is allowed.')
                    return
                role = roles[0]
                roleID = role.id
            else:
                if role.is_everyone:
                    await self.bot.say('Error! `everyone` is not a valid role. To have ScottBot announce when every user goes live, simply use `!streamPing` alone.')
                    return
                roleID = role.id

        with open('data/streams.json', 'r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id
        channelID = ctx.message.channel.id
        enable = True
        if serverID in data:  # Check if server is registered yet
            if 'streamChannelID' in data[serverID]:  # Check if stream is registered yet
                if data[serverID]['streamChannelID'] == channelID and data[serverID]['streamRoleID'] == roleID:  # Same info -> disable stream ping
                    data[serverID]['streamChannelID'] = None
                    data[serverID]['streamRoleID'] = None
                    enable = False
                else:  # Enable
                    data[serverID]['streamChannelID'] = channelID
                    data[serverID]['streamRoleID'] = roleID
            else:
                data[serverID]['streamChannelID'] = channelID
                data[serverID]['streamRoleID'] = roleID
        else:  # Register server w/ new data
            data[serverID] = {
                "streamChannelID": channelID,
                "streamRoleID": roleID
            }
        msg = ''
        if enable and roleID:
            msg += f'StreamPing enabled for members of `{role}`!'
        elif enable and not roleID:
            msg += f'StreamPing enabled for **ALL USERS**! Use `!streamPing "RoleName"` to __only__ ping members of that specific role.'
        else:
            msg += 'StreamPing disabled!'
        await self.bot.say(msg)

        # Update JSON
        with open('data/streams.json', 'w') as f:  # Update JSON
            json.dump(data, f, indent=2)
        s3.upload_file('data/streams.json', BUCKET_NAME, 'streams.json')

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def region(self, ctx, arg=None):
        """Change server region. Swaps between US East and US Central if none is provided."""

        curr = ctx.message.server.region
        if not arg:
            if curr == ServerRegion.us_east:
                await self.bot.edit_server(ctx.message.server, region=ServerRegion.us_central)
                await self.bot.say('The region has been changed to `us-central`.')
            else:
                await self.bot.edit_server(ctx.message.server, region=ServerRegion.us_east)
                await self.bot.say('The region has been changed to `us-east`.')
            return

        if arg.lower() == 'east':
            arg = ServerRegion.us_east
        elif arg.lower() == 'central':
            arg = ServerRegion.us_central
        elif arg.lower() == 'south':
            arg = ServerRegion.us_south
        elif arg.lower() == 'west':
            arg = ServerRegion.us_west

        try:
            newRegion = ServerRegion(arg)
            if newRegion == curr:
                await self.bot.say(f'The region is already `{newRegion}`.')
            else:
                await self.bot.edit_server(ctx.message.server, region=newRegion)
                await self.bot.say(f'The region has been changed to `{newRegion}`.')
        except ValueError:
            await self.bot.say('Invalid Region.')

    # Prompts the user to confirm an action and returns true/false
    async def confirmAction(self, ctx):
        msg = await self.bot.wait_for_message(timeout=10, author=ctx.message.author)
        if not msg or msg.content.lower() != 'y':
            return False
        return True

def setup(bot):
    bot.add_cog(Misc(bot))
