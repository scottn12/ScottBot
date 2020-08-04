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
import asyncio
import random
import sqlite3

# Globals
VERSION = '3.0.2'
PREFIX = '!'
bot = commands.Bot(command_prefix=PREFIX, description=f'ScottBot Version: {VERSION}')
db = sqlite3.connect('data/bot_database.db')
cursor = db.cursor()
started = False

# Load all essential files
@bot.event
async def on_ready():
    global started
    if started:
        return
    started = True
    # Load Extensions
    extensions = ['flake', 'misc', 'roles', 'quotes', 'slippi', 'music']
    for extension in extensions:
        print('Loading ' + extension + '...')
        bot.load_extension(extension)

    await bot.change_presence(activity=discord.Game(name="Overcooked"))
    print(bot.user.name + ' Version ' + VERSION + " is ready!")
    if bot.user.name == 'ScottBot':  # Don't send message for TestBot
        await get(bot.get_all_members(), id=int(os.environ.get('SCOTT'))).send(f'ScottBot Version {VERSION} has been deployed!')

# Default Error Handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.message.channel.send('Permission Denied')
    elif isinstance(error, CommandNotFound):
        pass
    else:
        await ctx.message.channel.send(f'Unknown Error Occurred: ```{error}```')
        raise error

# Stream Ping
@bot.event
async def on_member_update(before, after):
    if (before.activity == None or before.activity.type != discord.ActivityType.streaming) and (after.activity != None and after.activity.type == discord.ActivityType.streaming):  # Before = Not Streaming, After = Streaming
        serverID = str(before.guild.id)
        with open('data/streams.json', 'r') as f: # Load streams JSON
            data = json.load(f)
        if serverID in data and 'streamChannelID' in data[serverID] and data[serverID]['streamChannelID']:  # Check if server/channelID is registered
            channelID = int(data[serverID]['streamChannelID'])
        else:
            return # don't ping if not enabled

        roleID = int(data[serverID]['streamRoleID'])  # Get roleID if one is set

        if roleID != None:
            role = discord.utils.get(before.guild.roles, id=roleID)
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
            msgStr = roleMention + after.mention + ' has just gone live at ' + after.activity.url + ' !'
            await bot.get_channel(channelID).send(msgStr)

        # Update cooldown time (7200 seconds = 2 hours)
        await asyncio.sleep(5)  # Wait until all pings are sent
        with open('data/streams.json', 'r') as f:  # Update loaded JSON in case any changes were made
            data = json.load(f)
            data[userID] = time.time() + 7200
        with open('data/streams.json', 'w') as f:  # Write
            json.dump(data, f, indent=2)

@bot.event
async def on_message(message):
    if 'league' in message.content.lower() and message.author != bot.user and message.guild and message.guild.id == int(os.environ.get('MAIN_SERVER')):
        emojis = ['😂', '🤣', '🤢', '🤒', '🤕', '😡', '👺', '😤', '🤧', '🙄', '👻', '😱', '👎', '💩', '😷', '😒', '😖', '😴', '💤', '🖕', '👶', '🙅', '💇', '🤦', '🙈', '💦', '🍑', '🍆', '🚨', '💀', '📉', '⚠', '☣', '💔', '🔫', '🗑', '🚽']
        for i in range(3):
            emoji = emojis.pop(random.randint(0, len(emojis) - 1))
            await message.add_reaction(emoji)
    if message.author.id == int(os.environ.get('SECRET_USER_1')):
        if 'corrupt' in message.content.lower():
            await message.author.send('Your message has been deleted as it has been marked as anti-Scott propaganda. Please refrain from speaking poorly upon the regime. And remember, ScottBot is always listening.')
            await message.delete()
            return
        if random.randint(0, 100) == 12:
            if random.randint(0, 1):
                await message.channel.send(':rage: *REEEEEEEEEE* YASUO :rage:')
            else:
                await message.channel.send(':rage: *REEEEEEEEEE* YONE :rage:')
    elif message.author.id == int(os.environ.get('SECRET_USER_2')):
        if random.randint(0, 100) == 12:
            await message.channel.send(':rage: *REEEEEEEEEE* APPLE :rage:')
    elif message.author.id == int(os.environ.get('KEVIN')):
        if random.randint(0, 100) == 12:
            await message.channel.send(':rage: *REEEEEEEEEE* ZYRA :rage:')

    await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(os.environ.get('BOT_TOKEN'))
