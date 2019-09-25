# ScottBot by github.com/scottn12
# bot.py
# Contains all essential setup for ScottBot and non-command event handling.

import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure, CommandNotFound
from discord.utils import get
import os
import json
import time
import datetime
import asyncio
from fuzzywuzzy import fuzz
import random

# Globals
VERSION = '2.8.5.1'
PREFIX = '!'
bot = commands.Bot(command_prefix=PREFIX, description=f'ScottBot Version: {VERSION}')


# Randomly BEANS people
async def bean():
    while True:
        with open('data/bean.json', 'r') as f:
            data = json.load(f)
        hour = datetime.datetime.now().hour
        if data['servers'] and not (3 <= hour <= 9):  # Server(s) registered and the hour is not 3AM - 9AM
            for serverObj in data['servers']:  # Attempt to bean each registered server
                if random.randint(0, 1000) != 12:
                    continue
                serverID = list(serverObj.keys())[0]
                channelID = serverObj[serverID]['channel']
                server = get(bot.servers, id=serverID)
                if not server:  # Ensure ScottBot is still in the server
                    continue
                user = None
                while not user:  # Prevent ScottBot from getting beaned (that would just be embarrassing)
                    user = list(server.members)[random.randint(0, len(server.members) - 1)]
                    if user == bot.user:
                        user = None
                # Bean The User and add to beanCount
                if user.id in data['beanCount']:
                    data['beanCount'][user.id] += 1
                else:
                    data['beanCount'][user.id] = 1
                with open('data/bean.json', 'w') as f:
                    json.dump(data, f, indent=2)
                channel = get(bot.get_all_channels(), id=channelID)
                await bot.send_file(channel, 'assets/img/bean.png', content=user.mention)

        wait = random.randint(3600, 7200)  # Wait 1-2 hours for next bean attempt
        await asyncio.sleep(wait)

# Load all essential files
@bot.event
async def on_ready():
    # Load Cogs
    for extension in ['flake', 'misc', 'roles', 'quotes']:
        print('Loading ' + extension + '...')
        bot.load_extension(extension)

    await bot.change_presence(game=discord.Game(name='Overcooked'))
    print(bot.user.name + ' Version ' + VERSION + " is ready!")
    await bot.send_message(get(bot.get_all_members(), id=os.environ.get('SCOTT')), f'ScottBot Version {VERSION} has been deployed!')
    await bean()

# Default Error Handling
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, CheckFailure):
        await bot.send_message(ctx.message.channel, 'Permission Denied.')
    elif isinstance(error, CommandNotFound):
        pass
    else:
        await bot.send_message(ctx.message.channel, f'Unknown Error Occurred: ```{error}```')
        raise error

# Stream Ping
@bot.event
async def on_member_update(before, after):
    if (before.game == None or before.game.type != 1) and (after.game != None and after.game.type == 1):  # Before = Not Streaming, After = Streaming
        serverID = before.server.id
        with open('data/streams.json', 'r') as f: # Load streams JSON
            data = json.load(f)
        if serverID in data and 'streamChannelID' in data[serverID] and data[serverID]['streamChannelID']:  # Check if server/channelID is registered
            channelID = data[serverID]['streamChannelID']
        else:
            return # don't ping if not enabled

        roleID = data[serverID]['streamRoleID']  # Get roleID if one is set

        if roleID != None:
            role = discord.utils.get(before.server.roles, id=roleID)
            if role not in before.roles:  # If the streamer is not in the stream role then don't ping
                return
            roleMention = role.mention + ', '
        else:
            roleMention = ''

        # Load Current Streamers JSON
        with open('data/streams.json','r') as f:
            data = json.load(f)
        # Check Cooldown
        userID = before.id
        if userID in data:
            cooldownTime = data[userID]
        else:
            cooldownTime = -1  # First time streaming - no cooldown
        curr = time.time()
        if curr > cooldownTime:  # Cooldown expired - ping
            msgStr = roleMention + after.mention + ' has just gone live at ' + after.game.url + ' !'
            await bot.send_message(discord.Object(id=channelID), msgStr)

        # Update cooldown time (7200 seconds = 2 hours)
        await asyncio.sleep(5)  # Wait until all pings are sent
        with open('data/streams.json', 'r') as f:  # Update loaded JSON in case any changes were made
            data = json.load(f)
            data[userID] = time.time() + 7200
        with open('data/streams.json', 'w') as f:  # Write
            json.dump(data, f, indent=2)

@bot.event
async def on_message(message):
    if message.server and message.server.id == os.environ.get('MAIN_SERVER') and 'league' in message.content.lower():
        emojis = ['😂', '🤣', '🤢', '🤒', '🤕', '😡', '👺', '😤', '🤧', '🙄', '👻', '😱', '👎', '💩', '😷', '😒', '😖', '😴', '💤', '🖕', '👶', '🙅', '💇', '🤦', '🙈', '💦', '🍑', '🍆', '🚨', '💀', '📉', '⚠', '☣', '💔', '🔫', '🗑', '🚽']
        for i in range(3):
            emoji = emojis.pop(random.randint(0, len(emojis) - 1))
            await bot.add_reaction(message, emoji)
    if message.author.id == os.environ.get('SECRET_USER'):
        if 'corrupt' in message.content.lower():
            await bot.send_message(message.author, 'Your message has been deleted as it has been marked as anti-Scott propaganda. Please refrain from speaking poorly upon the regime. And remember, ScottBot is always listening.')
            await bot.delete_message(message)
            return
        words = message.content.lower().split()
        for word in words:
            ratio = fuzz.ratio(word, 'corrupt')
            if ratio > 50:
                await bot.send_message(message.channel, f'You know what\'s `{word}`? Enforcing a strict no alcohol policy, but drinking in your own room all the time.')
        if random.randint(0, 100) == 12:
            await bot.send_message(message.channel, ':rage: *REEEEEEEEEE* YASUO :rage:')
    await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(os.environ.get('BOT_TOKEN'))
