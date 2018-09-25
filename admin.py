import discord
from discord.ext import commands

class Admin:
    '''Commands for server administrators only.'''
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def clearAll(self, ctx):
        '''Clears all messages in the text channel.'''
        if (not await self.isAdmin(ctx)):
            await self.bot.say('Only admins may use !clear.')
            return

        await self.bot.say("Are you sure you want to permanently clear all the messages from this channel? Type 'Y' to confirm.")
        if (not await self.confirmAction(ctx)):
            await self.bot.say('Clear aborted.')
            return

        # Delete
        messages = []
        async for message in self.bot.logs_from(ctx.message.channel):
            messages.append(message)
        if len(messages) > 1:
            await self.bot.delete_messages(messages)

        # For messages older than 14 days
        async for message in self.bot.logs_from(ctx.message.channel):
            await self.bot.delete_message(message)

    @commands.command(pass_context=True)
    async def changePrefix(self, ctx):
        if (not await self.isAdmin(ctx)):
            await self.bot.say('Only admins may use !changePrefix.')
            return
        from bot import changePrefix
        import string
        '''Changes the prefix for ScottBot commands.'''
        newPrefix = ctx.message.content[14:]
        if (newPrefix in string.punctuation):
            changePrefix(newPrefix)
            await self.bot.say('Prefix successfully changed!')
        else:
            await self.bot.say('Invalid prefix. New prefix must be a single punctuation character.')

    @commands.command(pass_context=True)
    async def flakeReset(self, ctx):
        '''Resets the flakeRank.'''
        if (not await self.isAdmin(ctx)):
            await self.bot.say('Only admins may use !flakeReset.')
            return

        await self.bot.say("Are you sure you want to permanently reset the flakeRank? Type 'Y' to confirm.")
        if (not await self.confirmAction(ctx)):
            await self.bot.say('Reset aborted.')
            return
        
        # Reset
        import sqlite3
        conn = sqlite3.connect('bot_database.db')
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS flake')
        c.close()
        conn.close()
        
    async def isAdmin(self, ctx):
        user = ctx.message.author
        permissions = user.permissions_in(ctx.message.channel)
        if not permissions.administrator:
            return False
        return True

    async def confirmAction(self, ctx):
        msg = await self.bot.wait_for_message(timeout=10, author=ctx.message.author)
        if (msg == None or msg.content.lower() != 'y'):
            return False
        return True

def setup(bot):
    bot.add_cog(Admin(bot))