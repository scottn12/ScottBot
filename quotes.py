from discord.ext import commands
from bot import BUCKET_NAME, s3
import json
import random
import time
import string

class Quotes:
    '''Commands for quotes.'''
    def __init__(self, bot):
        self.bot = bot

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
                quotes = data[serverID]['quotes']
                if quote in quotes:
                    await self.bot.say(f'Error! Quote already registered (`{quotes.index(quote)+1}`).')
                    return
                quotes.append(quote)
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
            await self.bot.say('Error! No quote number provided! Use `!allQuotes` to see the full list quotes.')
            return

        if index > len(quotes) or index <= 0:
            await self.bot.say('Error! That quote does not exist! Use `!allQuotes` to see the full list of quotes.')
            return

        if not quotes[index-1]:
            await self.bot.say('Error! That quote has been deleted.')
        else:
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
            await self.bot.say('Error! No quotes found! Use `!addQuote` to add quotes.')
            return

        # Check if int was passed & num of quotes is not greater than max allowed
        try:
            arg = int(ctx.message.content.split()[1])
        except:
            arg = 1
        if arg > MAX_QUOTES:
            await self.bot.say('**Up to ' + str(MAX_QUOTES) + ' quotes are allowed at once.**')
            arg = MAX_QUOTES

        content = ''
        for _ in range(arg):
            rng = random.randint(0, len(quotes) - 1)
            while not quotes[rng]:
                rng = random.randint(0, len(quotes) - 1)
            content += f'{quotes[rng]} `{str(rng+1):3s}`\n'
        await self.bot.say(content)

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
            if not quotes[i]:  # Don't add deleted quotes
                continue
            content += f'{str(i+1):3s} {quotes[i]}\n'
        content += '```'
        msg = await self.bot.say(content)
        react = [u"\u25C0", u"\u25B6"]
        await self.bot.add_reaction(msg, react[0])  # Back
        await self.bot.add_reaction(msg, react[1])  # Forward
        page = 0
        start = time.time()
        end = start + TIMEOUT
        while time.time() < end:
            reaction = await self.bot.wait_for_reaction(react, message=msg, timeout=int(end - time.time()))
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
                    if not quotes[i]:  # Don't add deleted quotes
                        continue
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
                    end_i = page * MAX + total % MAX
                else:
                    end_i = page * MAX + MAX
                content = f'**Active for {TIMEOUT//60} minutes.**\n```'
                for i in range(page * MAX, end_i):
                    if not quotes[i]:  # Don't add deleted quotes
                        continue
                    content += f'{str(i + 1):3s} {quotes[i]}\n'
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
            await self.bot.say('Error! Use the format: `!changeQuote quoteNumber newQuote`')
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

        if not new and not quotes[quote_num-1]:
            await self.bot.say(f'Error! That quote is already deleted. Use `!changeQuote {quote_num} "new quote"` to change this quote.')
            return

        # Ask user to confirm and perform change
        thumbs = ['👍', '👎']
        if not new:
            confirm = await self.bot.say(f'Delete:\n```{quotes[quote_num-1]}```Press {thumbs[0]} to confirm and {thumbs[1]} to abort.')
        else:
            confirm = await self.bot.say(f'Change:\n```{quotes[quote_num - 1]}\nTO\n{new}```Press {thumbs[0]} to confirm and {thumbs[1]} to abort.')

        TIMEOUT = 180
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
                if not new and quote_num == len(quotes):  # Remove last quote from the list since it won't disturb any existing quotes
                    quotes.remove(quotes[quote_num-1])
                elif not new:
                    quotes[quote_num-1] = None
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

    @commands.command(pass_context=True)
    async def searchQuote(self, ctx):
        """Search for quotes."""
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
        if content[:3] == '!sq':
            content = content[4:]
        else:
            content = content[13:]
        if content == '':
            await self.bot.say('Error! Use the format: `!searchQuote keyword1 keyword2 keyword3`')
            return
        keywords = content.split()

        results = {}

        quoteNum = 1
        total_results = 0
        total_len = 0
        for quote in quotes:
            matches = 0
            for keyword in keywords:
                if keyword.lower() in quote.lower():
                    matches += 1
            if matches == 0:
                pass
            elif matches in results:
                results[matches].append((quoteNum, quote))
                total_results += 1
                total_len += len(quote)
            else:
                results[matches] = [(quoteNum, quote)]
                total_results += 1
                total_len += len(quote)
            quoteNum += 1

        if len(results) == 0:
            await self.bot.say('No matches found!')
            return

        content = f'**{total_results} Matches Found!**\n'
        if total_len < 1500:  # Fits on one page
            for key in sorted(results.keys(), reverse=True):
                content += f'{key} keyword'
                if key == 1:
                    content += f' matched ({len(results[key])}):\n```'
                else:
                    content += f's matched ({len(results[key])}):\n```'
                for value in results[key]:
                    content += f'{str(value[0]):3s} {value[1]}\n'
                content += '```'
            await self.bot.say(content)
            return

        # Set up pages
        pages = [f'**{total_results} Matches Found!**\n']
        page = 0
        for key in sorted(results.keys(), reverse=True):
            start = f'{key} keyword'
            if key == 1:
                start += f' matched ({len(results[key])}):\n```'
            else:
                start += f's matched ({len(results[key])}):\n```'
            pages[page] += start
            for value in results[key]:
                if len(pages[page]) > 1000:  # Reached end of page
                    pages[page] += '```'
                    pages.append(start)
                    page += 1
                pages[page] += f'{str(value[0]):3s} {value[1]}\n'
            pages[page] += '```'

        # Send message and wait for reactions
        msg = await self.bot.say(pages[0])
        page = 0
        react = [u"\u25C0", u"\u25B6"]
        await self.bot.add_reaction(msg, react[0])  # Back
        await self.bot.add_reaction(msg, react[1])  # Forward
        TIMEOUT = 180
        start = time.time()
        end = start + TIMEOUT
        while time.time() < end:
            reaction = await self.bot.wait_for_reaction(react, message=msg, timeout=int(end - time.time()))
            if not reaction or reaction.user == self.bot.user:
                continue
            e = reaction.reaction.emoji
            # Back
            if e == u"\u25C0":
                if page == 0:  # Already on the first page
                    continue
                page -= 1
                await self.bot.edit_message(msg, new_content=pages[page])
                continue
            # Forward
            else:
                if page == len(pages) - 1:  # Already on last page
                    continue
                page += 1
                await self.bot.edit_message(msg, new_content=pages[page])
        content = pages[page] + '**NO LONGER ACTIVE**'
        await self.bot.edit_message(msg, new_content=content)

    @commands.command(pass_context=True)
    async def sq(self, ctx):
        """Alias for !searchQuote."""
        await self.searchQuote.invoke(ctx)

    @commands.command(pass_context=True)
    async def fillTheQuote(self, ctx):
        """Guess the missing word from the quote provided."""
        with open('data/serverData.json', 'r') as f:
            data = json.load(f)
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:
            await self.bot.say('Error! No quotes registered yet! Use `!addQuote` to add quotes.')
            return

        # Select Quote
        while True:
            quote = quotes[random.randint(0, len(quotes) - 1)]
            if quote and len(quote.split()) > 1:
                break

        # Select quote
        while True:
            quote = quotes[random.randint(0, len(quotes) - 1)]
            if quote and len(quote.split()) > 1:  # Must contain at least 2 words
                # Select word to hide
                while True:
                    words = quote.split()
                    word = words[random.randint(0, len(words) - 1)].strip(string.punctuation)
                    if len(word) >= 4:  # Must be at least 4 characters
                        break
                break

        await self.bot.say(quote + '\n' + quote.replace(word, '`_____`'))

    @commands.command(pass_context=True)
    async def fq(self, ctx):
        """Alias for !searchQuote."""
        for i in range(10):
            await self.fillTheQuote.invoke(ctx)

def setup(bot):
    bot.add_cog(Quotes(bot))
