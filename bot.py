#ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os

PREFIX = '!'
VERSION = '2.2'
extensions = ['admin', 'flake', 'misc']

# S3 Data
ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID', None)
ACCESS_SECRET_KEY = os.environ.get('ACCESS_SECRET_KEY', None)
BUCKET_NAME = os.environ.get('BUCKET_NAME', None)
REGION_NAME = os.environ.get('REGION_NAME', None)

bot = commands.Bot(command_prefix = PREFIX, description = 'ScottBot Version: ' + VERSION)

@bot.event
async def on_ready():
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")
    await bot.change_presence(game=discord.Game(name='Overcooked'))

@bot.event # Stream Ping
async def on_member_update(before, after):
    # Begin streaming
    if (before.game == None or before.game.type != 1) and (after.game != None and after.game.type == 1): # Before = Not Streaming, After = Streaming
        serverID = before.server.id

        # S3 Connection/JSON Update
        from boto3.session import Session
        import os
        ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID', None)
        ACCESS_SECRET_KEY = os.environ.get('ACCESS_SECRET_KEY', None)
        BUCKET_NAME = os.environ.get('BUCKET_NAME', None)
        REGION_NAME = os.environ.get('REGION_NAME', None)
        session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key= ACCESS_SECRET_KEY, region_name= REGION_NAME)
        s3 = session.client('s3')
        s3.download_file(BUCKET_NAME, 'serverData.json', 'data/serverData.json')

        import json
        with open('data/serverData.json','r') as f:
            data = json.load(f)
        
        for server in data['servers']:
            if serverID == server['serverID']: # Look for current server
                try:
                    channelID = server['streamChannelID'] # Try to find channelID, if none return
                except:
                    return
                if channelID == None: 
                    return
                roleID = server['streamRoleID']
                if roleID != None:
                    roleMention = discord.utils.get(before.server.roles, id=roleID).mention + ', '
                else:
                    roleMention = ''
                msgStr = roleMention + after.mention + ' has just gone live at ' + after.game.url + ' !'
                await bot.send_message(discord.Object(id=channelID), msgStr)

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('BOT_TOKEN', None))
