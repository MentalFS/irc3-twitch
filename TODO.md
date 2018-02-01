# twitchlogger.py
- *cache channel names and IDs from `ROOMSTATE`, only poll `user` endpoint when scheduled*
- *use ThreadPoolExecutor instead of multiprocessing*
- log or insert game data with `helix`/`stream` (strip url field)
- log community data with `kraken`/`stream` (strip html and url fields) or just insert the names
- log or insert `helix/streams/metadata` with `helix`/`stream` if not empty (strip empty fields)
- prepare for termination of `kraken` API in the end of 2018
- see if the helix API supports bulk retrieval of follower numbers and communities

# tweets.py
- clean up the non-OO mess (it grew with time, honestly)
- reload capability
- optionally filter tweets by keywords (probably also as exclusions)
- account-specific formats
- extend URLs, check markdown syntax for Discord
- handle the same Twitter account configured multiple times
- adopt dispatcher system from feeds

# twitch.py
- support `RECONNECT` message
- option to not use membership capability (to avoid problems with large rooms)
- add file handler for rawlogger that logs whispers in separate files
- add a dispatcher that joins the channel
- translate private messages and notices to whispers or messages  <!-- hint: connection=IrcConnection -->
- option to specify handler for `RECONNECT`
- move room list from `twitchlogger.py` here and make it accessible including IDs
- optionally connect through websocket <!-- hint: connection=IrcConnection -->

# rawlogger.py
- catch messages like replies to `NAMES`
- optionally log raw non-channel messages to files with a configurable name
- log private messages separately to files

# plugin ideas
- leave channel after a period of idle time (sending or receiving), except autojoin channels
- split Twitch data retrieval from `twitchlogger.py` to a separate base module for use in other plugins
- call webhooks or external programs on messages or Twitch events
- typical Twitch bot functionality as plugins (custom commands, moderation, ...)
- ~~Twitch proxy that sends every raw line to an IRC client and back~~ (probably not going to work that way...)

# general
- better documentation/examples
- restructure project to look more Python-esque
- some kind of testing might be nice
