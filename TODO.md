# twitchstats.py
- *cache channel names and IDs from `ROOMSTATE`, only poll `user` endpoint when scheduled*
- *use threading instead of multiprocessing*
- *properly split APIs/endpoint into own methods/classes*
- log game name/data with `helix`/`stream`
- log community names/display names with `kraken`/`stream` (at least strip html fields)
- log `helix/streams/metadata` with `helix`/`stream` if not empty
- prepare for termination of `kraken` API in the end of 2018
- see if the helix API supports bulk retrieval of follower numbers and communities

# twitter_messages.py
- *make configuration more unambigous, like `<prefix>.account` instead of relying on the `@`*
- make it possible to send tweets to a webhook only
- optionally filter tweets by keywords (probably also as exclusions)
- handle the same Twitter account configured multiple times
- reload capability
- adopt dispatcher system from feeds
- send webhooks in background thread and enable multiple webhooks per Twitter account configuration
- enable formats for messages and webhooks per Twitter account configuration
- enable multiple Twitter accounts per configuration set

# twitch_capabilities.py
- support `RECONNECT` message
- option to ignore `RECONNECT`
- try to make private commands work, and the ones using `NOTICE` <!-- hint: connection=IrcConnection -->
- a dispatcher that automatically joins the channel prior to sending

# rawlogger.py
- catch messages like replies to `NAMES`
- log raw non-channel messages to files with a configurable name
- log private messages separately to files with a configurable name
- add a hook system so Twitch could log whispers in separate files

# new plugins
- leave channel after a period of idle time (sending or receiving), except autojoin channels
- notifications/highlights in `irc3.log` or external/webhooks
- periodically log channel user data/count (maybe `NAMES` will do)

# general
- *add `LICENCE` and `README`*
- *rename to `irc3_plugins`, subfolder for plugins: `plugins`*
- *put Twitch plugins into own package, rename `twitter_messages` to `tweets`, rename `twitch_stats` `twitch/apilogger`*
- add scripts for startup, shutdown and restart
- include a base configuration for Twitch with server, flood protection, ...
- better documentation/examples
- restructure project to document dependencies and look more Python-esque
- some kind of testing might be nice
