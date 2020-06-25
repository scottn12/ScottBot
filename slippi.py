# ScottBot by github.com/scottn12
# misc.py
# Contains all commands for slippi SSBM.


from discord.ext import commands
import json


class Misc:
    """Miscellaneous commands anyone can use."""
    def __init__(self, bot):
        self.bot = bot
        with open('data/slippi.json', 'r') as f:
            self.cacheJSON = json.load(f)

    @commands.command(pass_context=True)
    async def slippi(self, ctx, name=None):
        """Returns a player's slippi tag if provided, otherwise returns the whole list."""
        data = self.cacheJSON
        if name:
            found = False
            for key in data.keys():
                if key.lower() == name.lower():
                    name = key
                    found = True
            if not found:
                name = None
        if not name:
            rtn = f"```{'Player':10s}Tag\n"
            for key in data.keys():
                rtn += f'{key:10s}{data[key]}\n'
            rtn += "```\nYou can get a specific player's tag by using `!slippi name`"
            await self.bot.say(rtn)
        else:
            await self.bot.say(data[name])

    @commands.command(pass_context=True)
    async def addSlippi(self, ctx, name=None, tag=None):
        """Adds a player to the list of slippi tags."""
        if not (name and tag):
            await self.bot.say('You must provide both a name and tag to be added. `!addSlippi name tag`')
        else:
            data = self.cacheJSON
            for key in data.keys():
                if key.lower() == name.lower():
                    await self.bot.say('Error: Player already added.')
                    return
            else:
                data[name] = tag
                self.writeJSON()
                await self.bot.say('Added successfully!')


    # Update file with cached JSON
    def writeJSON(self):
        with open('data/slippi.json', 'w') as f:  # Update JSON
            json.dump(self.cacheJSON, f, indent=2)

def setup(bot):
    bot.add_cog(Misc(bot))
