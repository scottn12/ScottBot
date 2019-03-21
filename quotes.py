from discord.ext import commands
from bot import BUCKET_NAME, s3
import json
import random
import time

class Quotes:
    '''Commands for quotes.'''
    def __init__(self, bot):
        self.bot = bot
        #self.bot.command(name='q', pass_context=True)(self.quote.callback)

    @commands.command(pass_context=True)
    async def addQuote(self, ctx):
        '''Adds a quote to the list of quotes.'''
        if ctx.message.content[:4] == '!aq ':
            quote = ctx.message.content[4:]
        else:
            quote = ctx.message.content[10:]
        if len(quote) == 0:
            await self.bot.say('Error! No quote was provided.')
            return

        mentions = ctx.message.mentions
        if mentions:
            await self.bot.say('Error! You cannot mention someone in a quote.')
            return

        # Update JSON
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id

        if serverID in data:  # Check if server is registered yet
            if 'quotes' in data[serverID]:  # Check if quotes are registered yet
                data[serverID]['quotes'].append(quote)
                total = len(data[serverID]['quotes'])
            else:  # add quote field
                data[serverID]['quotes'] = [quote]
                total = 1
        else:  # new server
            data[serverID] = {
                "quotes": [quote]
            }
            total = 1

        with open('data/serverData.json', 'w') as f:  # Update JSON
            json.dump(data, f, indent=2)
        s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')

        await self.bot.say(f'Quote **{total}** added!')

    @commands.command(pass_context=True)
    async def aq(self, ctx):
        """Alias for !addQuote."""
        await self.addQuote.invoke(ctx)

    @commands.command(pass_context=True)
    async def quote(self, ctx):
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:
            await self.bot.say('Error! No quotes found! Use `!addQuote` to add quotes.')
            return

        try:
            index = int(ctx.message.content.split()[1])
        except:
            await self.bot.say('Error! No quote number provided! Use `!allQuotes` to see full list quotes.')
            return

        if index > len(quotes) or index <= 0:
            await self.bot.say('Error! That quote does not exist! Use `!allQuotes` to see the full list of quotes.')
            return
        await self.bot.say(quotes[index-1])

    @commands.command(pass_context=True)
    async def q(self, ctx):
        """Alias for !quote."""
        await self.quote.invoke(ctx)

    @commands.command(pass_context=True)
    async def randomQuote(self, ctx):
        """ScottBot says a random quote."""
        MAX_QUOTES = 5
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)

        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:
            await self.bot.say('Error! No quotes found! Use !addQuote to add quotes.')
            return

        # Check if int was passed & num of quotes is not greater than max allowed
        try:
            arg = int(ctx.message.content.split()[1])
        except:
            arg = 1
        if arg > MAX_QUOTES:
            await self.bot.say('**Up to ' + str(MAX_QUOTES) + ' quotes are allowed at once.**')
            arg = MAX_QUOTES

        for _ in range(arg):
            rng = random.randint(0, len(quotes) - 1)
            await self.bot.say(quotes[rng])

    @commands.command(pass_context=True)
    async def rq(self, ctx):
        """Alias for !randomQuote."""
        await self.randomQuote.invoke(ctx)

    @commands.command(pass_context=True)
    async def allQuotes(self, ctx):
        """Displays all registered quotes."""
        # Setup
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:
            await self.bot.say('Error! No quotes found! Use !addQuote to add quotes.')
            return
        MAX = 25
        TIMEOUT = 180
        total = len(quotes)

        # All quotes can fit on one  page
        content = '```'
        if total <= MAX:
            for i in range(total):
                content += f'{str(i+1):3s} {quotes[i]}\n'
            content += '```'
            await self.bot.say(content)
            return

        # Multiple pages needed
        content = f'**Active for {TIMEOUT//60} minutes.**\n```'
        for i in range(MAX):
            content += f'{str(i+1):3s} {quotes[i]}\n'
        content += '```'
        msg = await self.bot.say(content)
        react = [u"\u25C0", u"\u25B6"]
        await self.bot.add_reaction(msg, react[0])  # Back
        await self.bot.add_reaction(msg, react[1])  # Forward
        page = 0
        start = time.time()
        while time.time() < start + TIMEOUT:
            if page * MAX + MAX-1 >= total:
                on_page = total % MAX
            else:
                on_page = MAX
            reaction = await self.bot.wait_for_reaction(react, message=msg, timeout=int(start-time.time()))
            if not reaction or reaction.user == self.bot.user:
                continue
            e = reaction.reaction.emoji
            # Back
            if e == u"\u25C0":
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                content = f'**Active for {TIMEOUT//60} minutes.**\n```'
                for i in range(page * MAX, page * MAX + MAX):
                    content += f'{str(i+1):3s} {quotes[i]}\n'
                content += '```'
                await self.bot.edit_message(msg, new_content=content)
                continue
            # Forward
            else:
                if page * MAX + MAX-1 >= total - 1:  # Already on the last page
                    continue
                page += 1
                if page * MAX + MAX-1 >= total:  # Already on the last page
                    end = page * MAX + total % MAX
                else:
                    end = page * MAX + MAX
                content = f'**Active for {TIMEOUT//60} minutes.**\n```'
                for i in range(page * MAX, end):
                    content += f'{str(i+1):3s} {quotes[i]}\n'
                content += '```'
                await self.bot.edit_message(msg, new_content=content)
        content = content.replace(f'Active for {TIMEOUT//60} minutes.', 'NO LONGER ACTIVE')
        await self.bot.edit_message(msg, new_content=content)

    @commands.command(pass_context=True)
    async def allq(self, ctx):
        """Alias for !allQuotes."""
        await self.allQuotes.invoke(ctx)

    @commands.command(pass_context=True)
    async def changeQuote(self, ctx):
        """Change or delete a quote !changeQuote quoteNumber newQuote"""
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:
            await self.bot.say('Error! No quotes registered yet! Use `!addQuote` to add quotes.')
            return

        # Parse
        content = ctx.message.content
        if content[:3] == '!cq':
            content = content[4:]
        else:
            content = content[13:]
        if content == '':
            await self.bot.say('Error! Use the format `!changeQuote quoteNumber newQuote`')
            return
        try:
            index = content.index(' ')
            quote_num = int(content[:index])
            new = content[index+1:]
        except:
            try:
                quote_num = int(content)
                new = None
            except:
                await self.bot.say('Error! Use the format `!changeQuote quoteNumber newQuote`')
                return
        if quote_num > len(quotes) or quote_num <= 0:
            await self.bot.say('Error! That quote does not exist! Use `!allQuotes` to see the full list of quotes.')
            return

        # Ask user to confirm and perform change
        thumbs = ['👍', '👎']
        if not new:
            confirm = await self.bot.say(f'Delete:\n```{quotes[quote_num-1]}```Press {thumbs[0]} to confirm and {thumbs[1]} to abort.')
        else:
            confirm = await self.bot.say(f'Change:\n```{quotes[quote_num - 1]}\nTO\n{new}```Press {thumbs[0]} to confirm and {thumbs[1]} to abort.')

        TIMEOUT = 15
        await self.bot.add_reaction(confirm, thumbs[0])
        await self.bot.add_reaction(confirm, thumbs[1])
        start = time.time()
        end = start + TIMEOUT
        while time.time() < end:
            reaction = await self.bot.wait_for_reaction(thumbs, message=confirm, timeout=int(start - time.time()))
            if not reaction or reaction.user != ctx.message.author:
                continue
            e = reaction.reaction.emoji
            if e == '👍':
                if not new:
                    quotes.remove(quotes[quote_num-1])
                else:
                    quotes[quote_num-1] = new
                data[serverID]['quotes'] = quotes
                with open('data/serverData.json', 'w') as f:  # Update JSON
                    json.dump(data, f, indent=2)
                s3.upload_file('data/serverData.json', BUCKET_NAME, 'serverData.json')
                await self.bot.say('Success!')
                return
            else:
                await self.bot.say('Change aborted.')
                return
        await self.bot.say('Change aborted.')
        return

    @commands.command(pass_context=True)
    async def cq(self, ctx):
        """Alias for !changeQuote."""
        await self.changeQuote.invoke(ctx)

def setup(bot):
    bot.add_cog(Quotes(bot))
