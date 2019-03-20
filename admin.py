import discord
from discord.ext import commands
from bot import BUCKET_NAME, s3
import json
import time

class Admin:
    '''Commands for server administrators only.'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def manageRoles(self, ctx):
        '''Enable/Disable role(s) to be used with !roles.'''
        if not await self.isAdmin(ctx):  # Check Admin
            await self.bot.say('Only admins may use !allowRoles.')
            return

        # Get allowed roles (JSON)
        serverID = ctx.message.server.id
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)
        if serverID in data:
            if 'allowedRoles' in data[serverID]:
                allowed_roles = data[serverID]['allowedRoles']
            else:  # No Role data
                allowed_roles = []
                data[serverID]['allowedRoles'] = allowed_roles
        else:  # New Server
            allowed_roles = []
            data[serverID] = {
                "allowedRoles" : allowed_roles
            }

        # Get list of all valid roles to add/remove
        roles = []
        all_roles = ctx.message.server.roles
        for role in all_roles:
            if role.permissions >= discord.Permissions.all() or role.is_everyone:
                continue
            roles.append(role)
        roles_len = len(roles)
        emoji = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']
        react = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']  # unicode for emoji's 1-9

        # Roles can fit in one message
        TIMEOUT = 30
        if roles_len <= 9:
            content = f'Choose the role(s) you would like to add/remove (Active for {TIMEOUT} seconds):\n'
            for i in range(roles_len):
                content += f'{emoji[i]} '
                if roles[i].id in allowed_roles:
                    content += f'Remove `{roles[i]}`\n'
                else:
                    content += f'Add `{roles[i]}`\n'
            msg = await self.bot.say(content)
            for i in range(roles_len):
                await self.bot.add_reaction(msg, react[i])
            start = time.time()
            while time.time() < start + TIMEOUT:
                reaction = await self.bot.wait_for_reaction(react[:roles_len], message=msg, timeout=TIMEOUT)
                if not reaction or reaction.user != ctx.message.author:
                    continue
                e = reaction.reaction.emoji
                role = roles[react.index(e)]
                if role.id in allowed_roles:
                    allowed_roles.remove(role.id)
                    await self.bot.say(f'You have removed `{role}`!')
                    content = content.replace(f'Remove `{role}`', f'Add `{role}`')
                    await self.bot.edit_message(msg, new_content=content)
                else:
                    allowed_roles.append(role.id)
                    await self.bot.say(f'You have added `{role}`!')
                    content = content.replace(f'Add `{role}`', f'Remove `{role}`')
                    await self.bot.edit_message(msg, new_content=content)
                # Update
                data[serverID]['allowedRoles'] = allowed_roles
                with open('data/serverData.json', 'w') as f:
                    json.dump(data, f, indent=2)
                s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')
            return

        # Over 9 Roles
        TIMEOUT = 90
        content = f'Choose the role(s) you would like to add/remove (Active for {TIMEOUT} seconds):\n'
        for i in range(9):
            content += f'{emoji[i]} '
            if roles[i].id in allowed_roles:
                content += f'Remove `{roles[i]}`\n'
            else:
                content += f'Add `{roles[i]}`\n'
        msg = await self.bot.say(content)
        await self.bot.add_reaction(msg, u"\u25C0")
        for i in range(9):
            await self.bot.add_reaction(msg, react[i])
        await self.bot.add_reaction(msg, u"\u25B6")
        start = time.time()
        page = 0
        while time.time() < start + TIMEOUT:
            if page * 9 + 8 >= roles_len:
                on_page = roles_len % 9
            else:
                on_page = 9
            all_emoji = react[:on_page] + [u"\u25C0", u"\u25B6"]
            reaction = await self.bot.wait_for_reaction(all_emoji, message=msg, timeout=TIMEOUT)
            if not reaction or reaction.user != ctx.message.author:
                continue
            e = reaction.reaction.emoji
            # Back
            if e == u"\u25C0":
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                count = 0
                content = f'Choose the role(s) you would like to add/remove (Active for {TIMEOUT} seconds):\n'
                for i in range(page * 9, page * 9 + 9):
                    content += f'{emoji[count]} '
                    if roles[i].id in allowed_roles:
                        content += f'Remove `{roles[i]}`\n'
                    else:
                        content += f'Add `{roles[i]}`\n'
                    count += 1
                await self.bot.edit_message(msg, new_content=content)
                continue
            # Forward
            if e == u"\u25B6":
                if page * 9 + 8 >= roles_len - 1:  # Already on the last page
                    continue
                page += 1
                count = 0
                if page * 9 + 8 >= roles_len:  # Already on the last page
                    end = page * 9 + roles_len % 9
                else:
                    end = page * 9 + 9
                content = 'Choose the role(s) you would like to join/leave (Active for {TIMEOUT} seconds):\n'
                for i in range(page * 9, end):
                    content += f'{emoji[count]} '
                    if roles[i].id in allowed_roles:
                        content += f'Remove `{roles[i]}`\n'
                    else:
                        content += f'Add `{roles[i]}`\n'
                    count += 1
                await self.bot.edit_message(msg, new_content=content)
                continue
            # Make change
            role = roles[react.index(e) + page * 9]
            if role.id in allowed_roles:
                allowed_roles.remove(role.id)
                await self.bot.say(f'You have removed `{role}`!')
                content = content.replace(f'Remove `{role}`', f'Add `{role}`')
                await self.bot.edit_message(msg, new_content=content)
            else:
                allowed_roles.append(role.id)
                await self.bot.say(f'You have added `{role}`!')
                content = content.replace(f'Add `{role}`', f'Remove `{role}`')
                await self.bot.edit_message(msg, new_content=content)
            # Update
            data[serverID]['allowedRoles'] = allowed_roles
            with open('data/serverData.json', 'w') as f:
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

        s3.upload_file('bot_database.db', BUCKET_NAME, 'bot_database.db')

    """@commands.command(pass_context=True)
    async def changePrefix(self, ctx): #NOT FINISHED
        '''Changes the prefix for ScottBot commands.'''
        if (not await self.isAdmin(ctx)):
            await self.bot.say('Only admins may use !changePrefix.')
            return

        import string
        newPrefix = ctx.message.content[14:]
        if (newPrefix in string.punctuation):
            #await self.bot.say('Prefix successfully changed!')
            x = 2 #nothing
        else:
            await self.bot.say('Invalid prefix. New prefix must be a single punctuation character.')
            return"""

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