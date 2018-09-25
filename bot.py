#ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os

VERSION = '1.2.2'
extensions = ['admin', 'flake', 'misc']

bot = commands.Bot(command_prefix = '!', description = 'ScottBot Version: ' + VERSION, activity = discord.Game(name='Overcooked'))

@bot.event
async def on_ready():
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")

def changePrefix(newPrefix):
    bot = commands.Bot(command_prefix = newPrefix, description = 'ScottBot Version: ' + VERSION, activity = discord.Game(name='Overcooked'))

if (__name__ == '__main__'):
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('BOT_TOKEN', None))