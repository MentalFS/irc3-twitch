# twitchdumper.py
- *use ThreadPoolExecutor instead of multiprocessing*
- *cache channel names and IDs from `ROOMSTATE`, only poll `user` endpoint when scheduled*
- *Remove error messages from out.log*
- log or insert game data with `helix`/`stream` (strip url field)
- log community data with `kraken`/`stream` (strip html and url fields) or just insert the names
- log or insert `helix/streams/metadata` with `helix`/`stream` if not empty (strip empty fields)
- prepare for termination of `kraken` API in the end of 2018, look for more `helix` data

# rawlogger.py
- optional explicit channel list for logging

# twitchlogger.py
- create plugin as an extension/copy of the original `logger.py`
- write USERNOTICE and CLEARCHAT messages at least
- enable configuration with channelname
- create helper script to convert raw logs to text logs

# twitchstats.py
- create plugin that saves relevant statistics to database-like files (tab separated files or SQLite)
- create helper script to convert/import json dump files
- add IRC statistics: number of messages, distinct chatters, nummber of bans/timeouts, subs/other notices
- track subscription numbers
- create emote statistics
- create stats per stream and per minute

# tweets.py
- clean up the code, add reload capability
- optionally filter tweets by keywords (probably also as exclusions)
- account-specific formats
- extend URLs, check markdown syntax for Discord
- handle the same Twitter account configured multiple times

# twitch.py
- move room list from `twitchdumper.py` here and make it accessible including IDs
- move json polling from `twitchdumper.py` here and create events for plugins for every poll with change indicator
- translate private messages and notices to whispers or messages  <!-- hint: connection=IrcConnection -->
- optionally connect through websocket <!-- hint: connection=IrcConnection -->

# general
- better documentation/examples
- restructure project to look more Python-esque
- some kind of testing might be nice

# plugin ideas
- special handling for chatrooms, maybe autojoin
- split Twitch data retrieval from `twitchlogger.py` to a separate base module for use in other plugins
- call webhooks or external programs on messages or Twitch events
- typical Twitch bot functionality as plugins (custom commands, moderation, ...)
- ~~Twitch proxy that sends every raw line to an IRC client and back~~ (probably not going to work that way...)
