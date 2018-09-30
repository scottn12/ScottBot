#ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os

PREFIX = '!'
VERSION = '1.2.3'
extensions = ['admin', 'flake', 'misc']

bot = commands.Bot(command_prefix = PREFIX, description = 'ScottBot Version: ' + VERSION, game = discord.Game(name='Overcooked'))

@bot.event
async def on_ready():
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(os.environ.get('BOT_TOKEN', None))
