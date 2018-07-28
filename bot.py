#ScottBot by github.com/scottn12

import discord
from discord.ext import commands
import os

version = '1.1'
extensions = ['admin', 'flake', 'misc']

bot = commands.Bot(command_prefix = "!", description = 'ScottBot Version: ' + version)
for extension in extensions:
    bot.load_extension(extension)

@bot.event
async def on_ready():
    print(bot.user.name + ' Version: ' + version + " is ready!")

bot.run(os.environ.get('BOT_TOKEN', None))