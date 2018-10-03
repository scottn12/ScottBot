import discord
from discord.ext import commands
import sqlite3

class Flake:
    '''Commands for Flakers.'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def flake(self, ctx):
        '''Increments the flake count for all flakers mentioned.'''
        serverName = ctx.message.server.name
        createTable('Flake'+serverName)
        flakers = ctx.message.mentions
        for flaker in flakers:
            count = flakeIncrement(str(flaker), serverName)
            await self.bot.say(str(flaker) + ' has now flaked ' + count + ' times!')

    @commands.command(pass_context=True)
    async def flakeRank(self, ctx):
        '''Displays the flake standings.'''
        try:
            await self.bot.say(flakeRead(ctx.message.server.name))
        except:
            await self.bot.say('There are no flakers!')

# Setup Database 
def createTable(name):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS {}(Member TEXT PRIMARY KEY, Count INTEGER)'.format(name))
    c.close()
    conn.close()

# Incerment flaker count if exists, if not create
def flakeIncrement(member, serverName):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE flake'+serverName+' SET Count = Count + 1 WHERE member = ?', (member,))
    c.execute('INSERT OR IGNORE INTO flake'+serverName+' (Member, Count) VALUES (?, 1)', (member,))
    c.execute('SELECT Count FROM Flake'+serverName+' WHERE Member = ?', (member,))
    rtn = str(c.fetchone()[0])
    conn.commit()
    c.close()
    conn.close()
    return rtn

# Read from DB - output is a string formatted for discord text
def flakeRead(serverName):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    rtn = '```Flaker:\t\t\t\t\tCount:\n'
    c.execute('SELECT * FROM Flake'+serverName+' ORDER BY Count DESC')
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