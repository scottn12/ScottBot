# ScottBot by github.com/scottn12
# quotes.py
# Contains all commands related to ScottBot's quote functionality.

from discord.ext import commands
from bot import BUCKET_NAME, s3
import json
import random
import time
import re

class Quotes:
    """Commands for quotes."""
    def __init__(self, bot):
        self.bot = bot
        with open('data/quotes.json', 'r') as f:
            self.cacheJSON = json.load(f)

    @commands.command(pass_context=True, description='You may not mention a user in a quote.')
    async def addQuote(self, ctx):
        """Adds a quote to the list of quotes."""
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

        data = self.cacheJSON

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

        self.writeJSON('quotes.json')

        await self.bot.say(f'Quote **{total}** added!')

    @commands.command(pass_context=True)
    async def aq(self, ctx):
        """Alias for !addQuote."""
        await self.addQuote.invoke(ctx)

    @commands.command(pass_context=True)
    async def quote(self, ctx):
        """Display the quote at the given index."""
        data = self.cacheJSON
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:
            await self.bot.say('Error! No quotes found! Use `!addQuote` to add quotes.')
            return

        # Find/Write Quotes
        indexes = ctx.message.content.split()[1:]
        content = ''
        for index in indexes:
            try:
                index = int(index)
            except ValueError:
                continue  # Ignore non-numbers (kevin)
            if index > len(quotes) or index <= 0:
                content += f'Error! Quote {index} does not exist! Use `!allQuotes` to see the full list of quotes.\n'
                continue
            if not quotes[index-1]:
                content += f'Error! Quote `{index}` has been deleted.\n'
            else:
                content += f'{quotes[index-1]} `{index}`\n'
        if not content:
            await self.bot.say('Error! No quote number provided! Use `!allQuotes` to see the full list quotes.')
        else:
            await self.bot.say(content)

    @commands.command(pass_context=True)
    async def q(self, ctx):
        """Alias for !quote."""
        await self.quote.invoke(ctx)

    @commands.command(pass_context=True)
    async def randomQuote(self, ctx):
        """ScottBot says a random quote."""
        MAX_QUOTES = 5
        data = self.cacheJSON

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
        data = self.cacheJSON
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes']
        else:
            await self.bot.say('Error! No quotes found! Use !addQuote to add quotes.')
            return
        MAX_CHARS = 1500
        total = len(quotes)
        tempQuotes = [i for i in quotes if i]  # Get copy of quotes with no None values
        string = '\n'.join(tempQuotes)
        total_len = len(string) + 4*total  # 4 characters to account for quote number

        # All quotes can fit on one  page
        content = '```'
        if total_len <= MAX_CHARS:
            for i in range(total):
                if not quotes[i]:  # Don't add deleted quotes
                    continue
                content += f'{str(i+1):3s} {quotes[i]}\n'
            content += '```'
            await self.bot.say(content)
            return

        # Set up pages
        page = 0
        MAX_CHARS = 1000
        TIMEOUT = 180
        start = f'**Active for {TIMEOUT//60} minutes.**\n```'
        pages = [start]
        for i in range(total):
            if not quotes[i]:  # Don't add deleted quotes
                continue
            if len(pages[page]) + len(quotes[i])+4 > MAX_CHARS:  # End of page
                pages[page] += '```'
                pages.append(start)
                page += 1
            pages[page] += f'{str(i+1):3s} {quotes[i]}\n'
        pages[page] += '```'

        # Send and wait for reactions
        msg = await self.bot.say(pages[0])
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
                await self.bot.edit_message(msg, new_content=pages[page])
                continue
            # Forward
            else:
                if page == len(pages) - 1:  # Already on last page
                    continue
                page += 1
                await self.bot.edit_message(msg, new_content=pages[page])
        content = msg.content.replace(f'Active for {TIMEOUT//60} minutes.', 'NO LONGER ACTIVE') + '**NO LONGER ACTIVE**'
        await self.bot.edit_message(msg, new_content=content)

    @commands.command(pass_context=True)
    async def allq(self, ctx):
        """Alias for !allQuotes."""
        await self.allQuotes.invoke(ctx)

    @commands.command(pass_context=True, description='!changeQuote quoteNumber newQuote (Delete if no newQuote is provided)')
    @commands.has_permissions(administrator=True)
    async def changeQuote(self, ctx):
        """Change or delete a given quote (ADMIN)."""
        data = self.cacheJSON
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
                self.writeJSON('quotes.json')
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

    @commands.command(pass_context=True, description='!searchQuote keyword1 keyword2 keyword3')
    async def searchQuote(self, ctx):
        """Search for quotes."""
        data = self.cacheJSON
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
        MAX_CHARS = 1500
        for quote in quotes:
            if not quote:
                continue
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
        if total_len < MAX_CHARS:  # Fits on one page
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
        MAX_CHARS = 1000
        for key in sorted(results.keys(), reverse=True):
            start = f'{key} keyword'
            if key == 1:
                start += f' matched ({len(results[key])}):\n```'
            else:
                start += f's matched ({len(results[key])}):\n```'
            pages[page] += start
            for value in results[key]:
                if len(pages[page]) + len(value[1])+4 > MAX_CHARS:  # End of page
                    pages[page] += '```'
                    pages.append('```')
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
    async def matchQuote(self, ctx):
        """Guess the missing word from the quote provided."""
        data = self.cacheJSON
        serverID = ctx.message.server.id
        if serverID in data and 'quotes' in data[serverID] and data[serverID]['quotes']:  # Check if server/quotes are registered
            quotes = data[serverID]['quotes'].copy()
        else:
            await self.bot.say('Error! No quotes registered yet! Use `!addQuote` to add quotes.')
            return

        # Try to find quote that works until you run out of quotes
        eligible = []
        newQuote = ''
        rng = -1
        while quotes:
            rng = random.randint(0, len(quotes) - 1)
            quote = quotes[rng]
            if not quote or len(quote.split()) < 2:  # Deleted quote or only one word
                quotes.remove(quote)
                continue
            newQuote = re.sub('(?<!_)_(?!_)', '*', quote)  # Replace single '_' with '*'
            # Find eligible words to hide
            eligible = []  # Reset list for new quote
            words = newQuote.split()
            for word in words:
                word = word.strip('!“”"#$%&\'()+,-./:;<=>?@[\\]^{|}')  # Remove all non-markdown punctuation
                cleanWord = word.strip('*_~`')  # Remove all markdown punctuation
                if len(cleanWord) >= 4 and newQuote.count(cleanWord) == 1:  # Must be at least 4 characters and occur once
                    eligible.append((word,cleanWord))
            if eligible:  # Eligible quote found
                break
            else:  # Don't try this quote again
                quotes.remove(quote)
        if eligible:
            word, cleanWord = eligible[random.randint(0, len(eligible) - 1)]
        else:  # No eligible quotes found
            await self.bot.say('Error! No eligible quotes found. Use `!addQuote` to add quotes.')
            return

        # Deal with discord markdown characters
        start = ''
        end = ''
        if word != cleanWord:
            start = word[:word.index(cleanWord[0])]
            end = word[len(cleanWord) + len(start):]

        # Prompt user and get response
        TIMEOUT = 10
        blank_quote = newQuote.replace(word, start + '`_____`' + end)
        await self.bot.say(f'**Respond with the missing word in {TIMEOUT} seconds!** ({ctx.message.author.mention})\n{blank_quote}')
        answer = await self.bot.wait_for_message(timeout=TIMEOUT, author=ctx.message.author)
        filled = blank_quote.replace('`_____`', '`'+cleanWord+'`')
        msg = ''
        win = False
        if answer and answer.content.lower() == cleanWord.lower():
            msg += '**Correct, you win!**'
            win = True
        elif answer:
            msg += '**Wrong, you lose!**'
        else:
            msg += '**Time\'s up, you lose!**'
        msg += f'\n{filled} `{rng+1}`'

        # Update score
        wins = 0
        losses = 1
        if win:
            wins = 1
            losses = 0
        userID = ctx.message.author.id
        if 'matchScores' in data[serverID]:  # Check if matchScores are registered yet
            scores = data[serverID]['matchScores']
            if userID in scores:  # User already registered
                if win:
                    scores[userID]['wins'] += 1
                else:
                    scores[userID]['losses'] += 1
                wins = scores[userID]['wins']
                losses = scores[userID]['losses']
            else:
                scores[userID] = {
                    "wins": wins,
                    "losses": losses
                }
        else:  # add matchScores field
            data[serverID]['matchScores'] = {
                userID: {
                    "wins": wins,
                    "losses": losses
                }
            }
        winRate = round(wins/(wins+losses)*100)
        msg += f'\nWins: {wins} Losses: {losses} (**{winRate}%**)'
        await self.bot.say(msg)

        self.writeJSON('quotes.json')

    @commands.command(pass_context=True)
    async def mq(self, ctx):
        """Alias for !matchQuote."""
        await self.matchQuote.invoke(ctx)

    @commands.command(pass_context=True)
    async def quoteScoreboard(self, ctx):
        """Displays the quote scoreboard."""
        data = self.cacheJSON
        serverID = ctx.message.server.id
        if serverID in data and 'matchScores' in data[serverID] and data[serverID]['matchScores']:  # Check if scores are registered
            scores = data[serverID]['matchScores']
        else:
            await self.bot.say('Error! No scores recorded yet! Use `!matchQuote` to play.')
            return

        # Sort scores
        sortedIDs = []
        winRates = []
        for score in scores.keys():
            wins = scores[score]['wins']
            losses = scores[score]['losses']
            winRate = round(wins/(wins+losses)*100)
            if not winRates:
                winRates.append(winRate)
                sortedIDs.append(score)
                continue
            for i in range(len(winRates)):
                iWinRate = winRates[i]
                iWins = scores[sortedIDs[i]]['wins']
                if winRate > iWinRate:
                    winRates.insert(i, winRate)
                    sortedIDs.insert(i, score)
                    break
                if winRate == iWinRate:  # WinRate Tie
                    if wins > iWins:
                        winRates.insert(i, winRate)
                        sortedIDs.insert(i, score)
                        break
                if i == len(winRates) - 1:
                    winRates.append(winRate)
                    sortedIDs.append(score)

        # Display
        msg = f'```{"Player:":15s}\tWin Rate:\tWins:\tLosses:\n'
        for score in sortedIDs:
            user = await self.bot.get_user_info(score)
            wins = scores[score]['wins']
            losses = scores[score]['losses']
            msg += f'{str(user.name):15s}\t'
            msg += f'{str(round(wins/(wins+losses)*100)) + "%":5s}\t\t'
            msg += f'{str(wins):5s}\t'
            msg += f'{str(losses):5s}\n'
        msg += '```'
        await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def qs(self, ctx):
        """Alias for !quoteScoreboard."""
        await self.quoteScoreboard.invoke(ctx)

    # Update file with cached JSON and upload to AWS
    def writeJSON(self, filename):
        with open(f'data/{filename}', 'w') as f:  # Update JSON
            json.dump(self.cacheJSON, f, indent=2)
        s3.upload_file(f'data/{filename}', BUCKET_NAME, filename)

def setup(bot):
    bot.add_cog(Quotes(bot))
