from discord.ext import commands
from bot import BUCKET_NAME, s3
import json

class Admin:
    '''Commands for server administrators only.'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def streamPing(self, ctx):
        '''Allows ScottBot alerts when someone starts streaming.'''

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
                await self.bot.say('Error! The role cannot be "everyone".')
                return
        except:
            roleID = None

        with open('data/serverData.json','r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id
        channelID = ctx.message.channel.id

        if serverID in data: # Check if server is registered yet 
            if 'streamChannelID' in data[serverID]: # Check if stream is registered yet
                if data[serverID]['streamChannelID'] == channelID and data[serverID]['streamRoleID'] == roleID: # Same info -> disable stream ping
                    data[serverID]['streamChannelID'] = None
                    data[serverID]['streamRoleID'] = None
                    await self.bot.say('StreamPing disabled!')
                else: # Enable
                    data[serverID]['streamChannelID'] = channelID
                    data[serverID]['streamRoleID'] = roleID
                    await self.bot.say('StreamPing enabled!')
            else:
                data[serverID]['streamChannelID'] = channelID
                data[serverID]['streamRoleID'] = roleID
                await self.bot.say('StreamPing enabled!')
        else: # Register server w/ new data
            data[serverID] = {
                "streamChannelID" : channelID,
                "streamRoleID" : roleID
            }
            await self.bot.say('StreamPing enabled!')

        with open('data/serverData.json', 'w') as f: # Update JSON
            json.dump(data, f, indent=2)
        s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')              

    @commands.command(pass_context=True)
    async def clear(self, ctx):
        '''Clears all messages in the text channel.'''

        if not await self.isAdmin(ctx):
            await self.bot.say('Only admins may use !clear.')
            return

        test_msg = await self.bot.say("Are you sure you want to permanently clear all the messages from this channel? Type 'Y' to confirm.")
        if not await self.confirmAction(ctx):
            await self.bot.say('Clear aborted.')
            return

        # Test for permissions
        try:
            await self.bot.delete_message(test_msg)
        except:
            await self.bot.say('Error! ScottBot needs permissions to do this!')
            return

        # Delete
        async for message in self.bot.logs_from(ctx.message.channel):
            await self.bot.delete_message(message)

    @commands.command(pass_context=True)
    async def resetData(self, ctx):
        '''Permanently resets all ScottBot related data.'''
        if (not await self.isAdmin(ctx)):
            await self.bot.say('Only admins may use !resetData.')
            return

        await self.bot.say("Are you sure you want to permanently reset all ScottBot data for this server? Type 'Y' to confirm.")
        if (not await self.confirmAction(ctx)):
            await self.bot.say('Reset aborted.')
            return

        with open('data/serverData.json','r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id
        
        if serverID in data: # Check if registered
            del data[serverID]
            await self.bot.say('Server successfully data reset!')
        else: # Server has no data
            await self.bot.say('No server data found!')
            return

        with open('data/serverData.json', 'w') as f: # Update JSON
            json.dump(data, f, indent=2)
        s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')

    async def isAdmin(self, ctx):
        user = ctx.message.author
        permissions = user.permissions_in(ctx.message.channel)
        if not permissions.administrator:
            return False
        return True

    async def confirmAction(self, ctx):
        msg = await self.bot.wait_for_message(timeout=10, author=ctx.message.author)
        if msg == None or msg.content.lower() != 'y':
            return False
        return True

def setup(bot):
    bot.add_cog(Admin(bot))