# ScottBot by github.com/scottn12
# quotes.py
# Contains all commands related to ScottBot's flake recording functionality.

from discord.ext import commands
from bot import db, cursor


class Flake:
    '''Commands for Flakers.'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def flakeReset(self, ctx):
        '''Resets the flakeRank (ADMIN).'''
        await self.bot.say("Are you sure you want to permanently reset the flakeRank? Type 'Y' to confirm.")
        if not await self.confirmAction(ctx):
            await self.bot.say('Reset aborted.')
            return

        cursor.execute('DROP TABLE IF EXISTS flake' + ctx.message.server.id)
        db.commit()

    @commands.command(pass_context=True)
    async def flake(self, ctx):
        '''Increments the flake count for all flakers mentioned.'''
        serverID = ctx.message.server.id
        self.createTable('Flake'+serverID)
        flakers = ctx.message.mentions
        for flaker in flakers:
            count = self.flakeIncrement(flaker.id, serverID)
            await self.bot.say(str(flaker.name) + ' has now flaked ' + count + ' times!')

    @commands.command(pass_context=True)
    async def flakeRank(self, ctx):
        '''Displays the flake standings.'''
        try:
            ids, counts = self.flakeRead(ctx.message.server.id)
        except:
            await self.bot.say('There are no flakers!')
            return
        msg = f'```{"Flaker:":15s}\tCount:\n'
        for i in range(len(ids)):
            user = await self.bot.get_user_info(ids[i])
            msg += f'{str(user.name):15s}\t'
            msg += f'{counts[i]}\n'
        msg += '```'
        await self.bot.say(msg)

    # Prompts the user to confirm an action and returns true/false
    async def confirmAction(self, ctx):
        msg = await self.bot.wait_for_message(timeout=10, author=ctx.message.author)
        if not msg or msg.content.lower() != 'y':
            return False
        return True

    # Setup Database
    def createTable(self, name):
        cursor.execute('CREATE TABLE IF NOT EXISTS {}(ID TEXT PRIMARY KEY, Count INTEGER)'.format(name))
        db.commit()

    # Increment flaker count if exists, if not create
    def flakeIncrement(self, ID, serverID):
        cursor.execute('UPDATE Flake'+serverID+' SET Count = Count + 1 WHERE ID = ?', (ID,))
        cursor.execute('INSERT OR IGNORE INTO flake'+serverID+' (ID, Count) VALUES (?, 1)', (ID,))
        cursor.execute('SELECT Count FROM Flake'+serverID+' WHERE ID = ?', (ID,))
        rtn = str(cursor.fetchone()[0])
        db.commit()
        return rtn

    # Read from DB - output is a string formatted for discord text
    def flakeRead(self, serverID):
        ids = []
        counts = []
        cursor.execute('SELECT * FROM Flake' + serverID + ' ORDER BY Count DESC')
        rows = cursor.fetchall()
        for row in rows:
            ids.append(row[0])
            counts.append(row[1])

        return ids, counts


def setup(bot):
    bot.add_cog(Flake(bot))
