#ScottBot
#http://discordpy.readthedocs.io/en/latest/api.html#server

import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import sqlite3
import os

# Bot Setup
bot = commands.Bot(command_prefix = "!")
client = discord.Client()
VERSION = '1.0'

commands = ['!hello','!clear','!flake']

# Database Setup
def createTable(name):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS {}(Member TEXT PRIMARY KEY, Count INTEGER)'.format(name))
    c.close()
    conn.close()

# Incerment flaker count if exists, if not create
def flakeIncrement(member):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE flake SET Count = Count + 1 WHERE member = ?', (member,))
    c.execute('INSERT OR IGNORE INTO flake (Member, Count) VALUES (?, 1)', (member,))
    c.execute('SELECT Count FROM Flake WHERE Member = ?', (member,))
    rtn = str(c.fetchone()[0])
    conn.commit()
    c.close()
    conn.close()
    return rtn

# Read from DB - output is a string formatted for discord text
def flakeRead():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    rtn = '```Flaker:\t\t\t\t\tCount:\n'
    c.execute('SELECT * FROM Flake ORDER BY Count DESC')
    rows = c.fetchall()
    for row in rows:
        rtn += '{:<25}\t\t\t'.format(str(row[0]))
        rtn += str(row[1]) + '\n'
    c.close()
    conn.close()
    rtn +='```'
    return rtn

# Startup - print to console
@bot.event
async def on_ready():
    print(bot.user.name + ' Version: ' + VERSION + " is ready!")

# !version - bot says version number
@bot.command(pass_context=False)
async def version():
    await bot.say('ScottBot is running Version ' + VERSION)

# !hello - bot greets @user
@bot.command(pass_context=True)
async def hello(ctx):
    name = ctx.message.author.mention
    await bot.say("Hello {}!".format(name))

# !clear - bot clears text channel after confirmation
@bot.command(pass_context=True)
async def clear(ctx):
    # Check Permissions
    user = ctx.message.author
    permissions = user.permissions_in(ctx.message.channel)
    if not permissions.administrator:
        await bot.say('Only admins may use !clear.')
        return

    # Confirm
    await bot.say("Are you sure you want to permanently clear all the messages from this channel? Type 'Y' to confirm.")
    msg = await bot.wait_for_message(timeout=10, author=user)
    if msg.content.lower() != 'y':
        await bot.say('Clear aborted.')
        return

    # Delete
    messages = []
    async for message in bot.logs_from(ctx.message.channel):
        messages.append(message)
    if len(messages) > 1:
        await bot.delete_messages(messages)

    # For messages older than 14 days
    async for message in bot.logs_from(ctx.message.channel):
        await bot.delete_message(message)


# !flake @name - increments and prints flake counter
@bot.command(pass_context=True)
async def flake(ctx):
    createTable('Flake')
    flakers = ctx.message.mentions
    for flaker in flakers:
        count = flakeIncrement(str(flaker))
        await bot.say(str(flaker) + ' has now flaked ' + count + ' times!')

# !flakeRank displays flake rankings in a table
@bot.command(pass_context=False)
async def flakeRank():
    try:
        await bot.say(flakeRead())
    except:
        await bot.say('There are no flakers!')

# !flakeReset
@bot.command(pass_context=True)
async def flakeReset(ctx):
    # Check Permissions
    user = ctx.message.author
    permissions = user.permissions_in(ctx.message.channel)
    if not permissions.administrator:
        await bot.say('Only admins may use !flakeReset.')
        return

    # Confirm
    await bot.say("Are you sure you want to permanently reset the flakeRank? Type 'Y' to confirm.")
    msg = await bot.wait_for_message(timeout=10, author=user)
    if msg.content.lower() != 'y':
        await bot.say('Reset aborted.')
        return

    # Reset
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS flake')
    c.close()
    conn.close()

    




bot.run(os.environ.get('BOT_TOKEN', None))
