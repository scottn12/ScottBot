#ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os

PREFIX = '!'
VERSION = '1.3'
extensions = ['admin', 'flake', 'misc']

bot = commands.Bot(command_prefix = PREFIX, description = 'ScottBot Version: ' + VERSION, game = discord.Game(name='Overcooked'))

@bot.event
async def on_ready():
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")

@bot.event
async def on_member_update(before, after):
    if (before.game == None or before.game.type != 1) and (after.game != None and after.game.type == 1):
        serverID = before.server.id
        channelID = '-1'
        import json
        with open('data/streamData.json','r') as f:
            data = json.load(f)
        for server in data['servers']:
            if serverID == server['serverID']:
                channelID = server['channelID']
        if channelID == '-1':
            return

        msg = after.mention 
        msg += ' has just gone live at ' 
        msg += after.game.url
        msg += ' !'
        await bot.send_message(discord.Object(id=channelID), msg)
            

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('BOT_TOKEN', None))