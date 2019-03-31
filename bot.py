# ScottBot by github.com/scottn12
# bot.py
# Contains all essential setup for ScottBot and non-command event handling.

import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure, CommandNotFound
import os
from boto3.session import Session
import json
import time
import asyncio

# Globals
VERSION = '2.7.1'
PREFIX = '!'
bot = commands.Bot(command_prefix=PREFIX, description=f'ScottBot Version: {VERSION}')

# S3 Setup
ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID')
ACCESS_SECRET_KEY = os.environ.get('ACCESS_SECRET_KEY')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
REGION_NAME = os.environ.get('REGION_NAME')
session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY, region_name=REGION_NAME)
s3 = session.client('s3')

# Download Files
@bot.event
async def on_ready():
    # Load Files
    files = ['quotes.json', 'roles.json', 'streams.json', 'bot_database.db', 'requests.txt']
    for file in files:
        print(f'Loading {file}...')
        s3.download_file(BUCKET_NAME, file, f'data/{file}')

    # Load Cogs
    for extension in ['flake', 'misc', 'roles', 'quotes']:
        print('Loading ' + extension + '...')
        bot.load_extension(extension)

    await bot.change_presence(game=discord.Game(name='Overcooked'))
    print(bot.user.name + ' Version ' + VERSION + " is ready!")

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
    if (before.game == None or before.game.type != 1) and (after.game != None and after.game.type == 1): # Before = Not Streaming, After = Streaming
        serverID = before.server.id
        with open('data/streams.json', 'r') as f: # Load streams JSON
            data = json.load(f)
        if serverID in data and 'streamChannelID' in data[serverID] and data[serverID]['streamChannelID']: # Check if server/channelID is registered
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
        await asyncio.sleep(5)
        with open('data/streams.json', 'r+') as f:  # Load streams JSON
            data = json.load(f)
            data[userID] = time.time() + 7200
            json.dump(data, f, indent=2)
        s3.upload_file('data/streams.json', BUCKET_NAME, 'streams.json')

if __name__ == '__main__':
    bot.run(os.environ.get('BOT_TOKEN'))
