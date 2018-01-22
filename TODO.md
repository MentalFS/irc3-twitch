# twitchstats.py
- *cache channel names and IDs from `ROOMSTATE`, only poll `user` endpoint when scheduled*
- *use threading instead of multiprocessing*
- better exception handling - some runtime exceptions get to `STDOUT`
- properly split APIs/endpoint into own methods/classes
- log or insert game data with `helix`/`stream` (strip url field)
- log community data with `kraken`/`stream` (strip html and url fields) or just insert the names
- log or insert `helix/streams/metadata` with `helix`/`stream` if not empty (strip empty fields)
- prepare for termination of `kraken` API in the end of 2018
- see if the helix API supports bulk retrieval of follower numbers and communities

# twitter_messages.py
- *make configuration more unambigous, like `<prefix>.account` instead of relying on the `@`*
- *make webhooks Discord-specific and format them better*
- *use more generic formatting for IRC and apply sanity checks after*
- make it possible to send tweets to a Discord only
- optionally filter tweets by keywords (probably also as exclusions)
- handle the same Twitter account configured multiple times
- reload capability
- adopt dispatcher system from feeds
- send to Discord in background thread and enable multiple Discord webhooks per Twitter account configuration
- enable channel formats per Twitter account configuration
- enable multiple Twitter accounts per configuration set

# twitch_capabilities.py
- support `RECONNECT` message
- move room list from `twitchstats.py` here and make it accessible including IDs
- translate private messages and notices to whispers or messages  <!-- hint: connection=IrcConnection -->
- option to not use membership capability (to avoid problems with large rooms)
- option to ignore `RECONNECT`
- optionally connect through websocket <!-- hint: connection=IrcConnection -->

# rawlogger.py
- catch messages like replies to `NAMES`
- optionally log raw non-channel messages to files with a configurable name
- log private messages separately to files
- add a hook system so Twitch could log whispers in separate files

# plugin ideas
- leave channel after a period of idle time (sending or receiving), except autojoin channels
- automatically join a channel when sending a message, or a dispatcher that joins the channel
- notifications/highlights in `irc3.log` or external/webhooks
- periodically log channel user data/count (maybe `NAMES` will do)
- splitting Twitch data retrieval from `twitchstats.py` to a separate base module for use in other plugins
- typical Twitch bot functionality as plugins (custom commands, moderation, loyalty, ...)
- Twitch proxy that sends every raw line to an IRC client and back (probably not going to work that way...)

# general
- add scripts for startup, shutdown and restart with multiple configs
- include a base configuration for Twitch with server, flood protection, ...
- better documentation/examples
- restructure project to document dependencies and look more Python-esque
- some kind of testing might be nice
