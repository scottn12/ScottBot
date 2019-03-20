from discord.ext import commands
import sqlite3
from bot import BUCKET_NAME, s3

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
            count = flakeIncrement(flaker.id, serverID)
            await self.bot.say(str(flaker) + ' has now flaked ' + count + ' times!')

    @commands.command(pass_context=True)
    async def flakeRank(self, ctx):
        '''Displays the flake standings.'''
        try:
            ids, counts = flakeRead(ctx.message.server.id)
        except:
            await self.bot.say('There are no flakers!')
            return
        msg = '```Flaker: \t\t\t\t\tCount:\n'
        for i in range(len(ids)):
            name = await self.bot.get_user_info(ids[i])
            msg += f'{str(name):24s}\t'
            msg += f'{counts[i]}\n'
        msg += '```'
        await self.bot.say(msg)

# Setup Database
def createTable(name):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS {}(ID TEXT PRIMARY KEY, Count INTEGER)'.format(name))
    c.close()
    conn.close()
    s3.upload_file('data/bot_database.db', BUCKET_NAME, 'bot_database.db')

# Incerment flaker count if exists, if not create
def flakeIncrement(ID, serverID):
    conn = sqlite3.connect('data/bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE Flake'+serverID+' SET Count = Count + 1 WHERE ID = ?', (ID,))
    c.execute('INSERT OR IGNORE INTO flake'+serverID+' (ID, Count) VALUES (?, 1)', (ID,))
    c.execute('SELECT Count FROM Flake'+serverID+' WHERE ID = ?', (ID,))
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
    ids = []
    counts = []
    c.execute('SELECT * FROM Flake'+serverID+' ORDER BY Count DESC')
    rows = c.fetchall()
    for row in rows:
        ids.append(row[0])
        counts.append(row[1])

        #IDs += '{:<15}\t\t\t'.format(str(row[0]))
        #rtn += str(row[1]) + '\n'
    c.close()
    conn.close()
    return (ids, counts)

def setup(bot):
    bot.add_cog(Flake(bot))