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
            msg = msg.split('|')  # Split questions and choices
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
        emoji = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':ten:']
        content = 'Poll by ' + author.mention + ':\n'
        content += question + '\n'
        for i in range(len(choices)):
            content += emoji[i] + ' ' + choices[i].lstrip(' ') + '\n'  # strip to remove extra spaces at front/back
        poll = await self.bot.say(content)
        react = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣'] # unicode for emoji's 1-9
        for i in range(len(choices)):
            await self.bot.add_reaction(poll, react[i])

def setup(bot):
    bot.add_cog(Misc(bot))
