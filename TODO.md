# twitchdumper.py
- split stream info/viewer numbers, adjust dupe check for length
- *use ThreadPoolExecutor instead of multiprocessing*
- *cache channel names and IDs from `ROOMSTATE`, only poll `user` endpoint when scheduled*
- log or insert more data (game info, communities, metadata)
- prepare for termination of `kraken` API in the end of 2018, look for more `helix` data

# rawlogger.py
- add reload capability (for filters)

# tweets.py
- clean up the code, add reload capability
- optionally filter tweets by keywords
- account-specific formats
- extend URLs, check markdown format for Discord
- handle the same Twitter account configured multiple times

# twitch.py
- move room list from twitchdumper.py here and make it accessible including IDs
- special handling for chatrooms for readable names and joining
- translate private messages and notices to whispers or messages  <!-- hint: connection=IrcConnection -->
- optionally connect through websocket <!-- hint: connection=IrcConnection -->

# new plugin: twitchstatistics.py
- create plugin that saves relevant statistics to database-like files (tab separated files or SQLite)
- add IRC statistics: number of messages, distinct chatters, nummber of bans/timeouts, subs/other notices
- track subscription numbers
- create emote statistics
- create stats per stream and per minute, maybe day/month

# new plugin: twitchlogger.py
- create plugin as an extension/copy of the original logger.py
- write USERNOTICE and CLEARCHAT messages at least
- enable configuration with channelname
- create helper script to convert raw logs to text logs

# other plugin ideas
- autoreply on certain messages with short delay and data from tags
- call webhooks or external programs on messages or Twitch events
- typical Twitch bot functionality as plugins (custom commands, moderation, ...)

# general
- better documentation/examples
- restructure project to look more Python-esque
- some kind of testing might be nice
