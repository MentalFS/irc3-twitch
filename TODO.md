# twitchstats.py
- cache channel names and IDs from `ROOMSTATE`, only poll `user` endpoint when scheduled
- use threading instead of multiprocessing
- properly split APIs/endpoint into own methods/classes
- stop polling useless old API endpoint `kraken`/`user`
- omit overly expressive and unneeded fields (mainly URLs) before writing
- insert game name in `helix`/`stream`
- insert user login and display name into `helix`/`stream`
- log community data (or at least insert names/display names)
- log stream metadata if applicable
- prepare for termination of `kraken` API in the end of 2018
- see if the new API supports bulk retrieval of follower numbers

# twitter_messages.py
- remove dependency to `social`
- make configuration more unambigous, like `<prefix>.account` instead of relying on the `@`
- optionally filter tweets by keywords (for chat and webhook separately)
- make it possible to send tweets to a webhook only
- reload capability
- adopt dispatcher system from feeds
- enable formats for messages and webhooks per Twitter account
- send webhooks in background thread and enable multiple webhooks per Twitter account
- enable channel/webhook specific formats and filters

# twitch_capabilities.py
- support `RECONNECT` message
- option to ignore `RECONNECT`
- a dispatcher that automatically joins the channel prior to sending
- try to make private commands work, and the ones using `NOTICE`

# rawlogger.py
- catch messages like replies to `NAMES`
- log raw non-channel messages to files with a configurable name
- log private messages separately to files with a configurable name
- add a hook system so twitch could log whispers in separate files

# new plugins
- leave channel after a period of idle time (sending or receiving), except autojoin channels
- notifications/highlights in `irc3.log` or external/webhooks
- periodically log channel user data: user count, maybe list, numbers per prefix (maybe `NAMES` will do)

# general
- *add `LICENCE` and `README`*
- *rename to `irc3_plugins`, subfolder for plugins: `plugins`*
- *put Twitch plugins into own package, rename `twitter_messages` to `tweets`, rename `twitch_stats` `twitch/apilogger`*
- add scripts for startup, shutdown and restart
- better documentation/examples
- restructure project to document dependencies and look more Python-esque
- some kind of testing might be nice
