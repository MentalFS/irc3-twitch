# twitchstats.py
- cache channel names and IDs from tags, only poll `user` endpoint when scheduled
- stop polling useless old API endpoint `kraken`/`user`
- omit overly expressive and unneeded fields (mainly URLs) before writing
- insert game name in `helix`/`stream`
- insert user login into `helix`/`stream`
- log community data (or at least insert names)
- configuration of file names and formats per endpoint
- configuration of polling times per endpoint
- see if the new API supports bulk retrieval of follower numbers
- prepare for termination of `kraken` API in the end of 2018
- consider logging stream metadata
- consider using threading instead of multiprocessing

# twitter_messages.py
- reload capability
- better webhook handling: multiple formats, pre-defined formats, multiple webhooks per twitter
- send webhooks in background thread
- rebuild for more flexibility
- consider adopting dispatcher and hook system from feeds
- consider using the storage module
- consider removing dependency to social module
- consider different library for twitter

# twitch_capabilities.py
- support `RECONNECT` message
- option to ignore `RECONNECT`

# rawlogger.py
- catch messages like replies to `NAMES`
- log raw non-channel messages to files with a configurable name
- log private messages separately to files with a configurable name

# new plugins
- notifications/highlights in `irc3.log`
- periodically log channel user data: user count, maybe list, numbers per prefix (or just issue `NAMES` and let logger take care)
- automatically join channels a message is sent to by the bot (or make a dispatcher that does that)
- leave channel after a period of idling (except autojoin channels)
- probably externalize the channel list to a new module
- external notifications/highlights with webhooks

# general
- *LICENCE*
- *README*
- *find better names for some files - and the project*
- rename to `irc3_plugins`, subfolder for plugins: `plugins`
- put Twitch stuff into own package, rename `twitter_messages` to `tweets`, rename `twitch_stats` `twitch/apilogger`
- check config stuff (only base name)
- *make folders for plugins, bin, inis*
- consider adding scripts for searching logs
- restructure project to document dependencies and look more Python-esque
- better documentation / examples
- some kind of testing might be nice
- see if Twitch is moving further away from IRC and maybe ditch it too
