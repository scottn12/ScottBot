# ScottBot by github.com/scottn12
# misc.py
# Contains all commands that work independently of other commands.

from discord.ext import commands
from discord import ServerRegion
from bot import VERSION
from discord.utils import get
import smtplib
import os
import json
import random
import time
import datetime

class Misc:
    """Miscellaneous commands anyone can use."""
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')
        self.hangmanChannels = []
 
    @commands.command(pass_context=True)
    async def help(self, ctx, *args: str):
        '''Shows this message.'''
        return await commands.bot._default_help_command(ctx, *args)

    @commands.command(pass_context=True)
    async def hangman(self, ctx):
        """Play hangman."""
        if ctx.message.channel in self.hangmanChannels:
            await self.bot.send_message(ctx.message.author, 'There is already a game in that channel! Please try again later.')
            return
        self.hangmanChannels.append(ctx.message.channel)
        await self.bot.send_message(ctx.message.author, 'Send your phrase here!')
        phrase = None
        while not phrase:
            msg = await self.bot.wait_for_message(timeout=60, author=ctx.message.author)
            if not msg:
                self.hangmanChannels.remove(ctx.message.channel)
                await self.bot.send_message(ctx.message.author, 'No phrase provided. Use `!hangman` in your server channel again to retry.')
                return
            if not msg.channel.is_private:
                continue
            phrase = msg.content
            if len(phrase) < 6:
                phrase = None
                await self.bot.send_message(ctx.message.author, 'Phrase must be at least 6 characters long. Enter a new phrase.')
                continue

            validWords = True
            for word in phrase.split():
                if not word.isalpha():
                    validWords = False
            if not validWords:
                phrase = None
                await self.bot.send_message(ctx.message.author, 'Phrases must contain ONLY letters. Enter a new phrase.')
                continue

        await self.bot.send_message(ctx.message.author, 'Success!')
        words = phrase.split()
        hiddenWords  = [''] * len(words)
        spacedWords  = [''] * len(words)
        for i in range(len(words)):
            spacedWords[i] = ' '.join([char for char in words[i]])
            hiddenWords[i] = '_ ' * len(words[i])
        spacedPhrase = '  '.join(spacedWords)
        hiddenPhrase = ' '.join(hiddenWords)
        start = 'Guessed:\n ___________\n |        |\n |\n |\n |\n |\n---'
        fails = 0
        guessed = ''
        await self.bot.say(f'Hangman game created by: **{ctx.message.author.name.replace(ctx.message.author.discriminator, "")}**\n```{start}\n{hiddenPhrase}```')
        timeout = 900
        while True:
            win = False
            lose = False
            msg = await self.bot.wait_for_message(timeout=timeout, channel=ctx.message.channel)
            timeout = 300
            if not msg:
                self.hangmanChannels.remove(ctx.message.channel)
                await self.bot.say(f'Hangman game created by: **{ctx.message.author.name.replace(ctx.message.author.discriminator, "")}**\n```{start}\n{spacedPhrase}```**Game expired due to inactivity.**')
                return
            if msg.author == ctx.message.author:
                continue
            guess = msg.content
            if guess.lower() == phrase.lower():
                await self.bot.say(f'Hangman game created by: **{ctx.message.author.name.replace(ctx.message.author.discriminator, "")}**\n```{start}\n{spacedPhrase}```**You Win!**')
                break
            if len(guess) != 1 or not guess.isalpha():
                continue
            if guess.upper() in guessed:
                reactions = ['😡', '💤', '😴', '🙃', '🤣', '🙄' ,'👺', '🖕', '🤢', '🤷', '🍆', '🍑', '💦', '👀', '🤔', '🚽', '😖', '😱', '💯', '🐸', '🔥', '🏳️‍🌈', '💔', '😉']
                await self.bot.add_reaction(msg, random.choice(reactions))
                continue
            if guessed == '':
                guessed = guess.upper()
            else:
                guessed += f', {guess.upper()}'
            if guess.lower() not in phrase.lower():
                fails += 1
            else:
                indices = [i for i, x in enumerate(spacedPhrase.lower()) if x == guess.lower()]
                for index in indices:
                    hiddenPhrase = hiddenPhrase[:index] + spacedPhrase[index] + hiddenPhrase[index + 1:]
                if hiddenPhrase.count('_') == 0:
                    win = True

            if fails == 0:
                start = f'Guessed: {guessed}\n ___________\n |        |\n |\n |\n |\n |\n---'
            elif fails == 1:
                start = f'\nGuessed: {guessed}\n ___________\n |        |\n |        O\n |\n |\n |\n---'
            elif fails == 2:
                start = f'\nGuessed: {guessed}\n ___________\n |        |\n |        O\n |        |\n |\n |\n---'
            elif fails == 3:
                start = f'Guessed: {guessed}\n ___________\n |        |\n |        O\n |       -|\n |\n |\n---'
            elif fails == 4:
                start = f'Guessed: {guessed}\n ___________\n |        |\n |        O\n |       -|-\n |\n |\n---'
            elif fails == 5:
                start = f'Guessed: {guessed}\n ___________\n |        |\n |        O\n |       -|-\n |       /\n |\n---'
            else:
                start = f'Guessed: {guessed}\n ___________\n ___________\n |        |\n |        O\n |       -|-\n |       / \\\n |\n---'
                lose = True

            if win:
                await self.bot.say(f'Hangman game created by: **{ctx.message.author.name.replace(ctx.message.author.discriminator, "")}**\n```{start}\n{hiddenPhrase}```**You Win!**')
                break
            elif lose:
                await self.bot.say(f'Hangman game created by: **{ctx.message.author.name.replace(ctx.message.author.discriminator, "")}**\n```{start}\n{spacedPhrase}```**You Lose!**')
                break
            else:
                await self.bot.say(f'Hangman game created by: **{ctx.message.author.name.replace(ctx.message.author.discriminator, "")}**\n```{start}\n{hiddenPhrase}```')

        self.hangmanChannels.remove(ctx.message.channel)

    @commands.command(pass_context=True)
    async def restart(self, ctx):
        """Restart and update ScottBot (Scott Only)."""
        if ctx.message.author.id == os.environ.get('SCOTT'):
            await self.bot.say('Restarting...')
            os.system('git pull origin develop')
            await self.bot.logout()
        else:
            await self.bot.say('Permission Denied.')

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
    async def ironman(self, ctx):
        """Creates a randomized SSBM ironman order."""
        chars = ['Mario', 'Bowser',	'Peach', 'Yoshi', 'Donkey Kong', 'Captain Falcon', 'Fox', 'Ness', 'Ice Climbers', 'Kirby', 'Samus',	'Zelda', 'Sheik', 'Link', 'Pikachu', 'Jigglypuff', 'Dr. Mario', 'Luigi', 'Ganondorf', 'Falco', 'Young Link', 'Pichu', 'Mewtwo', 'Mr. Game & Watch', 'Marth', 'Roy']
        msg = ''
        while chars:
            msg += chars.pop(random.randint(0, len(chars) - 1)) + '\n'
        await self.bot.send_message(ctx.message.author, msg)

    @commands.command(pass_context=True)
    async def poll(self, ctx):
        """Creates a poll: !poll Question | Choice | Choice"""
        # Check for valid input and parse
        try:
            msg = ctx.message.content[6:]
            msg = msg.split('|')  # Split questions and choices
            question = msg[0]
            choices = msg[1:]
        except:
            await self.bot.say('Error! Use the following format(Min 2, Max 9 Choices): `!poll Question | Choice | Choice`')
            return
        # Check if number of choices is valid
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
    async def bean(self, ctx):
        """Allows ScottBot to bean morons."""
        serverID = ctx.message.server.id
        with open('data/bean.json', 'r') as f:
            data = json.load(f)
        found = False
        for server in data['servers']:
            if list(server.keys())[0] == serverID:
                data['servers'].remove(server)
                await self.bot.say('This server will no longer get beaned.')
                found = True
        if not found:
            data['servers'].append({
                serverID: {
                    'channel': ctx.message.channel.id
                }
            })
            await self.bot.say('This server will now get BEANED in this channel!')
        with open('data/bean.json', 'w') as f:  # Update JSON
            json.dump(data, f, indent=2)

    @commands.command(pass_context=True)
    async def beanCount(self):
        """Checks how much people have been beaned."""
        with open('data/bean.json', 'r') as f:
            data = json.load(f)
        if not data['beanCount']:
            await self.bot.say('Nobody in this server has been beaned!')
            return
        users = []
        for userID in data['beanCount']:
            user = get(self.bot.get_all_members(), id=userID)
            if not user:  # Ensure user is in this server
                continue
            users.append({'name': user.name, 'count': data['beanCount'][userID]})
        sortedUsers = sorted(users, key=lambda k: k['count']).reverse()
        print(sortedUsers)

        # Display
        msg = f'```{"Victim:":15s}\tBeans:\n'
        for user in users:
            msg += f'{str(user["name"]):15s}\t'
            msg += f'{user["count"]}\n'
        msg += '```'
        await self.bot.say(msg)

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

    @commands.command(pass_context=True)
    async def powerUp(self, ctx):
        """Poggy Woggy"""

        pog = '<:ebenPog:593599153263869952> '
        wog = '<:ebenWog:602589822682398740> '
        checked = ':white_large_square: '
        unchecked = ':white_square_button: '
        arrow = ':arrow_right: '
        question = ':question: '
        n = 10

        words = ctx.message.content.split()
        if len(words) == 3:
            pog = words[1]
            wog = words[2]
            try:
                await self.bot.delete_message(ctx.message)
            except:
                pass
        elif len(words) != 1:
            await self.bot.say('You must `!powerUp` with two emoji\'s, or none for the default `!powerUp`.')
            return

        msg = await self.bot.say('`POWERING UP!!!`\n' + pog + unchecked * n + arrow + question)

        for i in range(n):
            time.sleep(.5)
            if i == n - 1:
                await self.bot.edit_message(msg, '`WAKANDA FOREVER!!!!!!!!!`\n' + pog + checked * n + arrow + wog)
            else:
                await self.bot.edit_message(msg, '`POWERING UP!!!`\n' + pog + checked * (i+1) + unchecked * (n-i-1) + arrow + question)

    @commands.command(pass_context=True)
    async def region(self, ctx, region=None):
        """Changes server region. Swaps between US East and US Central if none is provided."""

        curr = ctx.message.server.region
        if not region:
            if curr == ServerRegion.us_east:
                await self.bot.edit_server(ctx.message.server, region=ServerRegion.us_central)
                await self.bot.say('The region has been changed to `us-central`.')
            else:
                await self.bot.edit_server(ctx.message.server, region=ServerRegion.us_east)
                await self.bot.say('The region has been changed to `us-east`.')
            return

        if region.lower() == 'east':
            region = ServerRegion.us_east
        elif region.lower() == 'central':
            region = ServerRegion.us_central
        elif region.lower() == 'south':
            region = ServerRegion.us_south
        elif region.lower() == 'west':
            region = ServerRegion.us_west

        try:
            newRegion = ServerRegion(region)
            if newRegion == curr:
                await self.bot.say(f'The region is already `{newRegion}`.')
            else:
                await self.bot.edit_server(ctx.message.server, region=newRegion)
                await self.bot.say(f'The region has been changed to `{newRegion}`.')
        except ValueError:
            await self.bot.say('Invalid Region.')

    @commands.command(pass_context=True)
    async def kevin(self, ctx):
        """Get Kevin's Schedule for this week. !kevin {next (optional)}"""
        # Check if schedule needs rotation
        now = datetime.datetime.now()
        currentWeek = datetime.date(now.year, now.month, now.day).isocalendar()[1]
        nextWeek = currentWeek + 1
        if currentWeek == 52:
            nextWeek = 1
        newData = None
        with open('data/kevin.json', 'r') as f:
            data = json.load(f)
            if 'nextWeek' in data:
                jsonNextWeek = data['nextWeek']
                if jsonNextWeek == currentWeek:  # Time to rotate
                    newData = {}
                    newData['curr'] = data['next']
                    newData['currentWeek'] = currentWeek
                    newData['nextWeek'] = nextWeek
        if newData:
            with open('data/kevin.json', 'w') as f:
                json.dump(newData, f, indent=2)

        # Get current by default if no arguments given
        if len(ctx.message.content.split()) == 1:
            with open('data/kevin.json', 'r') as f:
                data = json.load(f)
                if 'curr' not in data:
                    await self.bot.say('No schedule currently saved.')
                    return
                msg = f'```Week of {(now - datetime.timedelta(days=now.isoweekday() % 7)).strftime("%m/%d/%Y")}:\n'
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                for i in range(7):
                    msg += f'{(days[i] + ":"):11s} {data["curr"][i]}\n'
                msg += '```'
                await self.bot.say(msg)

        # Check if Kevin is trying to set schedule
        elif ctx.message.author.id == os.environ.get('KEVIN') and len(ctx.message.content.split('|')) > 1:
            days = ctx.message.content.split('|')
            week = None
            if 'curr' in days[0].lower():
                week = 'curr'
            elif 'next' in days[0].lower():
                week = 'next'
            else:
                await self.bot.say('Error! No week specified. Enter in the format: `!kevin {current/next} | Sunday | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday`')
            if week and len(days) != 8:
                await self.bot.say('Error! Incorrect amount of days. Enter in the format: `!kevin {current/next} | Sunday | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday`')
            else:
                days = days[1:]  # Remove options entry
                with open('data/kevin.json', 'r') as f:
                    data = json.load(f)
                    data[week] = []
                    for day in days:
                        data[week].append(day.strip())
                with open('data/kevin.json', 'w') as f:
                    data['currentWeek'] = currentWeek
                    data['nextWeek'] = nextWeek
                    json.dump(data, f, indent=2)
                await self.bot.say('Schedule successfully saved!')

        # Get schedule
        else:
            week = 'curr'  # Default
            if 'next' in ctx.message.content.split()[1].lower():  # Next week requested
                week = 'next'
                now = now + datetime.timedelta(days=7)  # Go ahead 7 days
            with open('data/kevin.json', 'r') as f:
                data = json.load(f)
                if week not in data:
                    await self.bot.say('No schedule saved for next week.')
                    return
                msg = f'```Week of {(now - datetime.timedelta(days=now.isoweekday() % 7)).strftime("%m/%d/%Y")}:\n'
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                for i in range(7):
                    msg += f'{(days[i] + ":"):11s} {data[week][i]}\n'
                msg += '```'
                await self.bot.say(msg)

    # Prompts the user to confirm an action and returns true/false
    async def confirmAction(self, ctx):
        msg = await self.bot.wait_for_message(timeout=10, author=ctx.message.author)
        if not msg or msg.content.lower() != 'y':
            return False
        return True

def setup(bot):
    bot.add_cog(Misc(bot))
