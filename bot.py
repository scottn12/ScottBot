# ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os
from boto3.session import Session
import json
import time

PREFIX = '!'
VERSION = '2.5.2'

# S3 Globals
ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID', None)
ACCESS_SECRET_KEY = os.environ.get('ACCESS_SECRET_KEY', None)
BUCKET_NAME = os.environ.get('BUCKET_NAME', None)
REGION_NAME = os.environ.get('REGION_NAME', None)
session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY, region_name=REGION_NAME)
s3 = session.client('s3')

bot = commands.Bot(command_prefix=PREFIX, description=f'ScottBot Version: {VERSION}')


@bot.event
async def on_ready():
    # Load Files
    print('Loading Server Data...')
    s3.download_file(BUCKET_NAME, 'serverData.json', 'data/serverData.json')
    print('Loading Streams...')
    s3.download_file(BUCKET_NAME, 'streams.json', 'data/streams.json')
    print('Loading DB...')
    s3.download_file(BUCKET_NAME, 'bot_database.db', 'data/bot_database.db')
    print('Loading Requests...')
    s3.download_file(BUCKET_NAME, 'requests.txt', 'data/requests.txt')

    await bot.change_presence(game=discord.Game(name='Overcooked'))
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")


@bot.event
async def on_member_update(before, after): # Stream Ping
    if (before.game == None or before.game.type != 1) and (after.game != None and after.game.type == 1): # Before = Not Streaming, After = Streaming
        serverID = before.server.id
        with open('data/serverData.json','r') as f: # Load server data JSON
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
            print('PING')
        else:
            print('ON COOLDOWN')
            print('current\t\t\tcooldown\t\tdelta')
            print(str(curr)+'\t'+str(cooldownTime) + '\t' + str(cooldownTime-curr))

        # Update cooldown time (7200 seconds = 2 hours)
        time.sleep(1)
        data[userID] = time.time() + 7200
        with open('data/streams.json', 'w') as f:  # Update Streams JSON
            json.dump(data, f, indent=2)
        s3.upload_file('data/streams.json', BUCKET_NAME, 'streams.json')
        print('done!')

if __name__ == '__main__':
    for extension in ['admin', 'flake', 'misc']:
        print('Loading ' + extension + '...')
        bot.load_extension(extension)
    bot.run(os.environ.get('BOT_TOKEN', None))
