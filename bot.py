#ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os

PREFIX = '!'
VERSION = '1.3.2'
extensions = ['admin', 'flake', 'misc']

bot = commands.Bot(command_prefix = PREFIX, description = 'ScottBot Version: ' + VERSION, game = discord.Game(name='Overcooked'))

@bot.event
async def on_ready():
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")

@bot.event # Stream Ping
async def on_member_update(before, after):
    if (before.game == None or before.game.type != 1) and (after.game != None and after.game.type == 1): # Before = Not Streaming, After = Streaming
        serverID = before.server.id

        import json
        with open('data/streamData.json','r') as f:
            data = json.load(f)
        
        for server in data['servers']:
            if serverID == server['serverID']: # Look for current server
                channelID = server['channelID']
                roleID = server['roleID']
                if roleID != None:
                    roleMention = discord.utils.get(before.server.roles, id=roleID).mention + ', '
                else:
                    roleMention = ''
                msg = after.mention + ' has just gone live at ' + after.game.url + ' ' + roleMention
                await bot.send_message(discord.Object(id=channelID), msg)       
            
if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('BOT_TOKEN', None))