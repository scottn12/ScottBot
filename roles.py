# ScottBot by github.com/scottn12
# quotes.py
# Contains all role management commands.

import discord
from discord.ext import commands
from discord.utils import get
import json
import time
import asyncio


class Roles(commands.Cog, name='Roles'):
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
        serverID = str(ctx.message.guild.id)
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
        all_roles = ctx.message.guild.roles
        for role in all_roles:
            if role.permissions >= discord.Permissions.all() or role.is_default():
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
                if str(roles[i].id) in allowed_roles:
                    content += f'Remove `{roles[i]}`\n'
                else:
                    content += f'Add `{roles[i]}`\n'
            msg = await ctx.send(content)
            for i in range(roles_len):
                await msg.add_reaction(react[i])
            start = time.time()
            end = start + TIMEOUT
            while time.time() < end:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=int(end - time.time()))
                except asyncio.TimeoutError:
                    pass
                if not reaction or user != ctx.message.author:
                    continue
                e = reaction.emoji
                role = roles[react.index(e)]
                roleID = str(role.id)
                if roleID in allowed_roles:
                    allowed_roles.remove(roleID)
                    await ctx.send(f'You have removed `{role}`!')
                    content = content.replace(f'Remove `{role}`', f'Add `{role}`')
                    await msg.edit(content=content)
                else:
                    allowed_roles.append(roleID)
                    await ctx.send(f'You have added `{role}`!')
                    content = content.replace(f'Add `{role}`', f'Remove `{role}`')
                    await msg.edit(content=content)
                # Update
                data[serverID]['allowedRoles'] = allowed_roles
                self.writeJSON()
            content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
            await msg.edit(content=content)
            return

        # Over 9 Roles
        TIMEOUT = 90
        content = f'Choose the role(s) you would like to add/remove (**Active for {TIMEOUT} seconds**):\n'
        for i in range(9):
            content += f'{emoji[i]} '
            if str(roles[i].id) in allowed_roles:
                content += f'Remove `{roles[i]}`\n'
            else:
                content += f'Add `{roles[i]}`\n'
        msg = await ctx.send(content)
        await msg.add_reaction(u"\u25C0")
        for i in range(9):
            await msg.add_reaction(react[i])
        await msg.add_reaction(u"\u25B6")
        page = 0
        start = time.time()
        end = start + TIMEOUT
        while time.time() < end:
            if page * 9 + 8 >= roles_len:
                on_page = roles_len % 9
            else:
                on_page = 9
            all_emoji = react[:on_page] + [u"\u25C0", u"\u25B6"]
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=int(end - time.time()))
            except asyncio.TimeoutError:
                pass
            if not reaction or user != ctx.message.author:
                continue
            e = reaction.emoji
            # Back
            if e == u"\u25C0" or e == '◀':
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                count = 0
                content = f'Choose the role(s) you would like to add/remove (**Active for {TIMEOUT} seconds**):\n'
                for i in range(page * 9, page * 9 + 9):
                    content += f'{emoji[count]} '
                    if str(roles[i].id) in allowed_roles:
                        content += f'Remove `{roles[i]}`\n'
                    else:
                        content += f'Add `{roles[i]}`\n'
                    count += 1
                await msg.edit(content=content)
                continue
            # Forward
            if e == u"\u25B6" or e == '▶':
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
                    if str(roles[i].id) in allowed_roles:
                        content += f'Remove `{roles[i]}`\n'
                    else:
                        content += f'Add `{roles[i]}`\n'
                    count += 1
                await msg.edit(content=content)
                continue
            # Make change
            role = roles[react.index(e) + page * 9]
            roleID = str(role.id)
            if roleID in allowed_roles:
                allowed_roles.remove(roleID)
                await ctx.send(f'You have removed `{role}`!')
                content = content.replace(f'Remove `{role}`', f'Add `{role}`')
                await msg.edit(content=content)
            else:
                allowed_roles.append(roleID)
                await ctx.send(f'You have added `{role}`!')
                content = content.replace(f'Add `{role}`', f'Remove `{role}`')
                await msg.edit(content=content)
            # Update
            data[serverID]['allowedRoles'] = allowed_roles
            self.writeJSON()
        content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
        await msg.edit(content=content)

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
            await ctx.send(f'Error! No name given.')
            return
        name = ' '.join(split)
        for r in ctx.message.guild.roles:
            if r.name == name:
                await ctx.send(f'Error! Role `{name}` already exists.')
                return
        role = await self.bot.create_role(ctx.message.guild, name=name)
        await self.bot.edit_role(ctx.message.guild, role, mentionable=True, name=name)
        await ctx.send(f'Role `{name}` was successfully created!')

    @commands.command(pass_context=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx):
        '''Join/leave a role using !role @role/"role"'''
        if len(ctx.message.content) < 7:
            await ctx.send('No role(s) given! Use the following format: `!role @role/"role"` or use `!roles`.')
            return
        else:
            roles = ctx.message.role_mentions  # Get mentioned roles
            roleStr = []
            s = ctx.message.content[6:]
            roleStr = s.split('"')

        allowedRoles = []
        serverID = ctx.message.guild.id

        # Get allowed roles (JSON)
        data = self.cacheJSON
        if serverID in data and 'allowedRoles' in data[serverID] and data[serverID]['allowedRoles']:  # Check if server is registered / role data exists / role data not empty
            allowedRoles = data[serverID]['allowedRoles']
        else:  # No server/role data registered yet
            await ctx.send('No roles have been enabled to be used with !role. Use `!manageRoles` to enable roles.')
            return

        user = ctx.message.author

        for role in roles:  # Evaluate mentioned roles
            if str(role.id) in allowedRoles:
                if role in (user.roles):
                    await ctx.send('You have been removed from role "' + role.name + '"!')
                    try:
                        await user.remove_roles(role)
                    except:
                        await ctx.send('Error! Permission denied. Try checking ScottBot\'s permissions')
                        return
                else:
                    await ctx.send('You have been added to role "' + role.name + '"!')
                    try:
                        await user.add_roles(role)
                    except:
                        await ctx.send('Error! Permission denied. Try checking ScottBot\'s permissions')
                        return
            else:
                await ctx.send('Error! Role: "' + role.name + '" is not enabled to be used with !role.')

        serverRoles = ctx.message.guild.roles

        for role in roleStr:  # Evaluate quoted roles
            found = False
            if role == '' or role == ' ' or role[0] == '<':
                continue
            for serverRole in serverRoles:
                if (role == serverRole.name):
                    found = True
                    if (str(serverRole.id) in allowedRoles):
                        if (serverRole in user.roles):
                            await ctx.send('You have been removed from role: "' + serverRole.name + '"!')
                            await user.remove_roles(serverRole)
                        else:
                            await ctx.send('You have been added to role: "' + serverRole.name + '"!')
                            await user.add_roles(serverRole)
                    else:
                        await ctx.send('Error! Role: "' + serverRole.name + '" is not enabled to be used with !role.')
            if not found:
                await ctx.send('Error! Role: "' + role + '" not found!')

    @commands.command(pass_context=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def roles(self, ctx):
        '''Shows roles available to join/leave.'''
        # Get allowed roles (JSON)
        serverID = str(ctx.message.guild.id)
        data = self.cacheJSON
        if serverID in data and 'allowedRoles' in data[serverID] and data[serverID]['allowedRoles']:  # Check if server is registered / role data exists / role data not empty
            allowedRoles = data[serverID]['allowedRoles']
        else:  # No server/role data registered yet
            await ctx.send('No roles have been enabled to be used with !role. Use `!manageRoles` to enable roles.')
            return

        for id in allowedRoles:
            role = ctx.message.guild.get_role(int(id))
            if not role:  # Role has been removed since last use
                allowedRoles.remove(id)
                data[serverID]['allowedRoles'] = allowedRoles
                self.writeJSON()

        author = ctx.message.author
        user_roles = author.roles
        emoji = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']
        react = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']  # unicode for emoji's 1-9
        total_roles = len(allowedRoles)
        # Allowed roles can fit in one message
        TIMEOUT = 30
        if total_roles <= 9:
            content = f'Choose the role(s) {author.mention} would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
            for i in range(total_roles):
                role = ctx.message.guild.get_role(int(allowedRoles[i]))
                content += f'{emoji[i]} '
                if role in user_roles:
                    content += 'Leave'
                else:
                    content += 'Join'
                content += f' `{role}`\n'
            msg = await ctx.send(content)
            for i in range(total_roles):
                await msg.add_reaction(react[i])
            start = time.time()
            end = start + TIMEOUT
            while time.time() < end:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=int(end - time.time()))
                except asyncio.TimeoutError:
                    pass
                if not reaction or user != author:
                    continue
                e = reaction.emoji
                role = ctx.message.guild.get_role(int(allowedRoles[react.index(e)]))
                if role in user.roles:
                    await user.remove_roles(role)
                    await ctx.send(f'{user.name} has left `{role}`!')
                    content = content.replace(f'Leave `{role}`', f'Join `{role}`')
                    await msg.edit(content=content)
                else:
                    await user.add_roles(role)
                    await ctx.send(f'{user.name} has joined `{role}`!')
                    content = content.replace(f'Join `{role}`', f'Leave `{role}`')
                    await msg.edit(content=content)
            content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
            await msg.edit(content=content)
            return

        # Over 9 Allowed Roles
        TIMEOUT = 90
        content = f'Choose the role(s) {author.mention} would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
        for i in range(9):
            role = ctx.message.guild.get_role(int(allowedRoles[i]))
            content += f'{emoji[i]} '
            if role in user_roles:
                content += 'Leave'
            else:
                content += 'Join'
            content += f' `{role}`\n'
        msg = await ctx.send(content)
        await msg.add_reaction(u"\u25C0")
        for i in range(9):
            await msg.add_reaction(react[i])
        await msg.add_reaction(u"\u25B6")
        page = 0
        start = time.time()
        end = start + TIMEOUT
        while time.time() < end:
            if page * 9 + 8 >= total_roles:
                on_page = total_roles % 9
            else:
                on_page = 9
            all_emoji = react[:on_page] + [u"\u25C0", u"\u25B6"]
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=int(end - time.time()))
            except asyncio.TimeoutError:
                pass
            if not reaction or user != author:
                continue
            e = reaction.emoji
            # Back
            if e == u"\u25C0" or e == '◀':
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                count = 0
                content = f'Choose the role(s) you would like to join/leave (**Active for {TIMEOUT} seconds**):\n'
                for i in range(page * 9, page * 9 + 9):
                    role = ctx.message.guild.get_role(int(allowedRoles[i]))
                    content += f'{emoji[count]} '
                    if role in user_roles:
                        content += 'Leave'
                    else:
                        content += 'Join'
                    content += f' `{role}`\n'
                    count += 1
                await msg.edit(content=content)
                continue
            # Forward
            if e == u"\u25B6" or e == '▶':
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
                    role = ctx.message.guild.get_role(int(allowedRoles[i]))
                    content += f'{emoji[count]} '
                    if role in user_roles:
                        content += 'Leave'
                    else:
                        content += 'Join'
                    content += f' `{role}`\n'
                    count += 1
                await msg.edit(content=content)
                continue
            # Role Change
            role = ctx.message.guild.get_role(int(allowedRoles[react.index(e) + page * 9]))
            if role in user.roles:
                await user.remove_roles(role)
                await ctx.send(f'{user.name} has left `{role}`!')
                content = content.replace(f'Leave `{role}`', f'Join `{role}`')
                await msg.edit(content=content)
            else:
                await user.add_roles(role)
                await ctx.send(f'{user.name} has joined `{role}`!')
                content = content.replace(f'Join `{role}`', f'Leave `{role}`')
                await msg.edit(content=content)
        content = content.replace(f'Active for {TIMEOUT} seconds', 'NO LONGER ACTIVE')
        await msg.edit(content=content)

    @commands.command(pass_context=True)
    async def r(self, ctx):
        """Alias for !roles."""
        await self.roles.invoke(ctx)

    @commands.command(pass_context=True)
    async def roleRank(self, ctx):
        '''Displays the number of users in each role.'''
        content = f'```{"Role":24s}\tMembers\n'
        for role in ctx.message.guild.roles:
            count = 0
            for member in ctx.message.guild.members:
                if role in member.roles:
                    count += 1
            content += f'{str(role):24s}\t{count}\n'
        content += '```'
        await ctx.send(content)

    # Update file with cached JSON and upload to AWS
    def writeJSON(self):
        with open('data/roles.json', 'w') as f:  # Update JSON
            json.dump(self.cacheJSON, f, indent=2)

def setup(bot):
    bot.add_cog(Roles(bot))
