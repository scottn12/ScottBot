#ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os
from boto3.session import Session
import json

PREFIX = '!'
VERSION = '2.3.3'
extensions = ['admin', 'flake', 'misc']

# S3 Setup
ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID', None)
ACCESS_SECRET_KEY = os.environ.get('ACCESS_SECRET_KEY', None)
BUCKET_NAME = os.environ.get('BUCKET_NAME', None)
REGION_NAME = os.environ.get('REGION_NAME', None)
session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY, region_name=REGION_NAME)
s3 = session.client('s3')

bot = commands.Bot(command_prefix = PREFIX, description = 'ScottBot Version: ' + VERSION)

@bot.event
async def on_ready():
    # Load Files
    print('Loading JSON...')
    s3.download_file(BUCKET_NAME, 'serverData.json', 'data/serverData.json')
    print('Loading DB...')
    s3.download_file(BUCKET_NAME, 'bot_database.db', 'data/bot_database.db')
    print('Loading Requests...')
    s3.download_file(BUCKET_NAME, 'requests.txt', 'data/requests.txt')

    await bot.change_presence(game=discord.Game(name='Overcooked'))
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")

# Stream Ping
@bot.event 
async def on_member_update(before, after):
    # Begin streaming
    if (before.game == None or before.game.type != 1) and (after.game != None and after.game.type == 1): # Before = Not Streaming, After = Streaming

        # Check if before was league. This is due to the league client and league 
        # game being considered different games and causing the one of them to override
        # the streaming status. This would cause the bot to ping each time the user
        # switched between the client and game.
        if (before.game != None and before.game.name == 'League of Legends'): # Before = League
            print('IT HAPPENED')
            #return

        serverID = before.server.id

        # Load JSON
        with open('data/serverData.json','r') as f: 
            data = json.load(f)

        
        for server in data['servers']:
            if serverID == server['serverID']: # Check for current server

                # Try to find channelID, if none return (stream ping not enabled)
                try:
                    channelID = server['streamChannelID'] 
                except:
                    return
                if channelID == None: 
                    return
                
                roleID = server['streamRoleID'] # Get roleID if one is set

                if roleID != None:
                    role =  discord.utils.get(before.server.roles, id=roleID)
                    if role not in before.roles: # If the streamer is not in the stream role then don't ping
                        return
                    roleMention = role.mention + ', '
                else:
                    roleMention = ''

                msgStr = roleMention + after.mention + ' has just gone live at ' + after.game.url + ' !'
                await bot.send_message(discord.Object(id=channelID), msgStr)

if __name__ == '__main__':
    for extension in extensions:
        print('Loading ' + extension + '...')
        bot.load_extension(extension)
    bot.run(os.environ.get('BOT_TOKEN', None))