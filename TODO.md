# Plans and ToDos

## Plugins

### tweets.py
- add reload capability
- command to post a status to a channel and/or webhook without filtering
- account-specific formats
- extend URLs, check markdown format for Discord
- handle the same Twitter account configured multiple times

### rawlogger.py
- add reload capability

### twitchdumper.py
- log or insert more data (game info, metadata)
- look for more `helix` data (tags, followers)

### twitch.py
- Check: Translating outgoing notices to messages by listening on the event
- unify twitch api calls and move them here as events
- override `IrcConnection`: whisper/notice/query translation for commands, readable chatroom names.

## other plugin ideas
- autojoin all followed channels (autopart? exceptions?)
- autoreply on certain messages with short delay and data from tags
- call webhooks or external programs on messages or events
- typical Twitch bot functionality as plugins (custom commands, moderation, loyalty points & games)

## general
- better documentation/examples
- restructure project to look more Python-esque
- some kind of testing might be nice
