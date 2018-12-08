import discord
from discord.ext import commands
import sqlite3
import os
from boto3.session import Session
from bot import ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME, REGION_NAME, s3

class Flake:
    '''Commands for Flakers.'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def flake(self, ctx):
        '''Increments the flake count for all flakers mentioned.'''
        serverID = ctx.message.server.id
        createTable('Flake'+serverID)
        flakers = ctx.message.mentions
        for flaker in flakers:
            count = flakeIncrement(str(flaker), serverID)
            await self.bot.say(str(flaker) + ' has now flaked ' + count + ' times!')

    @commands.command(pass_context=True)
    async def flakeRank(self, ctx):
        '''Displays the flake standings.'''
        try:
            await self.bot.say(flakeRead(ctx.message.server.id))
        except:
            await self.bot.say('There are no flakers!')

# Setup Database  #NO LONGER NEEDED
def createTable(name):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS {}(Member TEXT PRIMARY KEY, Count INTEGER)'.format(name))
    c.close()
    conn.close()
    s3.upload_file('data/bot_database.db', BUCKET_NAME, 'bot_database.db')

# Incerment flaker count if exists, if not create
def flakeIncrement(member, serverID):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE flake'+serverID+' SET Count = Count + 1 WHERE member = ?', (member,))
    c.execute('INSERT OR IGNORE INTO flake'+serverID+' (Member, Count) VALUES (?, 1)', (member,))
    c.execute('SELECT Count FROM Flake'+serverID+' WHERE Member = ?', (member,))
    rtn = str(c.fetchone()[0])
    conn.commit()
    c.close()
    conn.close()

    s3.upload_file('data/bot_database.db', BUCKET_NAME, 'bot_database.db')

    return rtn

# Read from DB - output is a string formatted for discord text
def flakeRead(serverID):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    rtn = '```Flaker:\t\t\t\t\tCount:\n'
    c.execute('SELECT * FROM Flake'+serverID+' ORDER BY Count DESC')
    rows = c.fetchall()
    for row in rows:
        rtn += '{:<15}\t\t\t'.format(str(row[0]))
        rtn += str(row[1]) + '\n'
    c.close()
    conn.close()
    rtn +='```'
    return rtn

def setup(bot):
    bot.add_cog(Flake(bot))