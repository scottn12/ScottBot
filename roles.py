# ScottBot by github.com/scottn12
# quotes.py
# Contains all role management commands.

import discord
from discord.ext import commands
from discord.utils import get
from bot import BUCKET_NAME, s3
import json
import time

class Roles:
    """Commands for role management."""
    def __init__(self, bot):
        self.bot = bot
        with open('data/roles.json', 'r') as f:
            self.cacheJSON = json.load(f)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def manageRoles(self, ctx):
        """Enable/Disable role(s) to be used with !roles (ADMIN)."""
        # Get allowed roles (JSON)
        serverID = ctx.message.server.id
        data = self.cacheJSON
        if serverID in data:
            if 'allowedRoles' in data[serverID]:
                allowed_roles = data[serverID]['allowedRoles']
            else:  # No Role data
                allowed_roles = []
                data[serverID]['allowedRoles'] = allowed_roles
        else:  # New Server
            allowed_roles = []
            data[serverID] = {
                "allowedRoles": allowed_roles
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
            content = f'Choose the role(s) you would like to add/remove (**Active for {TIMEOUT} seconds**):\n'
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
            end = start + TIMEOUT
            while time.time() < end:
                reaction = await self.bot.wait_for_reaction(react[:roles_len], message=msg, timeout=int(end-time.time()))
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
                self.writeJSON()
            content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
            await self.bot.edit_message(msg, new_content=content)
            return

        # Over 9 Roles
        TIMEOUT = 90
        content = f'Choose the role(s) you would like to add/remove (**Active for {TIMEOUT} seconds**):\n'
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
        page = 0
        start = time.time()
        end = start + TIMEOUT
        while time.time() < end:
            if page * 9 + 8 >= roles_len:
                on_page = roles_len % 9
            else:
                on_page = 9
            all_emoji = react[:on_page] + [u"\u25C0", u"\u25B6"]
            reaction = await self.bot.wait_for_reaction(all_emoji, message=msg, timeout=int(end-time.time()))
            if not reaction or reaction.user != ctx.message.author:
                continue
            e = reaction.reaction.emoji
            # Back
            if e == u"\u25C0":
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                count = 0
                content = f'Choose the role(s) you would like to add/remove (**Active for {TIMEOUT} seconds**):\n'
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
                    end_i = page * 9 + roles_len % 9
                else:
                    end_i = page * 9 + 9
                content = f'Choose the role(s) you would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
                for i in range(page * 9, end_i):
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
            self.writeJSON()
        content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
        await self.bot.edit_message(msg, new_content=content)

    @commands.command(pass_context=True)
    async def mr(self, ctx):
        """Alias for !manageRoles."""
        await self.manageRoles.invoke(ctx)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def addRole(self, ctx):
        """Creats mentionable role with given name (ADMIN)."""
        split = ctx.message.content.split()[1:]
        if not split:
            await self.bot.say(f'Error! No name given.')
            return
        name = ' '.join(split)
        for r in ctx.message.server.roles:
            if r.name == name:
                await self.bot.say(f'Error! Role `{name}` already exists.')
                return
        role = await self.bot.create_role(ctx.message.server, name=name)
        await self.bot.edit_role(ctx.message.server, role, mentionable=True, name=name)
        await self.bot.say(f'Role `{name}` was successfully created!')

    @commands.command(pass_context=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx):
        '''Join/leave a role using !role @role/"role"'''
        if len(ctx.message.content) < 7:
            await self.bot.say('No role(s) given! Use the following format: `!role @role/"role"` or use `!roles`.')
            return
        else:
            roles = ctx.message.role_mentions  # Get mentioned roles
            roleStr = []
            s = ctx.message.content[6:]
            roleStr = s.split('"')

        allowedRoles = []
        serverID = ctx.message.server.id

        # Get allowed roles (JSON)
        data = self.cacheJSON
        if serverID in data and 'allowedRoles' in data[serverID] and data[serverID]['allowedRoles']:  # Check if server is registered / role data exists / role data not empty
            allowedRoles = data[serverID]['allowedRoles']
        else:  # No server/role data registered yet
            await self.bot.say('No roles have been enabled to be used with !role. Use !allowRole to enable roles.')
            return

        user = ctx.message.author

        for role in roles:  # Evaluate mentioned roles
            if role.id in allowedRoles:
                if role in (user.roles):
                    await self.bot.say('You have been removed from role "' + role.name + '"!')
                    try:
                        await self.bot.remove_roles(user, role)
                    except:
                        await self.bot.say('Error! Permission denied. Try checking ScottBot\'s permissions')
                        return
                else:
                    await self.bot.say('You have been added to role "' + role.name + '"!')
                    try:
                        await self.bot.add_roles(user, role)
                    except:
                        await self.bot.say('Error! Permission denied. Try checking ScottBot\'s permissions')
                        return
            else:
                await self.bot.say('Error! Role: "' + role.name + '" is not enabled to be used with !role.')

        serverRoles = ctx.message.server.roles

        for role in roleStr:  # Evaluate quoted roles
            found = False
            if role == '' or role == ' ' or role[0] == '<':
                continue
            for serverRole in serverRoles:
                if (role == serverRole.name):
                    found = True
                    if (serverRole.id in allowedRoles):
                        if (serverRole in user.roles):
                            await self.bot.say('You have been removed from role: "' + serverRole.name + '"!')
                            await self.bot.remove_roles(user, serverRole)
                        else:
                            await self.bot.say('You have been added to role: "' + serverRole.name + '"!')
                            await self.bot.add_roles(user, serverRole)
                    else:
                        await self.bot.say('Error! Role: "' + serverRole.name + '" is not enabled to be used with !role.')
            if not found:
                await self.bot.say('Error! Role: "' + role + '" not found!')

    @commands.command(pass_context=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def roles(self, ctx):
        '''Shows roles available to join/leave.'''
        # Get allowed roles (JSON)
        serverID = ctx.message.server.id
        data = self.cacheJSON
        if serverID in data and 'allowedRoles' in data[serverID] and data[serverID]['allowedRoles']:  # Check if server is registered / role data exists / role data not empty
            allowedRoles = data[serverID]['allowedRoles']
        else:  # No server/role data registered yet
            await self.bot.say('No roles have been enabled to be used with !role. Use !allowRole to enable roles.')
            return

        for id in allowedRoles:
            role = get(ctx.message.server.roles, id=id)
            if not role:  # Role has been removed since last use
                allowedRoles.remove(id)
                data[serverID]['allowedRoles'] = allowedRoles
                self.writeJSON()

        user = ctx.message.author
        user_roles = user.roles
        emoji = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']
        react = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']  # unicode for emoji's 1-9
        total_roles = len(allowedRoles)
        # Allowed roles can fit in one message
        TIMEOUT = 30
        if total_roles <= 9:
            content = f'Choose the role(s) {user.mention} would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
            for i in range(total_roles):
                role = get(ctx.message.server.roles, id=allowedRoles[i])
                content += f'{emoji[i]} '
                if role in user_roles:
                    content += 'Leave'
                else:
                    content += 'Join'
                content += f' `{role}`\n'
            msg = await self.bot.say(content)
            for i in range(total_roles):
                await self.bot.add_reaction(msg, react[i])
            start = time.time()
            end = start + TIMEOUT
            while time.time() < end:
                reaction = await self.bot.wait_for_reaction(react[:total_roles], message=msg, timeout=int(end-time.time()))
                if not reaction or reaction.user != user:
                    continue
                e = reaction.reaction.emoji
                role = get(ctx.message.server.roles, id=allowedRoles[react.index(e)])
                if role in user.roles:
                    await self.bot.remove_roles(user, role)
                    await self.bot.say(f'{user.name} has left `{role}`!')
                    content = content.replace(f'Leave `{role}`', f'Join `{role}`')
                    await self.bot.edit_message(msg, new_content=content)
                else:
                    await self.bot.add_roles(user, role)
                    await self.bot.say(f'{user.name} has joined `{role}`!')
                    content = content.replace(f'Join `{role}`', f'Leave `{role}`')
                    await self.bot.edit_message(msg, new_content=content)
            content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
            await self.bot.edit_message(msg, new_content=content)
            return

        # Over 9 Allowed Roles
        TIMEOUT = 90
        content = f'Choose the role(s) {user.mention} would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
        for i in range(9):
            role = get(ctx.message.server.roles, id=allowedRoles[i])
            content += f'{emoji[i]} '
            if role in user_roles:
                content += 'Leave'
            else:
                content += 'Join'
            content += f' `{role}`\n'
        msg = await self.bot.say(content)
        await self.bot.add_reaction(msg, u"\u25C0")
        for i in range(9):
            await self.bot.add_reaction(msg, react[i])
        await self.bot.add_reaction(msg, u"\u25B6")
        page = 0
        start = time.time()
        end = start + TIMEOUT
        while time.time() < end:
            if page * 9 + 8 >= total_roles:
                on_page = total_roles % 9
            else:
                on_page = 9
            all_emoji = react[:on_page] + [u"\u25C0", u"\u25B6"]
            reaction = await self.bot.wait_for_reaction(all_emoji, message=msg, timeout=int(end - time.time()))
            if not reaction or reaction.user != user:
                continue
            e = reaction.reaction.emoji
            # Back
            if e == u"\u25C0":
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                count = 0
                content = f'Choose the role(s) you would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
                for i in range(page * 9, page * 9 + 9):
                    role = get(ctx.message.server.roles, id=allowedRoles[i])
                    content += f'{emoji[count]} '
                    if role in user_roles:
                        content += 'Leave'
                    else:
                        content += 'Join'
                    content += f' `{role}`\n'
                    count += 1
                await self.bot.edit_message(msg, new_content=content)
                continue
            # Forward
            if e == u"\u25B6":
                if page * 9 + 8 >= total_roles - 1:  # Already on the last page
                    continue
                page += 1
                count = 0
                if page * 9 + 8 >= total_roles:  # Already on the last page
                    end_i = page * 9 + total_roles % 9
                else:
                    end_i = page * 9 + 9
                content = f'Choose the role(s) {user.mention} would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
                for i in range(page * 9, end_i):
                    role = get(ctx.message.server.roles, id=allowedRoles[i])
                    content += f'{emoji[count]} '
                    if role in user_roles:
                        content += 'Leave'
                    else:
                        content += 'Join'
                    content += f' `{role}`\n'
                    count += 1
                await self.bot.edit_message(msg, new_content=content)
                continue
            # Role Change
            role = get(ctx.message.server.roles, id=allowedRoles[react.index(e) + page * 9])
            if role in user.roles:
                await self.bot.remove_roles(user, role)
                await self.bot.say(f'{user.name} has left `{role}`!')
                content = content.replace(f'Leave `{role}`', f'Join `{role}`')
                await self.bot.edit_message(msg, new_content=content)
            else:
                await self.bot.add_roles(user, role)
                await self.bot.say(f'{user.name} has joined `{role}`!')
                content = content.replace(f'Join `{role}`', f'Leave `{role}`')
                await self.bot.edit_message(msg, new_content=content)
        content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
        await self.bot.edit_message(msg, new_content=content)

    @commands.command(pass_context=True)
    async def r(self, ctx):
        """Alias for !roles."""
        await self.roles.invoke(ctx)

    @commands.command(pass_context=True)
    async def roleRank(self, ctx):
        '''Displays the number of users in each role.'''
        content = f'```{"Role":24s}\tMembers\n'
        for role in ctx.message.server.roles:
            count = 0
            for member in ctx.message.server.members:
                if role in member.roles:
                    count += 1
            content += f'{str(role):24s}\t{count}\n'
        content += '```'
        await self.bot.say(content)

    # Update file with cached JSON and upload to AWS
    def writeJSON(self):
        with open('data/roles.json', 'w') as f:  # Update JSON
            json.dump(self.cacheJSON, f, indent=2)
        s3.upload_file('data/roles.json', BUCKET_NAME, 'roles.json')

def setup(bot):
    bot.add_cog(Roles(bot))
