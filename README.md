# ScottBot
ScottBot is a bot made for discord servers using python, sqlite, AWS S3, and JSON. It is hosted through Heroku using their automatic GitHub deployment integration (That's why there are so many commits).

To add ScottBot to your server click the following link:
https://discordapp.com/oauth2/authorize?client_id=465969556633026604&scope=bot

Please note many commands require administrative permissions.

**ScottBot Version: 2.5**

Commands:

  * !help - Shows all ScottBot commands and descriptions.

  * !allowRoles - Enables/Disables role(s) to be used with !role.
  
  * !roles - Adds/Removes user to an allowed role.
  
  * !allowStreamPing - Allows ScottBot to send an alert when someone starts streaming on twitch. Optinally it can alert a specific role.
  
  * !clear - Deletes all commands sent and all messages from ScottBot in a text channel.
  
  * !flake - Increments the flake count for all users mentioned.
  
  * !flakeRank - Displays the flake standings.
  
  * flakeReset - Resets the flakeRank.
  
  * !resetData - Permanently resets all ScottBot related data for the server.

  * !request - Sends a request for a feature you would like added to ScottBot.

  * !addQuote - Adds a quote to the list of quotes.
  
  * !quote - ScottBot says a random quote from the list of quotes.
  
  * !poll - Creates a poll using reactions. Used with the following format (Minimum of 2 choices, maximum of 9 choices): !poll "Question" "Choice" "Choice"
  
  * !version - Displays ScottBot Version.
  
  * !hello ScottBot greets you.
