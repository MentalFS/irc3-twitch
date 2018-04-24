# Plans and ToDos

## Plugins

### tweets.py
- refactor configurations into classes
- add reload capability
- optionally filter tweets by keywords
- account-specific formats
- extend URLs, check markdown format for Discord
- handle the same Twitter account configured multiple times

### rawlogger.py
- add reload capability
- Log NAMES reply

### twitchdumper.py
- extract API code into classes and make them configurable
- log or insert more data (game info, communities, metadata)
- prepare for termination of `kraken` API in the end of 2018, look for more `helix` data

### twitch.py
- poll channel ID if no ROOMSTATE is sent
- unify twitch api calls and move them here as events
- special handling for chatrooms for readable names and joining
- translate private messages and notices to whispers or messages  <!-- hint: connection=IrcConnection -->
- optionally connect through websocket <!-- hint: connection=IrcConnection -->

## other plugin ideas
- periodically call NAMES (or maybe other commands)
- autoreply on certain messages with short delay and data from tags
- call webhooks or external programs on messages or events
- save relevant statistics (sub numbers, chat activity) to database (SQLITE)
- log Twitch chat and events in a readable text format that doesn't take as much space as raw IRC
- typical Twitch bot functionality as plugins (custom commands, moderation, ...)

## general
- better documentation/examples
- restructure project to look more Python-esque
- some kind of testing might be nice
