import discord
from discord.ext import commands

class Admin:
    '''Commands for server administrators only.'''
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def allowRole(self, ctx):
        '''Allows users to add/remove themselves from roles.'''
        if (not await self.isAdmin(ctx)): # Check Admin
            await self.bot.say('Only admins may use !enableAddRole.')
            return

        roles = ctx.message.role_mentions # Get roles mentioned
        
        for role in roles: # Check if the role is an admin role 
            if role.permissions >= discord.Permissions.administrator:
                # error
                return

    @commands.command(pass_context=True)
    async def streamPing(self, ctx):
        '''Sets up ScottBot to alert a role(optional) when someone starts streaming.'''

        if (not await self.isAdmin(ctx)): #Check Admin
            await self.bot.say('Only admins may use !streamPing.')
            return

        roles = ctx.message.role_mentions #Get roles mentioned
        if len(roles) > 1:
            await self.bot.say('Error! Maximum of one role allowed.')
            return
        try:
            roleID = roles[0].id
            if roles[0].is_everyone:
                await self.bot.say('Error! The role cannot be @everyone.')
                return
        except:
            roleID = None

        # Update Stream Data
        import json
        with open('data/streamData.json','r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id
        channelID = ctx.message.channel.id

        newData = {
            "serverID": serverID,
            "channelID": channelID,
            "roleID": roleID,
        }
        
        newServer = True
        for server in data['servers']: 
            if serverID == server['serverID']: # Check if server is already registered and update if true
                server['channelID'] = channelID
                server['roleID'] = roleID
                newServer = False

        if newServer: # Add new Data
            data['servers'].append(newData)

        with open('data/streamData.json', 'w') as f: # Update JSON
            json.dump(data, f, indent=2)

        if roleID != None:
            await self.bot.say('Stream channel and role set!')
            return
        await self.bot.say('Stream channel set!')
    
    @commands.command(pass_context=True)
    async def disableStreamPing(self, ctx):
        '''Disables streaming alters for this server.'''

        if (not await self.isAdmin(ctx)): #Check Admin
            await self.bot.say('Only admins may use !disableStreamPing.')
            return

        import json
        with open('data/streamData.json','r') as f:
            data = json.load(f)
        
        serverID = ctx.message.server.id

        for server in data['servers']: 
            if serverID == server['serverID']: # Check if server is already registered and update if true
                server['channelID'] = None
                await self.bot.say('StreamPing has been disabled!')
                with open('data/streamData.json', 'w') as f: # Update JSON
                    json.dump(data, f, indent=2) 
                return
                
        await self.bot.say('StreamPing was already not enabled!')              

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
        import string
        '''Changes the prefix for ScottBot commands.'''
        newPrefix = ctx.message.content[14:]
        if (newPrefix in string.punctuation):
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
        conn = sqlite3.connect('data/bot_database.db')
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS flake'+ctx.message.server.id)
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