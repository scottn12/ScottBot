import discord
from discord.ext import commands

class Admin:
    '''Commands for server administrators only.'''
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def allowRole(self, ctx): 
        '''Enables/Disables role(s) to be used with !role.'''
        if (not await self.isAdmin(ctx)): # Check Admin
            await self.bot.say('Only admins may use !enableAddRole.')
            return

        roles = ctx.message.role_mentions # Get mentioned roles
        roleStr = []
        if len(ctx.message.content) < 12 and not roles:
            await self.bot.say('No role(s) given! Use the following format: !role @role/"role"')
            return
        else:
            s = ctx.message.content[11:]
            roleStr = s.split('"')

        roleIDS = [] 
        serverRoles = ctx.message.server.roles
        for role in roles: # Check mentioned roles
            if role.is_everyone:
                await self.bot.say('Error! Role: "everyone" is not a valid role.')
                continue
            if role.permissions < discord.Permissions.all():
                roleIDS.append(role.id)
            else: 
                await self.bot.say('Error! Role: "' + role.name + '" is an administrator role.')

        for role in roleStr: # Check quotes roles
            if role == '' or role == ' ' or role[0]=='<':
                continue
            if role == 'everyone':
                await self.bot.say('Error! Role: "everyone" is not a valid role.')
                continue
            found = False
            for serverRole in serverRoles:
                if (serverRole.name == role):
                    found = True
                    if serverRole.permissions < discord.Permissions.all():
                        roleIDS.append(serverRole.id)
                    else:
                        await self.bot.say('Error! Role: "' + role + '" is an administrator role.')
            if not found:
                await self.bot.say('Error! Role: "' + role + '" not found!')

        # S3 Connection/JSON Update
        from boto3.session import Session
        from bot import ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME, REGION_NAME
        session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key= ACCESS_SECRET_KEY, region_name= REGION_NAME)
        s3 = session.client('s3')

        s3.download_file(BUCKET_NAME, 'serverData.json', 'data/serverData.json')
        import json
        with open('data/serverData.json','r') as f:
            data = json.load(f)
        
        serverID = ctx.message.server.id
        newData = {
            "serverID": serverID,
            "allowedRoles": roleIDS
        }
        
        newServer = True
        for server in data['servers']: 
            if serverID == server['serverID']: # Check if server is already registered and update if true
                try:
                    rolesJSON = server['allowedRoles']
                    for role in roleIDS:
                        if role in rolesJSON:
                            await self.bot.say(discord.utils.get(ctx.message.server.roles, id=role).name + ' has been disabled.')
                            rolesJSON.remove(role)
                        else:
                            await self.bot.say(discord.utils.get(ctx.message.server.roles, id=role).name + ' has been enabled.')
                            rolesJSON.append(role)
                except: # Server registered, but no role data
                    await self.bot.say('All mentioned roles enabled.')
                    server.update(newData)
                    newServer = False
                newServer = False

        if newServer: # Add new Data
            await self.bot.say('All mentioned roles enabled.')
            data['servers'].append(newData)

        with open('data/serverData.json', 'w') as f: # Update JSON
            json.dump(data, f, indent=2)
        
        s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')

    @commands.command(pass_context=True)
    async def allowStreamPing(self, ctx):
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

        # S3 Connection/JSON Update
        from boto3.session import Session
        from bot import ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME, REGION_NAME
        session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key= ACCESS_SECRET_KEY, region_name= REGION_NAME)
        s3 = session.client('s3')
        s3.download_file(BUCKET_NAME, 'serverData.json', 'data/serverData.json')
        
        import json
        with open('data/serverData.json','r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id
        channelID = ctx.message.channel.id

        newData = {
            "serverID": serverID,
            "streamChannelID": channelID,
            "streamRoleID": roleID,
        }
        
        newServer = True
        for server in data['servers']: 
            if serverID == server['serverID']: # Check if server is already registered and update if true
                try: # Server has existing stream data
                    if server['streamChannelID'] == channelID and server['streamRoleID'] == roleID: # Same info -> disable stream ping
                        server['streamChannelID'] = None
                        server['streamRoleID'] = None
                        await self.bot.say('StreamPing disabled!')
                    else:
                        server['streamChannelID'] = channelID
                        server['streamRoleID'] = roleID
                        await self.bot.say('StreamPing enabled!')
                    newServer = False
                except: # Server has no existing stream data
                    await self.bot.say('StreamPing enabled!')
                    server.update(newData)
                    newServer = False

        if newServer: # Add new Data
            data['servers'].append(newData)

        with open('data/serverData.json', 'w') as f: # Update JSON
            json.dump(data, f, indent=2)
        s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')              

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
    async def resetData(self, ctx):
        '''Permanently resets all ScottBot related data.'''
        if (not await self.isAdmin(ctx)):
            await self.bot.say('Only admins may use !resetData.')
            return

        await self.bot.say("Are you sure you want to permanently reset all ScottBot data for this server? Type 'Y' to confirm.")
        if (not await self.confirmAction(ctx)):
            await self.bot.say('Reset aborted.')
            return

        # S3 Connection/JSON Update
        from boto3.session import Session
        from bot import ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME, REGION_NAME
        session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key= ACCESS_SECRET_KEY, region_name= REGION_NAME)
        s3 = session.client('s3')
        s3.download_file(BUCKET_NAME, 'serverData.json', 'data/serverData.json')
        
        import json
        with open('data/serverData.json','r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id
        
        newServer = True
        for server in data['servers']:
            if serverID == server['serverID']: # Look for server
                data['servers'].remove(server)
                await self.bot.say('Server successfully data reset!')
                newServer = False

        if newServer: # Add new Data
            await self.bot.say('No server data found!')
            return

        with open('data/serverData.json', 'w') as f: # Update JSON
            json.dump(data, f, indent=2)
        s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')

    #@commands.command(pass_context=True)
    #async def changePrefix(self, ctx): #NOT FINISHED
    #    '''Changes the prefix for ScottBot commands.'''
    #    if (not await self.isAdmin(ctx)):
    #        await self.bot.say('Only admins may use !changePrefix.')
    #        return
    #
    #    import string
    #    newPrefix = ctx.message.content[14:]
    #    if (newPrefix in string.punctuation):
    #        #await self.bot.say('Prefix successfully changed!')
    #        x = 2 #nothing
    #    else:
    #        await self.bot.say('Invalid prefix. New prefix must be a single punctuation character.')
    #        return

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
        
        # S3 Connection/JSON Update
        from boto3.session import Session
        from bot import ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME, REGION_NAME
        session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key= ACCESS_SECRET_KEY, region_name= REGION_NAME)
        s3 = session.client('s3')
        s3.download_file(BUCKET_NAME, 'bot_database.db', 'data/bot_database.db')

        # Reset
        import sqlite3
        conn = sqlite3.connect('data/bot_database.db')
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS flake'+ctx.message.server.id)
        c.close()
        conn.close()

        s3.upload_file('bot_database.db', BUCKET_NAME, 'bot_database.db')
        
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